from typing import Dict, Any
import numpy as np
import Sofa

from SimRender.sofa.local.sofa_objects.base import Arrows


class ConstantForceField(Arrows):

    def __init__(self, sofa_object: Sofa.Core.Object):

        super().__init__(sofa_object=sofa_object)
        self.display_model = 'force'

    def create(self) -> Dict[str, Any]:

        # Position
        self.positions = self.sofa_node.getMechanicalState().getData('position').value
        self.positions = self.positions[self.sofa_object.getData('indices').value]
        # Vectors
        self.vectors = self.sofa_object.getData('forces').value * self.sofa_object.getData('showArrowSize').value
        self.vectors = np.tile(self.vectors, self.positions.shape[0]).reshape(-1, 3)
        # Color & alpha
        self.color = 'green5'
        self.alpha = 1.
        return super().create()

    def update(self) -> Dict[str, Any]:

        # Position
        self.positions = self.sofa_node.getMechanicalState().getData('position').value
        self.positions = self.positions[self.sofa_object.getData('indices').value]
        # Vectors
        self.vectors = self.sofa_object.getData('forces').value * self.sofa_object.getData('showArrowSize').value
        return super().update()
