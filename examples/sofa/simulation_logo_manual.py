import numpy as np

from SimRender.sofa import Viewer

from simulation_logo import Simulation as _Simulation


class Simulation(_Simulation):

    def init_view(self, viewer: Viewer):

        def disp():
            diff = self.root.logo.visual.getObject('ogl').position.array() - self.root.logo.visual.getObject('mesh').position.array()
            return np.linalg.norm(diff, axis=1)

        viewer.objects.add_sofa_mesh(positions_data=self.root.logo.visual.getObject('ogl').position,
                                     cells_data=self.root.logo.visual.getObject('ogl').triangles,
                                     alpha=0.8,
                                     line_width=0.,
                                     colormap_function=disp,
                                     colormap_range=np.array([0, 5]))

        viewer.objects.add_sofa_points(positions_data=self.root.logo.getObject('state').position,
                                       color='white')
