import numpy as np
import Sofa

from SimRender.sofa import Viewer
from examples.sofa.logo.scene import Simulation


class Controller:

    def __init__(self, kp: float, ki: float, kd: float, sim: Simulation, targets: np.ndarray):

        self.root = sim.root
        self.targets = targets

        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.previous_error = self.get_error()
        self.current_error = self.previous_error
        self.integral = np.zeros_like(targets)

    def update(self):

        self.current_error = self.get_error()
        self.integral += self.current_error * self.root.dt.value

        proportional = self.kp * self.current_error
        derivative = self.kd * (self.current_error - self.previous_error) / self.root.dt.value
        integral_contrib = self.ki * self.integral
        forces = proportional + integral_contrib + derivative

        self.set_force(forces)
        self.previous_error = self.current_error

    @property
    def get_pos(self):

        cff = [self.root.logo.forces.getObject(f'cff_{i}') for i in range(4)]
        state = self.root.logo.getObject('state')
        return np.array([np.mean(state.position.value[ff.indices.value], axis=0) for ff in cff])

    def get_error(self):

        return self.targets - np.array(self.get_pos)

    def set_force(self, forces: np.ndarray):

        for i, force in enumerate(forces):
            cff = self.root.logo.forces.getObject(f'cff_{i}')
            cff.forces.value = np.tile(force, cff.forces.value.shape[0]).reshape((-1, 3))


if __name__ == '__main__':

    # SOFA: create and init the scene graph
    root = Sofa.Core.Node()
    simu = root.addObject(Simulation(root=root))
    Sofa.Simulation.init(root)
    targets = np.array([[2.25, 5., 1.5], [1., 11.5, -1.5], [7., 13., 1.75], [11., 10., -2.]])

    # PID
    pid = Controller(kp=0.1, ki=0.02, kd=1.0, sim=simu, targets=targets)

    # VIEWER: create the viewer, create objects and start the rendering
    viewer = Viewer(root_node=root, sync=False)
    viewer.objects.add_scene_graph()
    viewer.objects.add_points(positions=targets, point_size=15)
    lines_id = viewer.objects.add_lines(start_positions=pid.get_pos, end_positions=targets, line_width=5)
    viewer.launch()

    # SOFA: run a few time steps
    # VIEWER: update the rendering
    while np.linalg.norm(pid.current_error) > 0.15:
        Sofa.Simulation.animate(root, root.dt.value)
        viewer.objects.update_lines(object_id=lines_id, start_positions=pid.get_pos)
        viewer.render()
        pid.update()

    # VIEWER: close the rendering
    viewer.shutdown()
