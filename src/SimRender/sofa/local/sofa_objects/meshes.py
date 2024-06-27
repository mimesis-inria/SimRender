from typing import Dict, Any
import Sofa

from SimRender.sofa.local.sofa_objects.base import Mesh


class OglModel(Mesh):

    def __init__(self, sofa_object: Sofa.Core.Object):

        super().__init__(sofa_object=sofa_object)
        self.display_model = 'visual'

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
        # Wireframe & line width
        self.wireframe = False
        self.line_width = 0
        # Texture
        self.texture_name = self.sofa_object.getData('texturename').value
        self.texture_coords = self.sofa_object.getData('texcoords').value
        return super().create()

    def update(self) -> Dict[str, Any]:

        # Position
        self.positions = self.sofa_object.getData('position').value
        # Color & alpha
        material = self.sofa_object.getData('material').value
        color = material.split('Diffuse')[1].split('Ambient')[0].split(' ')[2:-1]
        self.alpha = max(0.1, float(color[-1]))
        self.color = [float(c) for c in color[:-1]]
        return super().update()


class TriangleCollisionModel(Mesh):

    def __init__(self, sofa_object: Sofa.Core.Object):

        super().__init__(sofa_object=sofa_object)
        self.display_model = 'collision'

    def create(self) -> Dict[str, Any]:

        # Position
        self.positions = self.sofa_node.getMechanicalState().getData('position').value
        # Cells
        self.cells = self.sofa_object.findLink('topology').getLinkedBase().getData('triangles').value
        # Color & alpha
        self.alpha = 1.
        self.color = 'orange5'
        # Wireframe & line width
        self.wireframe = True
        self.line_width = 2
        return super().create()

    def update(self) -> Dict[str, Any]:

        # Position
        self.positions = self.sofa_node.getMechanicalState().getData('position').value
        return super().update()


class LineCollisionModel(Mesh):

    def __init__(self, sofa_object: Sofa.Core.Object):

        super().__init__(sofa_object=sofa_object)
        self.display_model = 'collision'

    def create(self) -> Dict[str, Any]:

        # Position
        self.positions = self.sofa_node.getMechanicalState().getData('position').value
        # Cells
        self.cells = self.sofa_object.findLink('topology').getLinkedBase().getData('edges').value
        # Color & alpha
        self.alpha = 1.
        self.color = 'orange5'
        # Wireframe & line width
        self.wireframe = True
        self.line_width = 2
        return super().create()

    def update(self) -> Dict[str, Any]:

        # Position
        self.positions = self.sofa_node.getMechanicalState().getData('position').value
        return super().update()
