import Sofa
from os.path import join, dirname


class Simulation(Sofa.Core.Controller):

    def __init__(self, root: Sofa.Core.Node, *args, **kwargs):
        """
        Python translation of the famous caduceus SOFA simulation.
        """

        Sofa.Core.Controller.__init__(self, name='PyController', *args, **kwargs)
        data_dir = join(dirname(__file__), 'data')

        # Root
        root.dt.value = 0.04
        root.gravity.value = [0, -1000, 0]
        with open(join(data_dir, 'plugins.txt'), 'r') as f:
            required_plugins = [plugin[:-1] if plugin.endswith('\n') else plugin for plugin in f.readlines()
                                if plugin != '\n']
        root.addObject('RequiredPlugin', pluginName=required_plugins)
        root.addObject('VisualStyle', displayFlags='showVisualModels')
        root.addObject('FreeMotionAnimationLoop', parallelCollisionDetectionAndFreeMotion=False)
        root.addObject('CollisionPipeline', depth=15, verbose=0, draw=0)
        root.addObject('BruteForceBroadPhase')
        root.addObject('BVHNarrowPhase')
        root.addObject('MinProximityIntersection', alarmDistance=1.5, contactDistance=1)
        root.addObject('CollisionResponse', response='FrictionContactConstraint')
        root.addObject('LCPConstraintSolver', tolerance=1e-3, maxIt=1000, initial_guess=False,
                       build_lcp=False, printLog=0, mu=0.2)

        # Camera
        root.addObject('InteractiveCamera', position=[0, 30, 90], lookAt=[0, 30, 0])
        root.addObject('LightManager')
        root.addObject('SpotLight', name='light1', position=[0, 80, 25], direction=[0, -1, -0.8],
                       cutoff=30, exponent=1)
        root.addObject('SpotLight', name='light2', position=[0, 40, 100], direction=[0, 0, -1],
                       cutoff=30, exponent=1)

        # Snake.Physics
        root.addChild('snake')
        root.snake.addObject('MeshOBJLoader', name='Snake', filename=join(data_dir, 'snake_body.obj'))
        root.snake.addObject('EulerImplicitSolver', rayleighMass=1, rayleighStiffness=0.03)
        root.snake.addObject('MatrixLinearSystem', name='LinearSystem', template='CompressedRowSparseMatrixMat3x3')
        root.snake.addObject('CGLinearSolver', iterations=20, tolerance=1e-12, threshold=1e-18,
                             template='CompressedRowSparseMatrixMat3x3d', linearSystem='@LinearSystem')
        root.snake.addObject('SparseGridRamificationTopology', name='Grid', src='@Snake', n=[4, 12, 3],
                             nbVirtualFinerLevels=3, finestConnectivity=0)
        root.snake.addObject('MechanicalObject', name='MO', src='@Grid', scale=1, dy=2)
        root.snake.addObject('UniformMass', totalMass=1.)
        root.snake.addObject('HexahedronFEMForceField', youngModulus=30000, poissonRatio=0.3,
                             method='large', updateStiffnessMatrix=False)
        root.snake.addObject('UncoupledConstraintCorrection', defaultCompliance=184,
                             useOdeSolverIntegrationFactors=False)

        # Snake.Collision
        root.snake.addChild('collision')
        root.snake.collision.addObject('MeshOBJLoader', name='SnakeColl', filename=join(data_dir, 'meca_snake.obj'))
        root.snake.collision.addObject('MeshTopology', name='SnakeCollTopo', src='@SnakeColl')
        root.snake.collision.addObject('MechanicalObject', name='SnakeCollMo', src='@SnakeColl')
        root.snake.collision.addObject('TriangleCollisionModel', selfCollision=False)
        root.snake.collision.addObject('LineCollisionModel', selfCollision=False)
        root.snake.collision.addObject('PointCollisionModel', selfCollision=False)
        root.snake.collision.addObject('BarycentricMapping', input='@..', output='@.')

        # Snake.Visual
        root.snake.addChild('visual')
        root.snake.visual.addChild('body')
        root.snake.visual.body.addObject('MeshOBJLoader', name='SnakeBody', filename=join(data_dir, 'snake_body.obj'))
        root.snake.visual.body.addObject('OglModel', name='OglBody', src='@SnakeBody',
                                         texturename=join(data_dir, 'snakeColorMap.png'))
        root.snake.visual.body.addObject('BarycentricMapping', input='@../..', output='@.')
        root.snake.visual.addChild('eye')
        root.snake.visual.eye.addObject('MeshOBJLoader', name='SnakeEye', filename=join(data_dir, 'snake_eye.obj'))
        root.snake.visual.eye.addObject('OglModel', name='OglEye', src='@SnakeEye')
        root.snake.visual.eye.addObject('BarycentricMapping', input='@../..', output='@.')

        # Base.Collision
        root.addChild('base')
        root.base.addChild('stick')
        root.base.stick.addObject('MeshOBJLoader', name='Stick', filename=join(data_dir, 'collision_batons.obj'))
        root.base.stick.addObject('MeshTopology', name='StickCollTopo', src='@Stick')
        root.base.stick.addObject('MechanicalObject', src='@Stick')
        root.base.stick.addObject('LineCollisionModel', simulated=False, moving=False)
        root.base.stick.addObject('PointCollisionModel', simulated=False, moving=False)
        root.base.addChild('blobs')
        root.base.blobs.addObject('MeshOBJLoader', name='Blobs', filename=join(data_dir, 'collision_boules.obj'))
        root.base.blobs.addObject('MeshTopology', name='BlobsCollTopo', src='@Blobs')
        root.base.blobs.addObject('MechanicalObject', src='@Blobs')
        root.base.blobs.addObject('TriangleCollisionModel', simulated=False, moving=False)
        root.base.blobs.addObject('LineCollisionModel', simulated=False, moving=False)
        root.base.blobs.addObject('PointCollisionModel', simulated=False, moving=False)
        root.base.addChild('foot')
        root.base.foot.addObject('MeshOBJLoader', name='Foot', filename=join(data_dir, 'collision_pied.obj'))
        root.base.foot.addObject('MeshTopology', name='FootCollTopo', src='@Foot')
        root.base.foot.addObject('MechanicalObject', src='@Foot')
        root.base.foot.addObject('TriangleCollisionModel', simulated=False, moving=False)
        root.base.foot.addObject('LineCollisionModel', simulated=False, moving=False)
        root.base.foot.addObject('PointCollisionModel', simulated=False, moving=False)

        # Base.Visual
        root.base.addChild('visual')
        root.base.visual.addObject('MeshOBJLoader', name='Base', filename=join(data_dir, 'SOFA_pod.obj'))
        root.base.visual.addObject('OglModel', name='OglBase', src='@Base')
