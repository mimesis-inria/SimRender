from os.path import dirname, join
from numpy import ones, zeros
from vedo import Image

from SimRender.generic.remote.viewer import Viewer as _Viewer


class Viewer(_Viewer):

    def __init__(self, socket_port: int):
        """
        Viewer to render visual objects.

        :param socket_port: Port number of the simulation socket.
        """

        super().__init__(socket_port=socket_port, bg=join(dirname(__file__), 'back_white.png'))

        # Get the automatically created background renderer and remove image actor
        acs = self.background_renderer.GetViewProps()
        acs.InitTraversal()
        a = acs.GetNextProp()
        self.background_renderer.RemoveActor(a)

        # Create the image actors that will be used as background images
        white_bg = Image(join(dirname(__file__), 'back_white.png'))
        black_bg = Image(join(dirname(__file__), 'back_black.png'))
        self.bg_images = [white_bg, Image(ones(white_bg.shape).T * 255),
                          black_bg, Image(zeros(black_bg.shape).T)]

        # Set the background image again, zoom to fit the window
        self.background_renderer.AddActor(white_bg.actor)
        self.render()
        self.background_renderer.GetActiveCamera().Zoom(2.3)

    def switch_background(self, evt) -> None:
        """
        Keyboard callback of the viewer.

        :param evt: Event dictionary.
        """

        # React on 'b' key press
        if evt.keypress == 'b':

            # Remove the previous background image actor
            self.background_renderer.RemoveActor(self.bg_images[self.bg_id].actor)

            # Set the new background image actor
            self.bg_id = (self.bg_id + 1) % len(self.bg_images)
            self.background_renderer.AddActor(self.bg_images[self.bg_id].actor)
            self.render()


if __name__ == '__main__':

    # Executed code when the visualization process is launched
    from sys import argv
    Viewer(socket_port=int(argv[1])).launch()
