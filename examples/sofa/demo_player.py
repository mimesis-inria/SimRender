import Sofa

from SimRender.sofa import Player
# from simulation_logo import Simulation
from simulation_caduceus import Simulation


if __name__ == '__main__':

    # SOFA: create and init the scene graph
    root = Sofa.Core.Node()
    simu = root.addObject(Simulation(root=root))
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
