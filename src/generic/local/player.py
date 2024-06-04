from SimRender.generic.local.viewer import Viewer
from SimRender.generic.remote import player


class Player(Viewer):

    def __init__(self):
        """
        This class manages a single remote viewer to render visual objects.
        """

        super().__init__(sync=True)
        self._remote_script = player.__file__
