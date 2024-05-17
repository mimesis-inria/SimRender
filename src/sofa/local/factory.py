from typing import List, Union, Dict
import Sofa

from SimRender.generic.local.factory import Factory as _Factory, Objects as _Objects
from SimRender.sofa.local.scene_graph import SceneGraph
from SimRender.sofa.local.sofa_objects import SOFA_OBJECTS, Base


class Factory(_Factory):

    def __init__(self, root_node: Sofa.Core.Node, sync: bool):
        """
        This class is used to create and update the visualization data in shared memories.

        :param root_node: Root node of the SOFA scene graph
        :param sync: If True, the update call is synchronized with the end of the remote rendering step.
        """

        super().__init__(sync=sync)

        self.objects = Objects(root_node=root_node, factory=self)
        self.callbacks: Dict[int, Base] = {}

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

    # TODO: add_sofa_mesh & add_sofa_point first, in the style of SSD
    #  (shared method for each object type, only check a variety of fields, then only add in
    #  OBJECTS the lists of object nams for each category)

    # def add_sofa_mesh(self,
    #                   positions_data: Sofa.Core.Data,
    #                   cells_data: Union[Sofa.Core.Data, List[Sofa.Core.Data]],
    #                   animated: bool = True) -> int:
    #
    #     # Positions data
    #     positions = positions_data.array()
    #     if len(positions) == 0:
    #         raise ValueError(f"Data contains an empty positions array.")
    #
    #     # Cells data
    #     cells = []
    #     cells_data = [cells_data] if not isinstance(cells_data, list) else cells_data
    #     for data in cells_data:
    #         if len(data.array()) > 0:
    #             cells += data.array().tolist()
    #     if len(cells) == 0:
    #         raise ValueError(f"Data contains empty topology arrays.")
    #
    #     # Add the mesh
    #     idx = self.add_mesh(positions=positions,
    #                         cells=cells)
    #     if animated:
    #         self.__factory.callbacks.append([self.__update_sofa_mesh,
    #                                          {'object_id': idx,
    #                                           'positions_data': positions_data}])
    #     return idx
    #
    # def __update_sofa_mesh(self,
    #                        object_id: int,
    #                        positions_data: Sofa.Core.Data):
    #
    #     self.update_mesh(object_id=object_id,
    #                      positions=positions_data.array())

    def add_scene_graph(self) -> None:
        """
        The whole SOFA scene graph is explored to create visual objects automatically.
        """

        # Process each sofa object in the scene graph
        for key, sofa_object in self.__scene_graph.graph.items():

            # Key format: root.child1...childN.@.Component<name>
            object_class = key.split('@.')[1].split('<')[0]

            # Handle the VisualStyle object
            if object_class == 'VisualStyle':
                display_flags = sofa_object.displayFlags.value.split('  ')
                # TODO: apply the display flags

            # Check if a configuration exists for the object
            elif object_class in SOFA_OBJECTS:
                data_wrapper = SOFA_OBJECTS[object_class](sofa_object=sofa_object)
                func = self.__getattribute__(f'add_{data_wrapper.object_type}')
                idx = func(**data_wrapper.create())
                self.__factory.callbacks[idx] = data_wrapper
