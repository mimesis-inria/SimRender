from typing import Optional, List
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
from multiprocessing.shared_memory import SharedMemory
from time import sleep
from numpy import array, ndarray, isnan
from vedo import Plotter, Mesh, Points, Arrows, Lines, Text2D
from matplotlib.colors import Normalize
from matplotlib.pyplot import get_cmap

from SimRender.core.remote.memory import Memory
from SimRender.core.utils import fix_memory_leak, get_mesh_cells


class Factory:

    def __init__(self, socket_port: int, plotter: Plotter, store_data: bool = False):
        """
        This class is used to manage the communication with the simulation process.
        It loads the visualization data from shared arrays.

        :param socket_port: Port number of the simulation socket.
        :param plotter: Plotter instance.
        """

        # CPython issue: https://github.com/python/cpython/issues/82300
        fix_memory_leak()

        # Connect to the simulation process (possibly wait for the server to bind to the defined address)
        self.__socket = socket(AF_INET, SOCK_STREAM)
        self.__socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        connected = False
        while not connected:
            try:
                self.__socket.connect(('localhost', socket_port))
                connected = True
            except ConnectionRefusedError:
                pass

        # Load the shared numpy array for synchronization with format [do_exit, do_synchronize, step_counter]
        sync_array = array([0, 0, 0], dtype=int)
        sm_name = self.__socket.recv(int.from_bytes(bytes=self.__socket.recv(2), byteorder='big')).decode('utf-8')
        self.__sync_sm = SharedMemory(create=False, name=sm_name)
        self.__sync_arr = ndarray(shape=sync_array.shape, dtype=sync_array.dtype, buffer=self.__sync_sm.buf)

        # Create the visual objects and the associated memories containers
        self.__objects: List[Object] = []
        self.__memories: List[Memory] = []

        # Receive the number of visual objects, then information about each visual object shared array
        nb_object = int.from_bytes(bytes=self.__socket.recv(2), byteorder='big')
        for _ in range(nb_object):

            # Receive the object type
            object_type = self.__socket.recv(int.from_bytes(bytes=self.__socket.recv(2),
                                                            byteorder='big')).decode(encoding='utf-8')

            # Receive data shared arrays in memory
            memory = Memory(remote=self.__socket, store_data=store_data)

            # Create the visual object
            self.__objects.append(Object(object_type=object_type, memory=memory, plotter=plotter))

        # Plotter instance
        self.plt = plotter
        self.active = True

    @property
    def vedo_objects(self) -> List[Points]:
        """
        Get the list of visual objects in the factory.
        """
        return [o.object for o in self.__objects]

    @property
    def count(self) -> int:
        """
        Get the counter value in the simulation process.
        """

        return self.__sync_arr[2]

    def listen(self) -> None:
        """
        Launch the listening thread of the factory.
        """

        # Launch the listening thread
        thread = Thread(target=self.__listen)
        thread.start()

        # Notify to the simulation process that the viewer is ready
        self.__socket.send(b'done')

    def __listen(self) -> None:
        """
        Listening thread of the factory.
        """

        # Do nothing while the do_exit flag is not turned on
        while not self.__sync_arr[0]:
            # Do not access the shared array value to often
            sleep(0.1)

        # Do not exit while the rendering window is not closed
        while not self.plt._must_close_now:
            pass
        self.close()

    def update(self) -> None:
        """
        Update the visual objects.
        """

        # Update each visual object
        for o in self.__objects:
            o.update()

        # Notify the simulation process if the do_synchronize flag is turned on
        if self.__sync_arr[1] == 1:
            self.__socket.send(b'done')

    def set_frame(self, idx: int) -> None:

        for o in self.__objects:
            o.set_frame(idx=idx)

    def close(self):
        """
        Close the communication with the simulation process.
        """

        # If the window is closed manually then turn the do_exit flag to True
        if not self.__sync_arr[0]:
            self.__sync_arr[0] = 1

        # Close the connection with the shared memories (synchronization array and each visual object array)
        try:
            self.__sync_sm.close()
        except OSError:
            pass

        for memory in self.__memories:
            memory.close()

        # Notify the simulation
        self.__socket.send(b'done')

        # Wait for the simulation process to close connections with the shared memories
        self.__socket.recv(4)

        # Close socket
        self.__socket.close()


