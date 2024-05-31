import Sofa

from SimRender.generic import ViewerBatch
from SimRender.sofa import Viewer

from simulation_logo import Simulation


if __name__ == '__main__':

    # VIEWER: create and start the rendering
    batch = ViewerBatch()
    nb_simu = 4
    batch_keys = batch.start(nb_view=nb_simu)

    # SOFA: create and init the scene graph
    # VIEWER: associate a standard viewer for each simulation
    root = [Sofa.Core.Node() for _ in range(nb_simu)]
    simu = [root[i].addObject(Simulation(root=root[i], id_simu=i)) for i in range(nb_simu)]
    view = [Viewer(root_node=root[i]) for i in range(nb_simu)]
    for i in range(nb_simu):
        Sofa.Simulation.init(root[i])
        view[i].objects.add_scene_graph()
        view[i].launch(batch_key=batch_keys[i])

    # SOFA: run a few time steps
    # VIEWER: update the rendering
    for _ in range(300):
        for i in range(nb_simu):
            Sofa.Simulation.animate(root[i], root[i].dt.value)
            view[i].render()

    # VIEWER: close the rendering
    for i in range(nb_simu):
        view[i].shutdown()
    batch.stop()
