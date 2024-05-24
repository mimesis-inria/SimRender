from typing import Optional
from os.path import join, dirname
import numpy as np
import Sofa


file = lambda f: join(dirname(__file__), 'data', f)


class Simulation(Sofa.Core.Controller):

    def __init__(self, root: Sofa.Core.Node, id_simu: Optional[int] = None, *args, **kwargs):
        """
        Simulation of the SOFA logo.
        Forces and constraints positions can be manually set with the 'selections.py' script.
        """

        Sofa.Core.Controller.__init__(self, name='PyController', *args, **kwargs)

        self.root = root
        self.create_graph(id_simu=id_simu)

    def create_graph(self, id_simu: Optional[int]) -> None:

        # Root
        self.root.dt.value = 0.1
        with open(file('plugins.txt'), 'r') as f:
            required_plugins = [plugin[:-1] if plugin.endswith('\n') else plugin for plugin in f.readlines()
                                if plugin != '\n']
        self.root.addObject('RequiredPlugin', pluginName=required_plugins)
        self.root.addObject('VisualStyle', displayFlags='showVisualModels showBehaviorModels showForceFields')
        self.root.addObject('DefaultAnimationLoop')
        self.root.addObject('GenericConstraintSolver', maxIterations=10, tolerance=1e-3)
        self.root.addObject('CollisionPipeline')
        self.root.addObject('BruteForceBroadPhase')
        self.root.addObject('BVHNarrowPhase')
        self.root.addObject('DiscreteIntersection')
        self.root.addObject('DefaultContactManager')

        self.root.addChild('logo')
        self.root.logo.addObject('EulerImplicitSolver', firstOrder=False, rayleighMass=0.1, rayleighStiffness=0.1)
        self.root.logo.addObject('CGLinearSolver', iterations=25, tolerance=1e-9, threshold=1e-9)
        self.root.logo.addObject('MeshVTKLoader', name='mesh', filename=file('volume.vtk'), rotation=[90, 0, 0])
        self.root.logo.addObject('TetrahedronSetTopologyContainer', name='topology', src='@mesh')
        self.root.logo.addObject('TetrahedronSetGeometryAlgorithms', template='Vec3d')
        self.root.logo.addObject('MechanicalObject', name='state', src='@topology')
        self.root.logo.addObject('TetrahedronFEMForceField', youngModulus=2000, poissonRatio=0.4, method='svd')
        self.root.logo.addObject('MeshMatrixMass', totalMass=0.01)
        self.root.logo.addObject('FixedConstraint', name='constraints', indices=np.load(file('constraints.npy')))

        self.root.logo.addChild('forces')
        self.root.logo.forces.addObject('MechanicalObject', name='state', src='@../topology')
        self.root.logo.forces.addObject('IdentityMapping')

        indices = np.load(file('forces.npy'))
        n = {int(i): np.array([], dtype=int) for i in indices}
        for i in n.keys():
            idx = np.where(np.isin(self.root.logo.topology.triangles.value[:], i))[0]
            n[i] = np.unique(np.concatenate(self.root.logo.topology.triangles.value[idx]))
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
        if id_simu is None:
            for i, cluster in enumerate(clusters):
                self.root.logo.forces.addObject('ConstantForceField', name=f'cff_{i}', indices=cluster,
                                                forces=np.random.choice([-0.5, 0.5], (3,)), showArrowSize=1)
        else:
            id_simu = id_simu % len(clusters)
            self.root.logo.forces.addObject('ConstantForceField', name='cff', indices=clusters[id_simu],
                                            forces=np.random.choice([-0.5, 0.5], (3,)), showArrowSize=1)

        self.root.logo.addChild('collision')
        self.root.logo.collision.addObject('TriangleSetTopologyContainer', name='topology')
        self.root.logo.collision.addObject('TriangleSetTopologyModifier', name='Modifier')
        self.root.logo.collision.addObject('Tetra2TriangleTopologicalMapping', input='@../topology', output='@topology')
        self.root.logo.collision.addObject('MechanicalObject', name='state', rest_position="@../state.rest_position")
        self.root.logo.collision.addObject('TriangleCollisionModel')
        self.root.logo.collision.addObject('IdentityMapping')

        self.root.logo.addChild('visual')
        self.root.logo.visual.addObject('MeshOBJLoader', name='mesh', filename=file('surface.obj'),
                                        rotation=[90, 0, 0])
        self.root.logo.visual.addObject('OglModel', name='ogl', color='0.85 .3 0.1 0.9', src='@mesh')
        self.root.logo.visual.addObject('BarycentricMapping')
