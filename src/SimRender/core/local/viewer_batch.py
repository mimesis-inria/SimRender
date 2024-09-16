from typing import Optional, List
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from subprocess import run
from sys import executable
from os.path import dirname, join


class ViewerBatch:

    def __init__(self):
        """
        This class manages a single remote viewer to render visual objects from several simulation sources.
        """

        self.__subprocess: Optional[Thread] = None

    def start(self, nb_view: int) -> List[int]:
        """
        Launch the rendering window in its own python process.

        :param nb_view: Number of simulations sources to render.
        """

        def __launch(ports: List[int]):
            run([executable, join(dirname(dirname(__file__)), 'remote', 'viewer_batch.py'),
                 ' '.join([str(port) for port in ports])])

        available_socket_ports = []
        for _ in range(nb_view):
            temp_socket = socket(AF_INET, SOCK_STREAM)
            temp_socket.bind(('localhost', 0))
            available_socket_ports.append(temp_socket.getsockname()[1])
            temp_socket.close()

        self.__subprocess = Thread(target=__launch, args=(available_socket_ports,))
        self.__subprocess.start()

        return available_socket_ports

    def stop(self) -> None:
        """
        Close the rendering window.
        """

        self.__subprocess.join()
