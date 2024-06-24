from typing import Optional
from threading import Thread
from subprocess import run
from sys import executable

from SimRender.core.local.factory import Factory, Objects
from SimRender.core.remote import viewer


class Viewer:

    def __init__(self, sync: bool = False):
        """
        This class manages a single remote viewer to render visual objects.

        :param sync: If True, the rendering step will block the python code execution. Otherwise, the viewer will only
                     render the current status of the simulation. Use it if you want to make sure that all your
                     simulation steps are rendered.
        """

        # Create a Factory to manage visual objects and remote communication
        self.__factory = Factory(sync=sync)
        self.__subprocess: Optional[Thread] = None
        self._remote_script = viewer.__file__

    @property
    def objects(self) -> Objects:
        """
        Access to visual objects creation and update methods.
        """

        return self.__factory.objects

    def launch(self, batch_key: Optional[int] = None) -> None:
        """
        Launch the rendering window in its own python process.
        """

        def __launch(port: int):
            run([executable, self._remote_script, str(port)])

        # Init the local factory connection
        socket_port = self.__factory.init(batch_key=batch_key)

        # In non-batch mode, launch the python process for the rendering window
        if batch_key is None:
            self.__subprocess = Thread(target=__launch, args=(socket_port,), daemon=True)
            self.__subprocess.start()

        # Share data between local and remote factories
        self.__factory.connect()

    def render(self) -> None:
        """
        Render the current step of the simulation.
        """

        # Share the update command between local and remote factories
        self.__factory.update()

    def shutdown(self) -> None:
        """
        Close the rendering window.
        """

        # Close the connection between local and remote factories
        self.__factory.close()
        # Stop the rendering python process in non-batch mode
        if self.__subprocess is not None:
            self.__subprocess.join()
