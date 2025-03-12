from os.path import dirname, join
import Sofa


data_dir = join(dirname(__file__), 'data')


def elastic_body(rotation, translation, color):

    node = Sofa.Core.Node('ElasticBody')

    # Mechanical model
    mechanical_model = node.addChild("MechanicalModel")
    mechanical_model.addObject('GIDMeshLoader', name='loader', rotation=rotation, translation=translation,
                               filename=join(data_dir, 'tripod_low.gidmsh'))
    mechanical_model.addObject('MeshTopology', src='@loader', name='container')

    mechanical_model.addObject('MechanicalObject', name='dofs', position=mechanical_model.loader.position,
                               showObject=False, showObjectScale=5.0)
    mechanical_model.addObject('UniformMass', name="mass", totalMass=0.032)
    mechanical_model.addObject('TetrahedronFEMForceField', name="linearElasticBehavior",
                               youngModulus=250, poissonRatio=0.45)

    # Visual model
    visual_model = node.addChild("VisualModel")
    visual_model.addObject('MeshSTLLoader', name='loader', filename=join(data_dir, 'tripod_mid.stl'),
                           rotation=rotation, translation=translation)
    visual_model.addObject('OglModel', src=visual_model.loader.getLinkPath(), name='renderer', color=color)
    visual_model.addObject('BarycentricMapping', input=mechanical_model.dofs.getLinkPath(),
                           output=visual_model.renderer.getLinkPath())

    return node
