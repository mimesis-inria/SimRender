import Sofa

from SimRender.sofa import Viewer
from simulation_logo_manual import Simulation


if __name__ == '__main__':

    # SOFA: create and init the scene graph
    root = Sofa.Core.Node()
    simu = root.addObject(Simulation(root=root))
    Sofa.Simulation.init(root)

    # VIEWER: create the viewer, create objects and start the rendering
    viewer = Viewer(root_node=root, sync=False)
    simu.init_view(viewer=viewer)
    viewer.launch()

    # SOFA: run a few time steps
    # VIEWER: update the rendering
    while viewer.is_open:
        Sofa.Simulation.animate(root, root.dt.value)
        viewer.render()

    # VIEWER: close the rendering
    viewer.shutdown()
