from typing import Dict, Optional, Any
import Sofa


class Base:

    def __init__(self, sofa_object: Sofa.Core.Object):

        self.sofa_object = sofa_object
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

    def create(self) -> Dict[str, Any]:

        return {'positions': self.positions,
                'cells': self.cells,
                'color': self.color,
                'alpha': self.alpha}

    def update(self) -> Dict[str, Any]:

        return {'positions': self.positions,
                'color': self.color,
                'alpha': self.alpha}


