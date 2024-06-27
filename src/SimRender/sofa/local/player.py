import Sofa

from SimRender.sofa.local.viewer import Viewer
from SimRender.sofa.remote import player


class Player(Viewer):

    def __init__(self, root_node: Sofa.Core.Node):
        """
        This class manages a single remote viewer to render visual objects.
        """

        super().__init__(root_node=root_node, sync=True)
        self._remote_script = player.__file__
