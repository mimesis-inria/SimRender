from typing import Optional
from threading import Thread
import Sofa

from SimRender.core.local.viewer import Viewer as _Viewer
from SimRender.sofa.local.factory import Factory, Objects
from SimRender.sofa.remote import viewer


class Viewer(_Viewer):

    def __init__(self, root_node: Sofa.Core.Node, sync: bool = False):
        """
        This class manages a single remote viewer to render SOFA objects.

        :param root_node: Root node of the SOFA scene graph.
        :param sync: If True, the rendering step will block the python code execution. Otherwise, the viewer will only
                     render the current status of the simulation. Use it if you want to make sure that all your
                     simulation steps are rendered.
        """

        # Create a Factory to manage visual objects and remote communication
        self.__factory = Factory(root_node=root_node, sync=sync)
        self.__subprocess: Optional[Thread] = None
        self._remote_script = viewer.__file__

    @property
    def objects(self) -> Objects:
        """
        Access to visual objects creation and update methods.
        """

        return self.__factory.objects
