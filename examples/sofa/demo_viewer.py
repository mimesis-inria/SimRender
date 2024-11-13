import Sofa

from SimRender.sofa import Viewer
from simulation_logo import Simulation
# from simulation_caduceus import Simulation


if __name__ == '__main__':

    # SOFA: create and init the scene graph
    root = Sofa.Core.Node()
    simu = root.addObject(Simulation(root=root))
    Sofa.Simulation.init(root)

    # VIEWER: create the viewer, create objects and start the rendering
    viewer = Viewer(root_node=root, sync=False)
    viewer.objects.add_scene_graph(visual_models=True,
                                   behavior_models=True,
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