class Object:

    def __init__(self, object_type: str, memory: Memory, plotter: Plotter):
        """
        This class gathers the methods to create and update visual object instances.

        :param object_type: Object type (mesh, points...).
        :param memory: Shared memories access.
        """

        # Shared memories access
        self.__memory = memory

        # Create the visual object instance
        self.object: Optional[Points] = None
        self.plt = plotter
        self.__getattribute__(f'_create_{object_type}')()

        # Define the update method depending on the visual object type
        self.update = self.__getattribute__(f'_update_{object_type}')
        self.set_frame = self.__getattribute__(f'_set_frame_{object_type}')

    def _create_mesh(self) -> None:
        """
        Create a mesh instance.
        """

        # Access data fields
        data, _ = self.__memory.get()
        cells = data['cells'] if len(data['cells'].shape) > 1 else get_mesh_cells(flat_cells=data['cells'])

        # Create instance
        color = data['color'].item() if len(data['color'].shape) == 0 else data['color']
        self.object = Mesh(inputobj=[data['positions'], cells], c=color, alpha=data['alpha'].item())
        self.object.wireframe(value=data['wireframe'].item()).lw(linewidth=data['line_width'].item())

        # Apply cmap
        if not isnan(data['colormap_field']).any():
            if not isnan(data['colormap_range']).any():
                self.object.cmap(input_cmap=data['colormap'].item(), input_array=data['colormap_field'],
                                 vmin=data['colormap_range'][0], vmax=data['colormap_range'][1])
            else:
                self.object.cmap(input_cmap=data['colormap'].item(), input_array=data['colormap_field'])

        # Apply texture
        elif not isnan(data['texture_coords']).any() and data['texture_name'].item() != '':
            self.object.texture(tname=data['texture_name'].item(), tcoords=data['texture_coords'])

    def _update_mesh(self) -> None:
        """
        Update a mesh instance.
        """

        self.object: Mesh
        data, dirty = self.__memory.get()

        # Update positions
        if dirty['positions']:
            self.object.vertices = data['positions']

        # Update color
        if dirty['color']:
            self.object.color(data['color'].item() if len(data['color'].shape) == 0 else data['color'])
        if dirty['alpha']:
            self.object.alpha(data['alpha'].item())
        if dirty['colormap_field']:
            if not isnan(data['colormap_range']).any():
                self.object.cmap(input_cmap=data['colormap'].item(),
                                 input_array=data['colormap_field'],
                                 vmin=data['colormap_range'][0], vmax=data['colormap_range'][1])
            else:
                self.object.cmap(input_cmap=data['colormap'].item(),
                                 input_array=data['colormap_field'])

        # Update rendering style
        if dirty['wireframe']:
            self.object.wireframe(data['wireframe'].item())
        if dirty['line_width']:
            self.object.linewidth(data['line_width'].item())

    def _set_frame_mesh(self, idx: int) -> None:
        """
        Update a mesh instance.
        """

        self.object: Mesh
        data = self.__memory.get_frame(idx=idx)

        # Update positions
        self.object.vertices = data['positions']

        # Update color
        self.object.color(data['color'].item() if len(data['color'].shape) == 0 else data['color'])
        self.object.alpha(data['alpha'].item())
        if not isnan(data['colormap_field']).any():
            if not isnan(data['colormap_range']).any():
                self.object.cmap(input_cmap=data['colormap'].item(),
                                 input_array=data['colormap_field'],
                                 vmin=data['colormap_range'][0], vmax=data['colormap_range'][1])
            else:
                self.object.cmap(input_cmap=data['colormap'].item(),
                                 input_array=data['colormap_field'])

        # Update rendering style
        self.object.wireframe(data['wireframe'].item())
        self.object.linewidth(data['line_width'].item())

    def _create_points(self) -> None:
        """
        Create a point cloud instance.
        """

        # Access data fields
        data, _ = self.__memory.get()

        # Create instance
        color = data['color'].item() if len(data['color'].shape) == 0 else data['color']
        self.object = Points(inputobj=data['positions'], r=data['point_size'].item(),
                             c=color, alpha=data['alpha'].item())

        # Apply cmap
        if not isnan(data['colormap_field']).any():
            if not isnan(data['colormap_range']).any():
                self.object.cmap(input_cmap=data['colormap'].item(), input_array=data['colormap_field'],
                                 vmin=data['colormap_range'][0], vmax=data['colormap_range'][1])
            else:
                self.object.cmap(input_cmap=data['colormap'].item(), input_array=data['colormap_field'])

    def _update_points(self):
        """
        Update a point cloud instance.
        """

        self.object: Points
        data, dirty = self.__memory.get()

        # Update positions
        if dirty['positions']:
            self.object.vertices = data['positions']

        # Update color
        if dirty['color']:
            self.object.color(data['color'].item() if len(data['color'].shape) == 0 else data['color'])
        if dirty['alpha']:
            self.object.alpha(data['alpha'].item())
        if dirty['colormap_field']:
            if not isnan(data['colormap_range']).any():
                self.object.cmap(input_cmap=data['colormap'].item(),
                                 input_array=data['colormap_field'],
                                 vmin=data['colormap_range'][0], vmax=data['colormap_range'][1])
            else:
                self.object.cmap(input_cmap=data['colormap'].item(), input_array=data['colormap_field'])

        # Update rendering style
        if dirty['point_size']:
            self.object.point_size(data['point_size'].item())

    def _set_frame_points(self, idx: int):
        """
        Update a point cloud instance.
        """

        self.object: Points
        data = self.__memory.get_frame(idx=idx)

        # Update positions
        self.object.vertices = data['positions']

        # Update color
        self.object.color(data['color'].item() if len(data['color'].shape) == 0 else data['color'])
        self.object.alpha(data['alpha'].item())
        if not isnan(data['colormap_field']).any():
            if not isnan(data['colormap_range']).any():
                self.object.cmap(input_cmap=data['colormap'].item(),
                                 input_array=data['colormap_field'],
                                 vmin=data['colormap_range'][0], vmax=data['colormap_range'][1])
            else:
                self.object.cmap(input_cmap=data['colormap'].item(), input_array=data['colormap_field'])

        # Update rendering style
        self.object.point_size(data['point_size'].item())

    def _create_arrows(self) -> None:
        """
        Create an arrows instance.
        """

        # Access data fields
        data, _ = self.__memory.get()

        # Create instance
        color = data['color'].item() if len(data['color'].shape) == 0 else data['color']
        self.object = Arrows(start_pts=data['positions'], end_pts=data['positions'] + data['vectors'],
                             c=color, alpha=data['alpha'].item())

        # Apply cmap
        if not isnan(data['colormap_field']).any():
            if not isnan(data['colormap_range']).any():
                cmap_norm = Normalize(vmin=float(data['colormap_range'][0]), vmax=float(data['colormap_range'][1]))
            else:
                cmap_norm = Normalize(vmin=min(data['colormap_field']), vmax=max(data['colormap_field']))
            cmap = get_cmap(data['colormap'].item())
            self.object.color(c=cmap(cmap_norm(data['colormap_field']))[:, :3])

    def _update_arrows(self):
        """
        Update an arrows instance.
        """

        self.object: Arrows
        data, dirty = self.__memory.get()

        # Update positions & vectors
        if dirty['positions'] or dirty['vectors']:
            self.plt.remove(self.object)
            self._create_arrows()
            self.plt.add(self.object)

        # Update color
        if dirty['color']:
            self.object.color(data['color'].item() if len(data['color'].shape) == 0 else data['color'])
        if dirty['alpha']:
            self.object.alpha(data['alpha'].item())
        if dirty['colormap_field']:
            if not isnan(data['colormap_range']).any():
                cmap_norm = Normalize(vmin=float(data['colormap_range'][0]),
                                      vmax=float(data['colormap_range'][1]))
            else:
                cmap_norm = Normalize(vmin=min(data['colormap_field']), vmax=max(data['colormap_field']))
            cmap = get_cmap(data['colormap'].item())
            self.object.color(c=cmap(cmap_norm(data['colormap_field']))[:, :3])

    def _set_frame_arrows(self, idx: int):
        """
        Update an arrows instance.
        """

        self.object: Arrows
        data = self.__memory.get_frame(idx=idx)

        self.plt.remove(self.object)

        # Create instance
        color = data['color'].item() if len(data['color'].shape) == 0 else data['color']
        self.object = Arrows(start_pts=data['positions'], end_pts=data['positions'] + data['vectors'],
                             c=color, alpha=data['alpha'].item())

        # Apply cmap
        if not isnan(data['colormap_field']).any():
            if not isnan(data['colormap_range']).any():
                cmap_norm = Normalize(vmin=float(data['colormap_range'][0]), vmax=float(data['colormap_range'][1]))
            else:
                cmap_norm = Normalize(vmin=min(data['colormap_field']), vmax=max(data['colormap_field']))
            cmap = get_cmap(data['colormap'].item())
            self.object.color(c=cmap(cmap_norm(data['colormap_field']))[:, :3])

        self.plt.add(self.object)

    def _create_lines(self):
        """
        Create a lines instance.
        """

        # Access data fields
        data, _ = self.__memory.get()

        # Create instance
        color = data['color'].item() if len(data['color'].shape) == 0 else data['color']
        self.object = Lines(start_pts=data['start_positions'], end_pts=data['end_positions'],
                            c=color, alpha=data['alpha'].item())
        self.object.lw(linewidth=data['line_width'].item())

    def _update_lines(self):
        """
        Update a lines instance.
        """

        self.object: Lines
        data, dirty = self.__memory.get()

        # Update positions
        if dirty['start_positions'] or dirty['end_positions']:
            self.object.vertices = array([data['start_positions'], data['end_positions']]).T.reshape((3, -1)).T

        # Update color
        if dirty['color']:
            self.object.color(data['color'].item() if len(data['color'].shape) == 0 else data['color'])
        if dirty['alpha']:
            self.object.alpha(data['alpha'].item())

        # Update rendering style
        if dirty['line_width']:
            self.object.linewidth(data['line_width'].item())

    def _set_frame_lines(self, idx: int):
        """
        Update a lines instance.
        """

        self.object: Lines

    def _create_text(self):
        """
        Create a text instance.
        """

        # Access data fields
        data, _ = self.__memory.get()

        # Create instance
        # content = data['content'].item().to_bytes((data['content'].item().bit_length() + 7) // 8, 'little')
        # content = content.decode('utf-8')
        content = data['content'].item()
        coord = {'R': 'right', 'L': 'left', 'T': 'top', 'M': 'middle', 'B': 'bottom'}
        corner = data['corner'].item()
        pos = f'{coord[corner[0].upper()]}-{coord[corner[1].upper()]}'
        color = data['color'].item() if len(data['color'].shape) == 0 else data['color']
        self.object = Text2D(txt=content,
                             pos=pos,
                             s=data['size'].item(),
                             font=data['font'].item(),
                             bold=data['bold'].item(),
                             italic=data['italic'].item(),
                             c=color)

    def _update_text(self):
        """
        Update a text instance.
        """

        self.object: Text2D
        data, dirty = self.__memory.get()

        # Update content
        if dirty['content']:
            # content = data['content'].item().to_bytes((data['content'].item().bit_length() + 7) // 8, 'little')
            # content = content.decode('utf-8')
            content = data['content'].item()
            self.object.text(txt=content)

        # Update color
        if dirty['color']:
            self.object.color(data['color'].item() if len(data['color'].shape) == 0 else data['color'])

        # Update rendering style
        if dirty['bold']:
            self.object.bold(data['bold'].item())
        if dirty['italic']:
            self.object.italic(data['italic'].item())

    def _set_frame_text(self, idx: int):
        """
        Create a text instance.
        """

        self.object: Text2D
        data = self.__memory.get_frame(idx=idx)

        # Update content
        # content = data['content'].item().to_bytes((data['content'].item().bit_length() + 7) // 8, 'little')
        # content = content.decode('utf-8')
        content = data['content'].item()
        self.object.text(txt=content)

        # Update color
        self.object.color(data['color'].item() if len(data['color'].shape) == 0 else data['color'])

        # Update rendering style
        self.object.bold(data['bold'].item()).italic(data['italic'].item())
