import Sofa
from os.path import join, dirname


file = lambda f: join(dirname(__file__), 'data', 'caduceus', f)


class Simulation(Sofa.Core.Controller):

    def __init__(self, root: Sofa.Core.Node, *args, **kwargs):
        """
        Python translation of the famous caduceus SOFA simulation.
        """

        Sofa.Core.Controller.__init__(self, name='PyController', *args, **kwargs)

        self.root = root
        self.create_graph()

    def create_graph(self) -> None:

        # Root
        self.root.dt.value = 0.04
        self.root.gravity.value = [0, -1000, 0]
        with open(file('plugins.txt'), 'r') as f:
            required_plugins = [plugin[:-1] if plugin.endswith('\n') else plugin for plugin in f.readlines()
                                if plugin != '\n']
        self.root.addObject('RequiredPlugin', pluginName=required_plugins)
        self.root.addObject('VisualStyle', displayFlags='showVisualModels')
        self.root.addObject('FreeMotionAnimationLoop', parallelCollisionDetectionAndFreeMotion=False)
        self.root.addObject('CollisionPipeline', depth=15, verbose=0, draw=0)
        self.root.addObject('BruteForceBroadPhase')
        self.root.addObject('BVHNarrowPhase')
        self.root.addObject('MinProximityIntersection', alarmDistance=1.5, contactDistance=1)
        self.root.addObject('CollisionResponse', response='FrictionContactConstraint')
        self.root.addObject('LCPConstraintSolver', tolerance=1e-3, maxIt=1000, initial_guess=False,
                            build_lcp=False, printLog=0, mu=0.2)

        # Camera
        self.root.addObject('InteractiveCamera', position=[0, 30, 90], lookAt=[0, 30, 0])
        self.root.addObject('LightManager')
        self.root.addObject('SpotLight', name='light1', position=[0, 80, 25], direction=[0, -1, -0.8], cutoff=30,
                            exponent=1)
        self.root.addObject('SpotLight', name='light2', position=[0, 40, 100], direction=[0, 0, -1], cutoff=30,
                            exponent=1)

        # Snake.Physics
        self.root.addChild('snake')
        self.root.snake.addObject('MeshOBJLoader', name='Snake', filename=file('snake_body.obj'))
        self.root.snake.addObject('EulerImplicitSolver', rayleighMass=1, rayleighStiffness=0.03)
        self.root.snake.addObject('MatrixLinearSystem', name='LinearSystem', template='CompressedRowSparseMatrixMat3x3')
        self.root.snake.addObject('CGLinearSolver', iterations=20, tolerance=1e-12, threshold=1e-18,
                                  template='CompressedRowSparseMatrixMat3x3d', linearSystem='@LinearSystem')
        self.root.snake.addObject('SparseGridRamificationTopology', name='Grid', src='@Snake', n=[4, 12, 3],
                                  nbVirtualFinerLevels=3, finestConnectivity=0)
        self.root.snake.addObject('MechanicalObject', name='MO', src='@Grid', scale=1, dy=2)
        self.root.snake.addObject('UniformMass', totalMass=1.)
        self.root.snake.addObject('HexahedronFEMForceField', youngModulus=30000, poissonRatio=0.3, method='large',
                                  updateStiffnessMatrix=False)
        self.root.snake.addObject('UncoupledConstraintCorrection', defaultCompliance=184,
                                  useOdeSolverIntegrationFactors=False)

        # Snake.Collision
        self.root.snake.addChild('collision')
        self.root.snake.collision.addObject('MeshOBJLoader', name='SnakeColl',
                                            filename=file('meca_snake_900tri.obj'))
        self.root.snake.collision.addObject('MeshTopology', name='SnakeCollTopo', src='@SnakeColl')
        self.root.snake.collision.addObject('MechanicalObject', name='SnakeCollMo', src='@SnakeColl')
        self.root.snake.collision.addObject('TriangleCollisionModel', selfCollision=False)
        self.root.snake.collision.addObject('LineCollisionModel', selfCollision=False)
        self.root.snake.collision.addObject('PointCollisionModel', selfCollision=False)
        self.root.snake.collision.addObject('BarycentricMapping', input='@..', output='@.')

        # Snake.Visual
        self.root.snake.addChild('visual')
        self.root.snake.visual.addChild('body')
        self.root.snake.visual.body.addObject('MeshOBJLoader', name='SnakeBody', filename=file('snake_body.obj'))
        self.root.snake.visual.body.addObject('OglModel', name='OglBody', src='@SnakeBody',
                                              texturename=file('snakeColorMap.png'))
        self.root.snake.visual.body.addObject('BarycentricMapping', input='@../..', output='@.')
        self.root.snake.visual.addChild('eye')
        self.root.snake.visual.eye.addObject('MeshOBJLoader', name='SnakeEye', filename=file('snake_yellowEye.obj'))
        self.root.snake.visual.eye.addObject('OglModel', name='OglEye', src='@SnakeEye')
        self.root.snake.visual.eye.addObject('BarycentricMapping', input='@../..', output='@.')

        # Base.Collision
        self.root.addChild('base')
        self.root.base.addChild('stick')
        self.root.base.stick.addObject('MeshOBJLoader', name='Stick', filename=file('collision_batons.obj'))
        self.root.base.stick.addObject('MeshTopology', name='StickCollTopo', src='@Stick')
        self.root.base.stick.addObject('MechanicalObject', src='@Stick')
        self.root.base.stick.addObject('LineCollisionModel', simulated=False, moving=False)
        self.root.base.stick.addObject('PointCollisionModel', simulated=False, moving=False)
        self.root.base.addChild('blobs')
        self.root.base.blobs.addObject('MeshOBJLoader', name='Blobs', filename=file('collision_boules_V3.obj'))
        self.root.base.blobs.addObject('MeshTopology', name='BlobsCollTopo', src='@Blobs')
        self.root.base.blobs.addObject('MechanicalObject', src='@Blobs')
        self.root.base.blobs.addObject('TriangleCollisionModel', simulated=False, moving=False)
        self.root.base.blobs.addObject('LineCollisionModel', simulated=False, moving=False)
        self.root.base.blobs.addObject('PointCollisionModel', simulated=False, moving=False)
        self.root.base.addChild('foot')
        self.root.base.foot.addObject('MeshOBJLoader', name='Foot', filename=file('collision_pied.obj'))
        self.root.base.foot.addObject('MeshTopology', name='FootCollTopo', src='@Foot')
        self.root.base.foot.addObject('MechanicalObject', src='@Foot')
        self.root.base.foot.addObject('TriangleCollisionModel', simulated=False, moving=False)
        self.root.base.foot.addObject('LineCollisionModel', simulated=False, moving=False)
        self.root.base.foot.addObject('PointCollisionModel', simulated=False, moving=False)

        # Base.Visual
        self.root.base.addChild('visual')
        self.root.base.visual.addObject('MeshOBJLoader', name='Base', filename=file('SOFA_pod.obj'))
        self.root.base.visual.addObject('OglModel', name='OglBase', src='@Base')


def createScene(node):
    node.addObject(Simulation(root=node))


if __name__ == '__main__':

    import Sofa.Gui
    from os import listdir, remove

    root = Sofa.Core.Node()
    createScene(root)
    Sofa.Simulation.init(root)

    Sofa.Gui.GUIManager.Init(program_name="main", gui_name="qglviewer")
    Sofa.Gui.GUIManager.createGUI(root, __file__)
    Sofa.Gui.GUIManager.SetDimension(1200, 900)
    Sofa.Gui.GUIManager.MainLoop(root)
    Sofa.Gui.GUIManager.closeGUI()

    for file in [f for f in listdir() if f.endswith('.ini') or f.endswith('.log')]:
        remove(file)
