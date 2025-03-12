from sys import argv
from importlib import import_module
import Sofa

from SimRender.sofa import Player


if __name__ == '__main__':

    scene = 'caduceus'
    if len(argv) == 2 and argv[1].lower() in ['caduceus', 'logo', 'tripod']:
        scene = argv[1].lower()
    simulation = import_module(scene)

    # SOFA: create and init the scene graph
    root = Sofa.Core.Node()
    simu = root.addObject(simulation.Simulation(root))
    Sofa.Simulation.init(root)

    # VIEWER: create the player, create objects and start the rendering
    player = Player(root_node=root)
    player.objects.add_scene_graph()
    player.launch()

    # SOFA: run a few time steps
    # VIEWER: update the rendering
    while player.is_open:
        Sofa.Simulation.animate(root, root.dt.value)
        player.render()

    # VIEWER: close the rendering
    player.shutdown()
