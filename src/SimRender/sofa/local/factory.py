from typing import List, Union, Dict, Optional, Callable
import Sofa
from numpy import array, ndarray, nan, tile

from SimRender.core.local.factory import Factory as _Factory, Objects as _Objects
from SimRender.sofa.local.scene_graph import SceneGraph
from SimRender.sofa.local.sofa_objects import collection, Object


class Factory(_Factory):

    def __init__(self, root_node: Sofa.Core.Node, sync: bool):
        """
        This class is used to create and update the visualization data in shared memories.

        :param root_node: Root node of the SOFA scene graph
        :param sync: If True, the update call is synchronized with the end of the remote rendering step.
        """

        super().__init__(sync=sync)

        self.objects = Objects(root_node=root_node, factory=self)
        self.callbacks: Dict[int, Object] = {}

    def update(self) -> None:

        for idx, data_wrapper in self.callbacks.items():
            func = self.objects.__getattribute__(f'update_{data_wrapper.object_type}')
            func(idx, **data_wrapper.update())

        super().update()


class Objects(_Objects):

    def __init__(self, root_node: Sofa.Core.Node, factory: Factory):
        """
        This class gathers the methods to create and update visual objects.

        :param factory: Factory that handles the objects.
        """

        super().__init__(factory=factory)

        self.__factory = factory
        self.__scene_graph = SceneGraph(root_node=root_node)
        self.__SOFA_OBJECTS = collection()

    def add_sofa_mesh(self,
                      positions_data: Sofa.Core.Data,
                      cells_data: Union[Sofa.Core.Data, List[Sofa.Core.Data]],
                      color: str = 'green',
                      alpha: float = 1.,
                      wireframe: bool = False,
                      line_width: float = 1.,
                      colormap: str = 'jet',
                      colormap_range: ndarray = array(nan),
                      colormap_function: Optional[Callable] = None) -> int:
        """
        Add a new mesh object in the viewer and record it automatically using the SOFA Data fields.

        :param positions_data: SOFA Data field containing the positions of the mesh.
        :param cells_data: SOFA Data field(s) containing the faces of the mesh.
        :param color: Color of the mesh.
        :param alpha: Opacity of the mesh.
        :param wireframe: If True, the mesh has a wireframe representation.
        :param line_width: Width of the mesh edges.
        :param colormap: Color map scheme name.
        :param colormap_range: Range of the color map.
        :param colormap_function: Function to compute at each time step the scalar values to color the mesh regarding
                                  the color map.
        :return: ID of the object in the viewer.
        """

        # Positions data
        positions = positions_data.array().copy()
        if len(positions) == 0:
            raise ValueError(f"Data contains an empty positions array.")

        # Cells data
        cells = []
        cells_data = cells_data if isinstance(cells_data, list) else [cells_data]
        for data in cells_data:
            if len(data.array()) > 0:
                cells += data.array().tolist()
        if len(cells) == 0:
            raise ValueError(f"Data contains empty topology arrays.")

        class DataWrapper:
            object_type: str = 'mesh'

            def update(self):
                return {'positions': positions_data.array().copy(),
                        'colormap_field': None if colormap_function is None else colormap_function()}

        # Create the mesh and add the data wrapper callback
        idx = self.add_mesh(positions=positions_data.array().copy(),
                            cells=cells,
                            color=color,
                            alpha=alpha,
                            wireframe=wireframe,
                            line_width=line_width,
                            colormap=colormap,
                            colormap_range=colormap_range,
                            colormap_field=colormap_function() if colormap_function is not None else array(nan))
        self.__factory.callbacks[idx] = DataWrapper()

        return idx

    def add_sofa_points(self,
                        positions_data: Sofa.Core.Data,
                        color: str = 'green',
                        alpha: float = 1.,
                        point_size: int = 4,
                        colormap: str = 'jet',
                        colormap_range: ndarray = array(nan),
                        colormap_function: Optional[Callable] = None) -> int:
        """
        Add a new point cloud in the viewer and record it automatically using the SOFA Data fields.

        :param positions_data: SOFA Data field containing the positions of the points.
        :param color: Color of the point cloud.
        :param alpha: Opacity of the point cloud.
        :param point_size: Size of points.
        :param colormap: Color map scheme name.
        :param colormap_range: Range of the color map.
        :param colormap_function: Function to compute at each time step the scalar values to color the points regarding
                                  the color map.
        :return: ID of the object in the viewer.
        """

        # Positions data
        positions = positions_data.array().copy()
        if len(positions) == 0:
            raise ValueError(f"Data contains an empty positions array.")

        class DataWrapper:
            object_type: str = 'points'

            def update(self):
                return {'positions': positions_data.array().copy(),
                        'colormap_field': None if colormap_function is None else colormap_function()}

        # Create the points and add the data wrapper callback
        idx = self.add_points(positions=positions_data.array().copy(),
                              color=color,
                              alpha=alpha,
                              point_size=point_size,
                              colormap=colormap,
                              colormap_range=colormap_range,
                              colormap_field=colormap_function() if colormap_function is not None else array(nan))
        self.__factory.callbacks[idx] = DataWrapper()

        return idx

    def add_sofa_arrows(self,
                        positions_data: Sofa.Core.Data,
                        vectors_data: Sofa.Core.Data,
                        color: str = 'green',
                        alpha: float = 1.,
                        colormap: str = 'jet',
                        colormap_range: ndarray = array(nan),
                        colormap_function: Optional[Callable] = None) -> int:
        """
        Add a new point cloud in the viewer.

        :param positions_data: SOFA Data field containing the positions of the arrows bases.
        :param vectors_data: SOFA Data field containing the vectors of the arrows.
        :param color: Color of the arrows.
        :param alpha: Opacity of the arrows.
        :param colormap: Color map scheme name.
        :param colormap_range: Range of the color map.
        :param colormap_function: Function to compute at each time step the scalar values to color the arrows regarding
                                  the color map.
        :return: ID of the object in the viewer.
        """

        # Positions data
        positions = positions_data.array().copy()
        if len(positions) == 0:
            raise ValueError(f"Data contains an empty positions array.")

        # Vectors data
        vectors = vectors_data.array().copy()
        if len(vectors) == 0:
            raise ValueError("Data contains an empty  vectors array.")
        if vectors.shape[0] == 1:
            vectors = tile(vectors, positions.shape[0]).reshape(-1, 3)

        class DataWrapper:
            object_type: str = 'arrows'

            def update(self):
                return {'positions': positions_data.array().copy(),
                        'vectors': vectors_data.array().copy(),
                        'colormap_field': None if colormap_function is None else colormap_function()}

        # Create the arrows and add the data wrapper callback
        idx = self.add_arrows(positions=positions_data.array().copy(),
                              vectors=vectors,
                              color=color,
                              alpha=alpha,
                              colormap=colormap,
                              colormap_range=colormap_range,
                              colormap_field=colormap_function() if colormap_function is not None else array(nan))
        self.__factory.callbacks[idx] = DataWrapper()

        return idx

    def add_sofa_object(self, sofa_object: Sofa.Core.Object) -> int:
        """
        Create a 3D object automatically from the Data fields of a SOFA Object.
        It will work only if the representation of this component is implemented.

        :param sofa_object: SOFA Object to render in the viewer.
        :return: ID of the object in the viewer.
        """

        # Check if the component is implemented
        object_class = sofa_object.getClassName()
        if object_class in self.__SOFA_OBJECTS:

            data_wrapper = self.__SOFA_OBJECTS[object_class](sofa_object=sofa_object)
            func = self.__getattribute__(f'add_{data_wrapper.object_type}')
            idx = func(**data_wrapper.create())
            self.__factory.callbacks[idx] = data_wrapper
            return idx

        else:
            print(f"WARNING: Could not create a 3D object for this component as the class representation is not"
                  f"implemented. Available components are {self.__SOFA_OBJECTS.keys()}.")

    def add_scene_graph(self,
                        visual_models: bool = True,
                        behavior_models: bool = False,
                        force_fields: bool = False,
                        collision_models: bool = False) -> None:
        """
        The whole SOFA scene graph is explored to create visual objects automatically.

        :param visual_models: If True, display each detected visual model in the scene graph.
        :param behavior_models: If True, display each detected behavior model in the scene graph.
        :param force_fields: If True, display each detected force field in the scene graph.
        :param collision_models: If True, display each detected collision model in the scene graph.
        """

        display_models = {'visual_model': visual_models, 'behavior_model': behavior_models,
                          'force_field': force_fields, 'collision_model': collision_models}

        # Process each sofa object in the scene graph
        for key, sofa_object in self.__scene_graph.graph.items():

            # Key format: root.child1...childN.@.Component<name>
            object_class = key.split('@.')[1].split('<')[0]

            # Handle the VisualStyle object
            if object_class == 'VisualStyle':
                display_flags = sofa_object.displayFlags.value.split('  ')
                # TODO: apply the display flags

            # Check if a configuration exists for the object
            elif object_class in self.__SOFA_OBJECTS:
                data_wrapper = self.__SOFA_OBJECTS[object_class](sofa_object=sofa_object)
                if display_models[data_wrapper.display_model]:
                    func = self.__getattribute__(f'add_{data_wrapper.object_type}')
                    idx = func(**data_wrapper.create())
                    self.__factory.callbacks[idx] = data_wrapper
