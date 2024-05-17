import Sofa

from SimRender.sofa import Viewer
from simulation import Simulation


if __name__ == '__main__':

    # SOFA: create and init the scene graph
    root = Sofa.Core.Node()
    simu = root.addObject(Simulation(root=root))
    Sofa.Simulation.init(root)

    # VIEWER: create and start the rendering
    viewer = Viewer(root_node=root, sync=True)
    viewer.objects.add_scene_graph()
    viewer.launch()

    # SOFA: run a few time steps
    # VIEWER: update the rendering
    for i in range(300):
        Sofa.Simulation.animate(root, root.dt.value)
        viewer.render()

    # VIEWER: close the rendering
    viewer.shutdown()
