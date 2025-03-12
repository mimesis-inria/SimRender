from os.path import dirname, join
import Sofa, SofaRuntime


data_dir = join(dirname(__file__), 'data')


class ServoMotor(Sofa.Prefab):

    prefabParameters = [
        {'name': 'rotation', 'type': 'Vec3d', 'help': 'Rotation', 'default': [0.0, 0.0, 0.0]},
        {'name': 'translation', 'type': 'Vec3d', 'help': 'Translation', 'default': [0.0, 0.0, 0.0]},
        {'name': 'scale3d', 'type': 'Vec3d', 'help': 'Scale 3d', 'default': [1.0, 1.0, 1.0]}]

    prefabData = [
        {'name': 'minAngle', 'help': 'min angle of rotation (in radians)', 'type': 'float', 'default': -100},
        {'name': 'maxAngle', 'help': 'max angle of rotation (in radians)', 'type': 'float', 'default': 100},
        {'name': 'angleIn', 'help': 'angle of rotation (in radians)', 'type': 'float', 'default': 0},
        {'name': 'angleOut', 'help': 'angle of rotation (in degree)', 'type': 'float', 'default': 0}]

    def __init__(self, *args, **kwargs):

        Sofa.Prefab.__init__(self, *args, **kwargs)
        SofaRuntime.importPlugin('ArticulatedSystemPlugin')

        # Servo body
        servo_body = self.addChild('ServoBody')
        servo_body.addObject('MechanicalObject', name='dofs', template='Rigid3',
                             position=[[0., 0., 0., 0., 0., 0., 1.]], translation=self.translation.value,
                             rotation=self.rotation.value, scale3d=self.scale3d.value)
        servo_body.addObject('FixedProjectiveConstraint', indices=0)
        servo_body.addObject('UniformMass', totalMass=0.01)
        visual = servo_body.addChild('VisualModel')
        visual.addObject('MeshSTLLoader', name='loader',
                         filename=join(data_dir, 'SG90_servomotor.stl'))
        visual.addObject('MeshTopology', src='@loader')
        visual.addObject('OglModel', color=[0.15, 0.45, 0.75, 0.2], writeZTransparent=True)
        visual.addObject('RigidMapping', index=0)

        # Servo wheel
        angle = self.addChild('Articulation')
        angle.addObject('MechanicalObject', name='dofs', template='Vec1', position=[[0]],
                        rest_position=self.angleIn.getLinkPath())
        angle.addObject('RestShapeSpringsForceField', points=0, stiffness=1e9)
        angle.addObject('UniformMass', totalMass=0.01)
        servo_wheel = angle.addChild('ServoWheel')
        servo_wheel.addObject('MechanicalObject', name='dofs', template='Rigid3', showObjectScale=20,
                              position=[[0., 0., 0., 0., 0., 0., 1.], [0., 0., 0., 0., 0., 0., 1.]],
                              translation=self.translation.value, rotation=self.rotation.value,
                              scale3d=self.scale3d.value)
        servo_wheel.addObject('ArticulatedSystemMapping', input1="@../dofs", input2="@../../ServoBody/dofs",
                              output="@./")
        articulation_center = angle.addChild('ArticulationCenter')
        articulation_center.addObject('ArticulationCenter', parentIndex=0, childIndex=1, posOnParent=[0., 0., 0.],
                                      posOnChild=[0., 0., 0.])
        articulation = articulation_center.addChild('Articulations')
        articulation.addObject('Articulation', translation=False, rotation=True, rotationAxis=[1, 0, 0],
                               articulationIndex=0)
        angle.addObject('ArticulatedHierarchyContainer', printLog=False)
        self.angleOut.setParent(angle.dofs.position)


class ServoArm(Sofa.Prefab):

    prefabData = [
        {'name': 'mappingInputLink', 'type': 'string',
         'help': 'the rigid mechanical object that will control the orientation of the servo arm', 'default': ''},
        {'name': 'indexInput', 'type': 'int', 'help': 'index of the rigid the ServoArm should be mapped to',
         'default': 1}]

    def __init__(self, *args, **kwargs):

        Sofa.Prefab.__init__(self, *args, **kwargs)

    def init(self):

        self.addObject('MechanicalObject', name='dofs', size=1, template='Rigid3', showObject=False,
                       showObjectScale=5, translation=[0, 25, 0])

    def set_rigid_mapping(self, path):

        self.addObject('RigidMapping', name='mapping', input=path, index=self.indexInput.value)
        visual = self.addChild('visual')
        visual.addObject('MeshSTLLoader', name='loader', filename=join(data_dir, 'SG90_servoarm.stl'))
        visual.addObject('OglModel', name="OglModel", src="@loader", translation=[0., -25., 0.],
                       color=[1., 1., 1., 0.3], updateNormals=False, writeZTransparent=True)
        visual.addObject('RigidMapping', name='mapping')


class ActuatedArm(Sofa.Prefab):

    prefabParameters = [
        {'name': 'rotation', 'type': 'Vec3d', 'help': 'Rotation', 'default': [0.0, 0.0, 0.0]},
        {'name': 'translation', 'type': 'Vec3d', 'help': 'Translation', 'default': [0.0, 0.0, 0.0]},
        {'name': 'scale', 'type': 'Vec3d', 'help': 'Scale 3d', 'default': [1.0, 1.0, 1.0]}]

    prefabData = [
        {'name': 'angleIn', 'group': 'ArmProperties', 'help': 'angle of rotation (in radians) of the arm',
         'type': 'float', 'default':0},
        {'name': 'angleOut', 'group': 'ArmProperties', 'type': 'float', 'help': 'angle of rotation (in radians) of '
                                                                                'the arm', 'default': 0}]

    def __init__(self, *args, **kwargs):

        Sofa.Prefab.__init__(self, *args, **kwargs)
        self.servo_arm = None
        self.servo_motor = None

    def init(self):

        self.servo_motor = self.addChild(ServoMotor(name="ServoMotor", translation=self.translation.value,
                                                    rotation=self.rotation.value))
        self.servo_arm = self.servo_motor.Articulation.ServoWheel.addChild(ServoArm(name="ServoArm"))
        self.servo_arm.set_rigid_mapping(self.ServoMotor.Articulation.ServoWheel.dofs.getLinkPath())
        self.servo_motor.angleIn.setParent(self.angleIn)
        self.angleOut.setParent(self.ServoMotor.angleOut)
