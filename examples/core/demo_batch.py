from SimRender.core import Viewer, ViewerBatch
from simulation import Simulation


if __name__ == '__main__':

    # Initialize the batch
    batch = ViewerBatch()
    nb_simu = 5
    batch_keys = batch.start(nb_view=nb_simu)

    # Create the simulations and the viewers (sync is not available in batch mode)
    simu = [Simulation() for _ in range(nb_simu)]
    viewer = [Viewer(sync=False) for _ in range(nb_simu)]

    # Init the visualization for each simulation
    for i in range(nb_simu):
        simu[i].init_viewer(viewer=viewer[i])
        viewer[i].launch(batch_key=batch_keys[i])

    # Run some steps of the simulation
    for _ in range(1000):
        for i in range(nb_simu):
            simu[i].step()
            viewer[i].render()

    # Close the rendering window
    for i in range(nb_simu):
        viewer[i].shutdown()
    batch.stop()
