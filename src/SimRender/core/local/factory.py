from typing import Optional, List, Dict, Any
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from multiprocessing.shared_memory import SharedMemory
from time import sleep
from numpy import array, ndarray, nan

from SimRender.core.local.memory import Memory
from SimRender.core.utils import flat_mesh_cells


class Factory:

    def __init__(self, sync: bool):
        """
        This class is used to manage the communication with the visualization process.
        It creates and update the visualization data in shared memories.

        :param sync: If True, the update call is synchronized with the end of the remote rendering step.
        """

        # Create the shared memories container
        self.memories: List[Memory] = []

        # Create the visual object API
        self.objects = Objects(factory=self)

        # Local and remote socket to communicate between processes
        self.__socket = socket(AF_INET, SOCK_STREAM)
        self.__socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.__remote: Optional[socket] = None

        # Define the synchronization function if required, otherwise add a manual delay (minimal synchronization)
        self.__sync_fct = self.__sync if sync else lambda: sleep(0.002)
        # Create a shared numpy array for synchronization with format [do_exit, do_synchronize, step_counter]
        sync_array = array([0, 0, 0], dtype=int)
        self.__sync_sm = SharedMemory(create=True, size=sync_array.nbytes)
        self.__sync_arr = ndarray(shape=sync_array.shape, dtype=sync_array.dtype, buffer=self.__sync_sm.buf)
        self.__sync_arr[...] = sync_array[...]

    @property
    def is_open(self) -> bool:
        return self.__sync_arr[0] == 0

    def init(self, batch_key: Optional[int]) -> int:
        """
        Initialize the local socket.

        :return: Available port number of the socket.
        """

        # Case 1: Non-batch mode, get an available socket port
        if batch_key is None:
            self.__socket.bind(('localhost', 0))
        # Case 2: Batch mode, bind to the defined key
        else:
            # Disable sync for batch mode
            if self.__sync_fct == self.__sync:
                self.__sync_fct = lambda: sleep(0.002)
                print('Warning: Synchronization is not available for Viewer in batch mode '
                      '(automatically turned "sync" parameter to False)')
            self.__socket.bind(('localhost', batch_key))
        return self.__socket.getsockname()[1]

    def connect(self) -> None:
        """
        Connect to the remote process and communicate each shared memory information.
        """

        # Connect to the remote socket
        self.__socket.listen()
        self.__remote, _ = self.__socket.accept()

        # Send information about the sync shared array
        sm_name = self.__sync_sm.name.encode(encoding='utf-8')
        self.__remote.send(len(sm_name).to_bytes(length=2, byteorder='big'))
        self.__remote.send(sm_name)

        # Send the number of visual objects, then information about each visual object shared arrays
        self.__remote.send(len(self.memories).to_bytes(length=2, byteorder='big'))
        for memory in self.memories:
            memory.connect(remote=self.__remote)

        # Wait for the remote viewer to create all visual objects
        self.__remote.recv(4)

    def update(self) -> None:
        """
        Trigger a render call in the remote process.
        """

        # Increment the shared step counter to trigger the remote render
        self.__sync_arr[2] += 1

        # If defined, call the synchronization function
        self.__sync_fct()

    def __sync(self):
        """
        Synchronization with the remote process.
        """

        # Turn the 'do_synchronize' shared flag on
        self.__sync_arr[1] = 1

        # Wait for the remote process to be done (after several tests, it appears to be the faster way)
        a = self.__remote.recv(4)

        # Turn the 'do_synchronize' shared flag off
        self.__sync_arr[1] = 0

    def close(self) -> None:
        """
        Close the communication with the visualization process.
        """

        # Turn the 'do_exit' shared flag on
        self.__sync_arr[0] = 1

        # Wait for the visualization process to close connections with the shared memories
        self.__remote.recv(4)

        # Close the connection with the shared memories (synchronization array and each visual object array)
        self.__sync_sm.close()
        self.__sync_sm.unlink()
        for memory in self.memories:
            memory.close()

        # Close local and remote sockets
        self.__remote.send(b'done')
        self.__socket.close()


