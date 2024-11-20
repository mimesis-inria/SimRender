from os.path import join, dirname
from math import sin, cos
from numpy import array
import Sofa
from splib3.numerics import to_radians
from stlib3.physics.collision import CollisionMesh
from stlib3.physics.mixedmaterial import Rigidify
from stlib3.components import addOrientedBoxRoi
from splib3.numerics import vec3
from splib3.numerics.quat import Quat

from .actuators import ActuatedArm
from .elasticbody import elastic_body


data_dir = join(dirname(__file__), 'data')


def __get_transform(index, num_step, angle_shift, dist):

    fi = float(index)
    fnumstep = float(num_step)
    angle = fi * 360 / fnumstep
    angle2 = fi * 360 / fnumstep + angle_shift
    euler_rotation = [0, angle, 0]
    translation = [dist * sin(to_radians(angle2)), -1.35, dist * cos(to_radians(angle2))]
    return translation, euler_rotation


def __rigidify(node, radius=60, num_motors=3, angle_shift=180.0):

    deformable_object = node.ElasticBody.MechanicalModel
    deformable_object.dofs.init()
    dist = radius
    num_step = num_motors
    group_indices = []
    frames = []

    for i in range(0, num_step):
        translation, euler_rotation = __get_transform(i, num_step, angle_shift, dist)
        box = addOrientedBoxRoi(node, name=f'BoxROI{i}',
                                position=array([list(i) for i in deformable_object.dofs.rest_position.value]),
                                translation=vec3.vadd(translation, [0.0, 25.0, 0.0]),
                                eulerRotation=euler_rotation, scale=[45, 15, 30])
        box.drawBoxes = False
        box.init()
        group_indices.append([ind for ind in box.indices.value])
        frames.append(vec3.vadd(translation, [0.0, 25.0, 0.0]) +
                      list(Quat.createFromEuler([0, float(i) * 360 / float(num_step), 0], inDegree=True)))

    effector_pos = [0, 30, 0]
    o = deformable_object.addObject('SphereROI', name='roi', template='Rigid3', centers=effector_pos,
                                    radii=[7.5], drawSphere=False)
    o.init()
    group_indices.append(list(o.indices.value))
    frames.append([effector_pos[0], effector_pos[1], effector_pos[2], 0, 0, 0, 1])

    # Rigidify the deformable part at extremity to attach arms
    Rigidify(node, deformable_object, groupIndices=group_indices, frames=frames, name='RigidifiedStructure')


def __attach_to_actuated_arms(node):

    rigid_parts = node.RigidifiedStructure.RigidParts
    for arm in node.actuated_arms:
        arm.ServoMotor.Articulation.ServoWheel.addChild(rigid_parts)

    free_center = node.RigidifiedStructure.addChild('FreeCenter')
    free_center.addObject('MechanicalObject', name='dofs', template='Rigid3', position=array([0, 30, 0, 0, 0, 0, 1]),
                          showObject=False, showObjectScale=10)
    free_center.addChild(rigid_parts)

    rigid_parts.addObject('SubsetMultiMapping', name='mapping',
                          input=[node.actuated_arms[0].ServoMotor.Articulation.ServoWheel.getLinkPath(),
                                 node.actuated_arms[1].ServoMotor.Articulation.ServoWheel.getLinkPath(),
                                 node.actuated_arms[2].ServoMotor.Articulation.ServoWheel.getLinkPath(),
                                 free_center.getLinkPath()],
                          output='@./', indexPairs=[0, 1, 1, 1, 2, 1, 3, 0])


def Tripod(name='Tripod', radius=60, num_motors=3, angle_shift=180.0):

    node = Sofa.Core.Node(name)
    node.actuated_arms = []

    for i in range(0, num_motors):
        translation, euler_rotation = __get_transform(i, num_motors, angle_shift, radius)
        arm = ActuatedArm(name=f'ActuatedArm{i}', translation=translation, rotation=euler_rotation)

        # Add limits to angle that correspond to limits on real robot
        arm.ServoMotor.minAngle = -2.0225
        arm.ServoMotor.maxAngle = -0.0255
        node.actuated_arms.append(arm)
        node.addChild(arm)

    node.addChild(elastic_body(translation=[0.0, 30, 0.0], rotation=[90, 0, 0], color=[1.0, 0.5, 0.5, 1.]))
    __rigidify(node, radius, num_motors, angle_shift)
    __attach_to_actuated_arms(node)
    CollisionMesh(node.ElasticBody.MechanicalModel, name="CollisionModel",
                  surfaceMeshFileName=join(data_dir, 'tripod_low.stl'),
                  translation=[0.0, 30, 0.0], rotation=[90, 0, 0], collisionGroup=1)
    return node
