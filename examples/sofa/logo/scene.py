from os.path import join, dirname
import numpy as np
import Sofa


class Simulation(Sofa.Core.Controller):

    def __init__(self, root: Sofa.Core.Node, *args, **kwargs):
        """
        Simulation of the SOFA logo.
        Forces and constraints can be manually defined using the 'select_constraints.py' script.
        """

        Sofa.Core.Controller.__init__(self, name='PyController', *args, **kwargs)
        data_dir = join(dirname(__file__), 'data')

        # Root
        root.dt.value = 0.1
        with open(join(data_dir, 'plugins.txt'), 'r') as f:
            required_plugins = [plugin[:-1] if plugin.endswith('\n') else plugin for plugin in f.readlines()
                                if plugin != '\n']
        root.addObject('RequiredPlugin', pluginName=required_plugins)
        root.addObject('VisualStyle', displayFlags='showVisualModels showBehaviorModels showForceFields')
        root.addObject('DefaultAnimationLoop')
        root.addObject('GenericConstraintSolver', maxIterations=10, tolerance=1e-3)
        root.addObject('CollisionPipeline')
        root.addObject('BruteForceBroadPhase')
        root.addObject('BVHNarrowPhase')
        root.addObject('DiscreteIntersection')
        root.addObject('CollisionResponse')

        root.addChild('logo')
        root.logo.addObject('EulerImplicitSolver', firstOrder=False, rayleighMass=0.1, rayleighStiffness=0.1)
        root.logo.addObject('CGLinearSolver', iterations=25, tolerance=1e-9, threshold=1e-9)
        root.logo.addObject('MeshVTKLoader', name='mesh', filename=join(data_dir, 'volume.vtk'), rotation=[90, 0, 0])
        root.logo.addObject('TetrahedronSetTopologyContainer', name='topology', src='@mesh')
        root.logo.addObject('TetrahedronSetGeometryAlgorithms', template='Vec3d')
        root.logo.addObject('MechanicalObject', name='state', src='@topology')
        root.logo.addObject('TetrahedronFEMForceField', youngModulus=2000, poissonRatio=0.4, method='svd')
        root.logo.addObject('MeshMatrixMass', totalMass=0.01)
        root.logo.addObject('FixedConstraint', name='constraints', indices=np.load(join(data_dir, 'constraints.npy')))

        root.logo.addChild('forces')
        root.logo.forces.addObject('MechanicalObject', name='state', src='@../topology')
        root.logo.forces.addObject('IdentityMapping')

        indices = np.load(join(data_dir, 'forces.npy'))
        n = {int(i): np.array([], dtype=int) for i in indices}
        for i in n.keys():
            idx = np.where(np.isin(root.logo.topology.triangles.value[:], i))[0]
            n[i] = np.unique(np.concatenate(root.logo.topology.triangles.value[idx]))
        clusters = []
        for idx, nei in n.items():
            if len(clusters) == 0:
                clusters.append([idx])
            else:
                new_cluster = True
                for i_c in range(len(clusters)):
                    if len(set(clusters[i_c]).intersection(set(nei))) > 0:
                        clusters[i_c].append(idx)
                        new_cluster = False
                        break
                if new_cluster:
                    clusters.append([idx])

        # Create ForceFields
        for i, cluster in enumerate(clusters):
            root.logo.forces.addObject('ConstantForceField', name=f'cff_{i}', indices=cluster,
                                            forces=np.random.choice([-0.5, 0.5], (3,)), showArrowSize=1)

        root.logo.addChild('collision')
        root.logo.collision.addObject('TriangleSetTopologyContainer', name='topology')
        root.logo.collision.addObject('TriangleSetTopologyModifier', name='Modifier')
        root.logo.collision.addObject('Tetra2TriangleTopologicalMapping', input='@../topology', output='@topology')
        root.logo.collision.addObject('MechanicalObject', name='state', rest_position="@../state.rest_position")
        root.logo.collision.addObject('TriangleCollisionModel')
        root.logo.collision.addObject('IdentityMapping')

        root.logo.addChild('visual')
        root.logo.visual.addObject('MeshOBJLoader', name='mesh', filename=join(data_dir, 'surface.obj'),
                                        rotation=[90, 0, 0])
        root.logo.visual.addObject('OglModel', name='ogl', color='0.85 .3 0.1 0.9', src='@mesh')
        root.logo.visual.addObject('BarycentricMapping')