class Objects:

    def __init__(self, factory: Factory):
        """
        This class gathers the methods to create and update visual objects.

        :param factory: Factory that handles the objects.
        """

        # Keep the Factory as a private attribute so that it is not accessible for users
        self.__factory = factory

        # Store objects types to check the update methods calls
        self.__types: List[str] = []

    def __add_object(self, object_type: str, data: Dict[str, Any]) -> int:
        """
        Joint method to create a visual object.

        :param object_type: Object type (mesh, points...).
        :param data: Object data (positions, color...).
        :return: ID of the visual object in the viewer.
        """

        # The call to locals() in the add_ methods also includes the 'self' key
        del data['self']

        # Create a new memory for the visual object
        self.__factory.memories.append(Memory(object_type=object_type, data=data))

        # Store the type of the visual object
        self.__types.append(object_type)

        # Return the visual object ID
        return len(self.__types) - 1

    def __update_object(self, object_type: str, data: Dict[str, Any]) -> None:
        """
        Joint method to update a visual object.

        :param object_type: Object type (mesh, points...).
        :param data: Object data (positions, color...).
        """

        # The call to locals() in the update_ methods also includes 'self' and 'object_id' keys
        del data['self']
        object_id = data.pop('object_id')

        # Check that the update_ method is called for the good visual object type
        self.__check_id(object_id=object_id, object_type=object_type)

        # Update the data fields in the shared memories
        self.__factory.memories[object_id].update(data=data)

    def __check_id(self, object_id: int, object_type: str) -> None:
        """
        Check that the visual object is called with the right method.

        :param object_id: ID of the visual object.
        :param object_type: Object type (mesh, points...).
        """

        if object_type != self.__types[object_id]:
            raise ValueError(f"The object with ID={object_id} is type '{self.__types[object_id]}'."
                             f"Call update_{self.__types[object_id]}() instead of update_{object_type}().")

    def add_mesh(self,
                 positions: ndarray,
                 cells: List[int],
                 color: str = 'green',
                 alpha: float = 1.,
                 wireframe: bool = False,
                 line_width: float = 1.,
                 colormap: str = 'jet',
                 colormap_field: ndarray = array(nan),
                 colormap_range: ndarray = array(nan),
                 texture_name: str = '',
                 texture_coords: ndarray = array(nan)) -> int:
        """
        Add a new mesh in the viewer.

        :param positions: Positions of the mesh.
        :param cells: Faces of the mesh.
        :param color: Color of the mesh.
        :param alpha: Opacity of the mesh.
        :param wireframe: If True, the mesh has a wireframe representation.
        :param line_width: Width of the mesh edges.
        :param colormap: Color map scheme name.
        :param colormap_field: Scalar values to color the mesh regarding the colormap.
        :param colormap_range: Range of the color map.
        :param texture_name: Name of the texture file.
        :param texture_coords: Texture coordinates.
        :return: ID of the object in the viewer.
        """

        try:
            cells = array(cells)
        except ValueError:
            cells = flat_mesh_cells(cells=cells)
        return self.__add_object(object_type='mesh', data=locals())

    def update_mesh(self,
                    object_id: int,
                    positions: Optional[ndarray] = None,
                    color: Optional[str] = None,
                    alpha: Optional[float] = None,
                    wireframe: Optional[bool] = None,
                    line_width: Optional[float] = None,
                    colormap_field: Optional[ndarray] = None) -> None:
        """
        Update an existing mesh in the viewer.

        :param object_id: ID of the object as returned when created.
        :param positions: Positions of the mesh.
        :param color: Color of the mesh.
        :param alpha: Opacity of the mesh.
        :param wireframe: If True, the mesh has a wireframe representation.
        :param line_width: Width of the mesh edges.
        :param colormap_field: Scalar values to color the mesh regarding the colormap.
        """

        self.__update_object(object_type='mesh', data=locals())

    def add_points(self,
                   positions: ndarray,
                   color: str = 'green',
                   alpha: float = 1.,
                   point_size: int = 4,
                   colormap: str = 'jet',
                   colormap_field: ndarray = array(nan),
                   colormap_range: ndarray = array(nan)) -> int:
        """
        Add a new point cloud in the viewer.

        :param positions: Positions of the point cloud.
        :param color: Color of the point cloud.
        :param alpha: Opacity of the point cloud.
        :param point_size: Size of points.
        :param colormap: Color map scheme name.
        :param colormap_field: Scalar values to color the point cloud regarding the colormap.
        :param colormap_range: Range of the color map.
        :return: ID of the object in the viewer.
        """

        return self.__add_object(object_type='points', data=locals())

    def update_points(self,
                      object_id: int,
                      positions: Optional[ndarray] = None,
                      color: Optional[str] = None,
                      alpha: Optional[float] = None,
                      point_size: Optional[float] = None,
                      colormap_field: Optional[ndarray] = None) -> None:
        """
        Update an existing point cloud in the viewer.

        :param object_id: ID of the object as returned when created.
        :param positions: Positions of the point cloud.
        :param color: Color of the point cloud.
        :param alpha: Opacity of the point cloud.
        :param point_size: Size of points.
        :param colormap_field: Scalar values to color the point cloud regarding the colormap.
        """

        self.__update_object(object_type='points', data=locals())

    def add_arrows(self,
                   positions: ndarray,
                   vectors: ndarray,
                   color: str = 'green',
                   alpha: float = 1.,
                   colormap: str = 'jet',
                   colormap_field: ndarray = array(nan),
                   colormap_range: ndarray = array(nan)) -> int:
        """
        Add a new point cloud in the viewer.

        :param positions: Positions of the arrows bases.
        :param vectors: Vectors of the arrows.
        :param color: Color of the arrows.
        :param alpha: Opacity of the arrows.
        :param colormap: Color map scheme name.
        :param colormap_field: Scalar values to color the point cloud regarding the colormap.
        :param colormap_range: Range of the color map.
        :return: ID of the object in the viewer.
        """

        return self.__add_object(object_type='arrows', data=locals())

    def update_arrows(self,
                      object_id: int,
                      positions: Optional[ndarray] = None,
                      vectors: Optional[ndarray] = None,
                      color: Optional[str] = None,
                      alpha: Optional[float] = None,
                      colormap_field: Optional[ndarray] = None) -> None:
        """
        Update an existing point cloud in the viewer.

        :param object_id: ID of the object as returned when created.
        :param positions: Positions of the point cloud.
        :param vectors: Vectors of the arrows.
        :param color: Color of the point cloud.
        :param alpha: Opacity of the point cloud.
        :param colormap_field: Scalar values to color the point cloud regarding the colormap.
        """

        self.__update_object(object_type='arrows', data=locals())

    def add_lines(self,
                  start_positions: ndarray,
                  end_positions: ndarray,
                  color: str = 'green',
                  alpha: float = 1.,
                  line_width: float = 1.) -> int:
        """
        Add line segments to the viewer.

        :param start_positions: Start position of each line segment.
        :param end_positions: End position of each line segment.
        :param color: Color of the lines.
        :param alpha: Opacity of the lines.
        :param line_width: Width of the lines.
        :return: ID of the object in the viewer.
        """

        return self.__add_object(object_type='lines', data=locals())

    def update_lines(self,
                     object_id: int,
                     start_positions: Optional[ndarray] = None,
                     end_positions: Optional[ndarray] = None,
                     color: Optional[str] = None,
                     alpha: Optional[float] = None,
                     line_width: Optional[float] = None) -> None:
        """
        Update existing line segments in the viewer.

        :param object_id: ID of the object as returned when created.
        :param start_positions: Start position of each line segment.
        :param end_positions: End position of each line segment.
        :param color: Color of the lines.
        :param alpha: Opacity of the lines.
        :param line_width: Width of the lines.
        """

        self.__update_object(object_type='lines', data=locals())

    def add_text(self,
                 content: str,
                 corner: str = 'BR',
                 color: str = 'black',
                 font: str = '',
                 size: int = 1,
                 bold: bool = False,
                 italic: bool = False) -> int:
        """
        Add 2D text in the viewer.

        :param content: Text content (max 100 car.).
        :param corner: Vertical (Top, Middle, Bottom) and horizontal (Left, Middle, Right) positions of the Text - for
                       instance, 'BR' stands for 'bottom-right'.
        :param color: Text color.
        :param font: Text font name.
        :param size: Text size.
        :param bold: If True, apply bold style to the text.
        :param italic: If True, apply italic style to the text.
        :return: ID of the object in the viewer.
        """

        content = array(content, dtype='<U100')
        return self.__add_object(object_type='text', data=locals())

    def update_text(self,
                    object_id: int,
                    content: str,
                    color: str = 'black',
                    bold: bool = False,
                    italic: bool = False) -> None:
        """
        Update an existing text in the viewer.

        :param object_id: ID of the object as returned when created.
        :param content: Text content (max 100 car.).
        :param color: Text color.
        :param bold: If True, apply bold style to the text.
        :param italic: If True, apply italic style to the text.
        """

        content = array(content, dtype='<U100')
        self.__update_object(object_type='text', data=locals())
