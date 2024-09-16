from vedo import Plotter, get_color

from SimRender.core.remote.factory import Factory


class Viewer(Plotter):

    def __init__(self, socket_port: int, store_data: bool = False, *args, **kwargs):
        """
        Viewer to render visual objects.

        :param socket_port: Port number of the simulation socket.
        """

        # Init the Plotter as interactive
        super().__init__(interactive=True, *args, **kwargs)

        # Create a Factory to recover the visual objects from the simulation process
        self.factory = Factory(socket_port=socket_port, plotter=self, store_data=store_data)

        # Add visual objects from the factory
        self.add(self.factory.vedo_objects)

        # Create the background switch callback
        self.add_callback(event_name='keypress', func=self.switch_background)
        self.bg_colors = ['w', 'k']
        self.bg_id = 0

        # Timer callback
        self.initialize_interactor()  # needed for windows
        self.cid = self.add_callback(event_name='timer', func=self.time_step, enable_picking=True)
        self.timer_id = self.timer_callback(action='create', dt=1)
        self.count = 0

    def launch(self):

        # Launch the visualization window
        self.factory.listen()
        self.show(axes=4).close()
        self.factory.close()

    def time_step(self, _) -> None:
        """
        Timer callback of the viewer.
        """

        # Check the number of rendered steps
        if self.count < self.factory.count:

            # Update the viewer counter
            self.count = self.factory.count

            # Update the visuals objects
            self.factory.update()
            self.render()

    def switch_background(self, evt) -> None:
        """
        Keyboard callback of the viewer.

        :param evt: Event dictionary.
        """

        # React on 'b' key press
        if evt.keypress == 'b':

            # Change the background color
            self.bg_id = (self.bg_id + 1) % len(self.bg_colors)
            self.renderer.SetBackground(get_color(self.bg_colors[self.bg_id]))
            self.render()


if __name__ == '__main__':

    # Executed code when the visualization process is launched
    from sys import argv
    Viewer(socket_port=int(argv[1])).launch()
