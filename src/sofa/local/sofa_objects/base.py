from typing import Dict, Optional, Any
import Sofa


class Base:

    def __init__(self, sofa_object: Sofa.Core.Object):

        self.sofa_object = sofa_object
        self.sofa_node: Sofa.Core.Node = sofa_object.getLinks()[0].getLinkedBase()
        self.object_type = ''

    def create(self) -> Dict[str, Any]:
        raise NotImplementedError

    def update(self) -> Dict[str, Any]:
        raise NotImplementedError


class Mesh(Base):

    def __init__(self, sofa_object: Sofa.Core.Object):

        super().__init__(sofa_object=sofa_object)

        self.object_type = 'mesh'
        self.positions: Optional[Any] = None
        self.cells: Optional[Any] = None
        self.color: Optional[Any] = None
        self.alpha: Optional[Any] = None
        self.wireframe: Optional[Any] = None
        self.line_width: Optional[Any] = None
        self.texture_name: Optional[Any] = None
        self.texture_coords: Optional[Any] = None

    def create(self) -> Dict[str, Any]:

        res = {'positions': self.positions,
               'cells': self.cells,
               'color': self.color,
               'alpha': self.alpha,
               'wireframe': self.wireframe,
               'line_width': self.line_width,
               'texture_name': self.texture_name,
               'texture_coords': self.texture_coords}
        return {key: value for key, value in res.items() if value is not None}

    def update(self) -> Dict[str, Any]:

        res = {'positions': self.positions,
               'color': self.color,
               'alpha': self.alpha}
        return {key: value for key, value in res.items() if value is not None}
