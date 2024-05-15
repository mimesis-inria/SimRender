from typing import Dict, Any
import Sofa

from SimRender.sofa.local.sofa_objects.base import Mesh


class OglModel(Mesh):

    def __init__(self, sofa_object: Sofa.Core.Object):

        super().__init__(sofa_object=sofa_object)

    def create(self) -> Dict[str, Any]:

        # Position
        self.positions = self.sofa_object.getData('position').value
        # Cells
        self.cells = []
        for topology in ['triangles', 'quads']:
            cells = self.sofa_object.getData(topology).value
            if len(cells) > 0:
                self.cells += cells.tolist()
        # Color & alpha
        material = self.sofa_object.getData('material').value
        color = material.split('Diffuse')[1].split('Ambient')[0].split(' ')[2:-1]
        self.alpha = max(0.1, float(color[-1]))
        self.color = [float(c) for c in color[:-1]]
        return super().create()

    def update(self) -> Dict[str, Any]:

        # Position
        self.positions = self.sofa_object.getData('position').value

        return super().update()
