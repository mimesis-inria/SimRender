import Sofa
from splib3.animation import animate
from splib3.constants import Key
from splib3.numerics import RigidDof


def reset_animation(actuators, step, angular_step, factor):

    for actuator in actuators:
        rigid = RigidDof(actuator.ServoMotor.ServoBody.dofs)
        rigid.setPosition(rigid.rest_position + rigid.forward * step * factor)
        actuator.angleIn = angular_step * factor


class Controller(Sofa.Core.Controller):

    def __init__(self, root, actuators, step_size=0.1, manual=True,  *args, **kwargs):

        Sofa.Core.Controller.__init__(self, *args, **kwargs)
        self.name = "TripodController"
        self.step_size = step_size
        self.actuators = actuators
        self.manual = manual

        cycle_len = 50
        self.sequence = [[chr(19)] * cycle_len + [chr(21)] * cycle_len,
                         [chr(18)] * cycle_len + [chr(20)] * cycle_len,
                         ['+']     * cycle_len + ['-']     * cycle_len]
        self.id_sequence = 0
        self.root = root

    def onSimulationInitDoneEvent(self, event):

        self.__animate_tripod('A')

    def onAnimateBeginEvent(self, event):

        if self.root.time.value > 0.2 and not self.manual:
            for s in self.sequence:
                self.__animate_tripod(s[self.id_sequence])
            self.id_sequence = (self.id_sequence + 1) % len(self.sequence[0])

    def onKeypressedEvent(self, event):

        self.__animate_tripod(event['key'])

    def __animate_tripod(self, key):

        if key == Key.A:
            animate(reset_animation, {"actuators": self.actuators, "step": 35.0, "angular_step": -1.4965},
                    duration=0.2)

        if key == Key.uparrow:
            self.actuators[0].ServoMotor.angleIn = self.actuators[0].ServoMotor.angleOut.value + self.step_size
        elif key == Key.downarrow:
            self.actuators[0].ServoMotor.angleIn = self.actuators[0].ServoMotor.angleOut.value - self.step_size

        if key == Key.leftarrow:
            self.actuators[1].ServoMotor.angleIn = self.actuators[1].ServoMotor.angleOut.value + self.step_size
        elif key == Key.rightarrow:
            self.actuators[1].ServoMotor.angleIn = self.actuators[1].ServoMotor.angleOut.value - self.step_size

        if key == Key.plus:
            self.actuators[2].ServoMotor.angleIn = self.actuators[2].ServoMotor.angleOut.value + self.step_size
        elif key == Key.minus:
            self.actuators[2].ServoMotor.angleIn = self.actuators[2].ServoMotor.angleOut.value - self.step_size
