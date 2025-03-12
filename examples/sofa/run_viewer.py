from sys import argv
from importlib import import_module
import Sofa

from SimRender.sofa import Viewer


if __name__ == '__main__':

    scene = 'caduceus'
    if len(argv) == 2 and argv[1].lower() in ['caduceus', 'logo', 'tripod']:
        scene = argv[1].lower()
    simulation = import_module(scene)

    # SOFA: create and init the scene graph
    root = Sofa.Core.Node()
    root.addObject(simulation.Simulation(root))
    Sofa.Simulation.init(root)

    # VIEWER: create the viewer, create objects and start the rendering
    viewer = Viewer(root_node=root, sync=False)
    viewer.objects.add_scene_graph(visual_models=True,
                                   behavior_models=scene != 'tripod',
                                   force_fields=True,
                                   collision_models=False)
    viewer.launch()

    # SOFA: run a few time steps
    # VIEWER: update the rendering
    while viewer.is_open:
        Sofa.Simulation.animate(root, root.dt.value)
        viewer.render()

    # VIEWER: close the rendering
    viewer.shutdown()
