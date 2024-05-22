from typing import List
from vedo import Plotter

from SimRender.generic.remote.factory import Factory


class ViewerBatch(Plotter):

    def __init__(self, socket_ports: List[int], *args, **kwargs):

        # Init the Plotter as interactive
        super().__init__(interactive=True, *args, **kwargs)

        self.factories: List[Factory] = []
        for socket_port in socket_ports:
            self.factories.append(Factory(socket_port=socket_port, plotter=self))
        self.active_factory = self.factories[0]
        if len(self.factories) > 1:
            for factory in self.factories[1:]:
                factory.active = False

        # Add visual objects from the factory
        self.add(self.active_factory.vedo_objects)

        # Timer callback
        self.add_callback(event_name='timer', func=self.time_step, enable_picking=True)
        self.timer_id = self.timer_callback(action='create', dt=1)
        self.count = 0

    def launch(self):

        # Launch the visualization window
        for factory in self.factories:
            factory.listen()
        self.show(axes=4).close()

    def time_step(self, _) -> None:
        """
        Timer callback of the viewer.
        """

        # Check the number of rendered steps
        if self.count < self.active_factory.count:

            # Update the viewer counter
            self.count = self.active_factory.count

            # Update the visuals objects
            self.active_factory.update()
            self.render()


if __name__ == '__main__':

    # Executed code when the visualization process is launched
    from sys import argv
    batch_socket_ports = [int(port) for port in argv[1].split(' ')]
    ViewerBatch(socket_ports=batch_socket_ports).launch()
