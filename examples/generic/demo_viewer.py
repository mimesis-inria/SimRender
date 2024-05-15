from os.path import join, dirname
import numpy as np
from vedo import Mesh

from SimRender.generic import Viewer


file = lambda f: join(dirname(__file__), 'data', f)


class Simulation:

    def __init__(self):
        """
        Simulation of a heartbeat cycle.
        Deformations are loaded from pre-recorded data.
        """

        self.step_id = 0

        # Load the heart data (mesh, recorded positions, displacement)
        self.heart_mesh = Mesh(inputobj=file('heart.obj'))
        self.heart_pos = np.load(file=file('heart.npy'))
        self.heart_disp = np.linalg.norm(self.heart_pos - self.heart_pos.mean(axis=0), axis=2)

        # Load the vessel data (mesh, recorded positions)
        self.vessel_mesh = Mesh(inputobj=file('vessels.obj'))
        # self.vessel_pos = np.load(file=file('vessels.npy'))

        # Create the viewer
        self.viewer = Viewer(sync=True)

    def init_viewer(self) -> None:
        """
        Init the 3D rendering of the simulation.
        """

        # Add a mesh object for the heart to the viewer
        self.viewer.objects.add_mesh(positions=self.heart_mesh.vertices,
                                     cells=self.heart_mesh.cells,
                                     alpha=0.8,
                                     colormap='jet',
                                     colormap_field=np.zeros(len(self.heart_mesh.vertices)),
                                     colormap_range=np.array([np.min(self.heart_disp), np.max(self.heart_disp)]))

        # Add a mesh object for the vessel to the viewer
        self.viewer.objects.add_mesh(positions=self.vessel_mesh.vertices,
                                     cells=self.vessel_mesh.cells,
                                     color='red2',
                                     alpha=0.8,
                                     line_width=0.)

        # Launch the rendering window
        self.viewer.launch()

    def step(self) -> None:
        """
        Load the next state of the simulation and update the viewer.
        """

        # Load the next state of the simulation
        self.step_id = (self.step_id + 1) % len(self.heart_pos)
        self.heart_mesh.vertices = self.heart_pos[self.step_id]
        # self.vessel_mesh.vertices = self.vessel_pos[self.step_id]

        # Update the mesh objects with the new positions
        self.viewer.objects.update_mesh(object_id=0,
                                        positions=self.heart_pos[self.step_id],
                                        colormap_field=self.heart_disp[self.step_id])
        # self.viewer.objects.update_mesh(object_id=1,
        #                                 positions=self.vessel_pos[self.step_id])

        # Update the rendering window
        self.viewer.render()

    def close(self) -> None:
        """
        End of the simulation.
        """

        # Close the rendering window
        self.viewer.shutdown()


if __name__ == '__main__':

    from time import time
    from numpy import array

    # Create the simulation
    simu = Simulation()

    # Init the visualization
    simu.init_viewer()

    # Run some steps of the simulation
    T = []
    for i in range(500):
        st = time()
        simu.step()
        T.append(time() - st)
    print(array(T).mean())

    # Close the simulation
    simu.close()
