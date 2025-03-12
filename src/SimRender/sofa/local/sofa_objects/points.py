from typing import Dict, Any
import Sofa

from SimRender.sofa.local.sofa_objects.base import Object


class PointCollisionModel(Object):

    def __init__(self, sofa_object: Sofa.Core.Object):

        super().__init__(sofa_object=sofa_object)
        self.object_type = 'points'
        self.display_model = 'collision_model'

    def create(self) -> Dict[str, Any]:

        return {'positions': self.sofa_node.getMechanicalState().getData('position').value,
                'color': 'orange5',
                'alpha': 1.,
                'point_size': 7}

    def update(self) -> Dict[str, Any]:

        return {'positions': self.sofa_node.getMechanicalState().getData('position').value}


class MechanicalObject(Object):

    def __init__(self, sofa_object: Sofa.Core.Object):

        super().__init__(sofa_object=sofa_object)
        self.object_type = 'points'
        self.display_model = 'behavior_model'

    def create(self) -> Dict[str, Any]:

        return {'positions': self.sofa_object.getData('position').value,
                'color': 'grey5',
                'alpha': 0.5,
                'point_size': 3}

    def update(self) -> Dict[str, Any]:

        return {'positions': self.sofa_object.getData('position').value}


class FixedProjectiveConstraint(Object):

    def __init__(self, sofa_object: Sofa.Core.Object):

        super().__init__(sofa_object=sofa_object)
        self.object_type = 'points'
        self.display_model = 'behavior_model'

    def create(self) -> Dict[str, Any]:

        pos = self.sofa_node.getMechanicalState().getData('position').value[self.sofa_object.getData('indices').value, :3]
        return {'positions': pos,
                'color': 'red5',
                'alpha': 0.9,
                'point_size': 15}
