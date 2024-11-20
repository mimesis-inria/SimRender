from sys import argv
from importlib import import_module
import Sofa

from SimRender.core import ViewerBatch
from SimRender.sofa import Viewer


if __name__ == '__main__':

    scene = 'caduceus'
    if len(argv) == 2 and argv[1].lower() in ['caduceus', 'logo', 'tripod']:
        scene = argv[1].lower()
    simulation = import_module(scene)

    # VIEWER: create and start the rendering
    batch = ViewerBatch()
    nb_simu = 4
    batch_keys = batch.start(nb_view=nb_simu)

    # SOFA: create and init the scene graph
    # VIEWER: associate a standard viewer for each simulation
    root = [Sofa.Core.Node() for _ in range(nb_simu)]
    simu = [r.addObject(simulation.Simulation(root=r)) for r in root]
    view = [Viewer(root_node=r) for r in root]
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
