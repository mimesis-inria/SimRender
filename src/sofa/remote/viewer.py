from SimRender.generic.remote.viewer import Viewer as _Viewer


class Viewer(_Viewer):

    def __init__(self, socket_port: int):

        super().__init__(socket_port=socket_port)

        self.bg_colors = ['back_white', 'w', 'back_black', 'k']

    def switch_background(self, evt) -> None:

        # React on 'b' key press
        if evt.keypress == 'b':
            print('BACK', self.background_renderer)


if __name__ == '__main__':

    # Executed code when the visualization process is launched
    from sys import argv
    Viewer(socket_port=int(argv[1]))
