import numpy as np
import Sofa

from SimRender.sofa import Viewer


def init_viewer(root: Sofa.Core.Node, viewer: Viewer):

    def displacement():
        disp = root.logo.visual.ogl.position.array() - root.logo.visual.mesh.position.array()
        return np.linalg.norm(disp, axis=1)

    viewer.objects.add_sofa_mesh(positions_data=root.logo.visual.ogl.postion,
                                 cells_data=root.logo.visual.ogl.triangles,
                                 colormap_function=displacement,
                                 colormap_range=np.array([0., 5.0]),
                                 alpha=0.8, line_width=0.)
    viewer.objects.add_sofa_points(positions_data=root.logo.state.position,
                                   color='white')
