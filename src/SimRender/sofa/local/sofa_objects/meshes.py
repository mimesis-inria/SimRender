from typing import Dict, Any
import Sofa

from SimRender.sofa.local.sofa_objects.base import Object


class OglModel(Object):

    def __init__(self, sofa_object: Sofa.Core.Object):

        super().__init__(sofa_object=sofa_object)
        self.object_type = 'mesh'
        self.display_model = 'visual_model'

    def create(self) -> Dict[str, Any]:

        cells = []
        for topology in ['triangles', 'quads']:
            cells += self.sofa_object.getData(topology).value.tolist()
        color = self.sofa_object.getData('material').value.split('Diffuse')[1].split('Ambient')[0].split(' ')[2: -1]
        return {'positions': self.sofa_object.getData('position').value,
                'cells': cells,
                'color': [float(c) for c in color[:-1]],
                'alpha': max(0.1, float(color[-1])),
                'wireframe': False,
                'line_width': 0.,
                'texture_name': self.sofa_object.getData('texturename').value,
                'texture_coords': self.sofa_object.getData('texcoords').value}

    def update(self) -> Dict[str, Any]:

        color = self.sofa_object.getData('material').value.split('Diffuse')[1].split('Ambient')[0].split(' ')[2: -1]
        return {'positions': self.sofa_object.getData('position').value,
                'color': [float(c) for c in color[:-1]],
                'alpha': max(0.1, float(color[-1]))}


class TriangleCollisionModel(Object):

    def __init__(self, sofa_object: Sofa.Core.Object):

        super().__init__(sofa_object=sofa_object)
        self.object_type = 'mesh'
        self.display_model = 'collision_model'

    def create(self) -> Dict[str, Any]:

        return {'positions': self.sofa_node.getMechanicalState().getData('position').value,
                'cells': self.sofa_object.findLink('topology').getLinkedBase().getData('triangles').value,
                'color': 'orange5',
                'alpha': 1.,
                'wireframe': True,
                'line_width': 2.}

    def update(self) -> Dict[str, Any]:

        return {'positions': self.sofa_node.getMechanicalState().getData('position').value}


class LineCollisionModel(Object):

    def __init__(self, sofa_object: Sofa.Core.Object):

        super().__init__(sofa_object=sofa_object)
        self.object_type = 'mesh'
        self.display_model = 'collision_model'

    def create(self) -> Dict[str, Any]:

        return {'positions': self.sofa_node.getMechanicalState().getData('position').value,
                'cells': self.sofa_object.findLink('topology').getLinkedBase().getData('edges').value,
                'color': 'orange5',
                'alpha': 1.,
                'wireframe': True,
                'line_width': 2.}

    def update(self) -> Dict[str, Any]:

        return {'positions': self.sofa_node.getMechanicalState().getData('position').value}
