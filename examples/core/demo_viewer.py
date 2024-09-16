from SimRender.core import Viewer
from simulation import Simulation


if __name__ == '__main__':

    # Create the simulation and the viewer
    simu = Simulation()
    viewer = Viewer(sync=True)

    # Init the visualization
    simu.init_viewer(viewer=viewer)
    viewer.launch()

    # Run some steps of the simulation
    while viewer.is_open:
        simu.step()
        viewer.render()

    # Close the rendering window
    viewer.shutdown()
