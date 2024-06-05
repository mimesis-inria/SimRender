from SimRender.generic.remote.player import Player as _Player
from SimRender.sofa.remote.viewer import Viewer


class Player(Viewer, _Player):

    def __init__(self, socket_port: int):

        super().__init__(socket_port=socket_port)


if __name__ == '__main__':

    # Executed code when the visualization process is launched
    from sys import argv
    Player(socket_port=int(argv[1])).launch()
