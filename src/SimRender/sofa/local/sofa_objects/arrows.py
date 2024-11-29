from typing import Dict, Any
import numpy as np
import Sofa

from SimRender.sofa.local.sofa_objects.base import Object


class ConstantForceField(Object):

    def __init__(self, sofa_object: Sofa.Core.Object):

        super().__init__(sofa_object=sofa_object)
        self.object_type = 'arrows'
        self.display_model = 'force_field'

    def create(self) -> Dict[str, Any]:

        pos = self.sofa_node.getMechanicalState().getData('position').value[self.sofa_object.getData('indices').value]
        vec = self.sofa_object.getData('forces').value * self.sofa_object.getData('showArrowSize').value
        return {'positions': pos,
                'vectors': np.tile(vec, pos.shape[0]).reshape(-1, 3),
                'color': 'green5',
                'alpha': 1.}

    def update(self) -> Dict[str, Any]:

        return {'positions': self.sofa_node.getMechanicalState().getData('position').value[self.sofa_object.getData('indices').value],
                'vectors': self.sofa_object.getData('forces').value * self.sofa_object.getData('showArrowSize').value}
