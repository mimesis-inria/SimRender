from SimRender.generic.remote.viewer import Viewer


PLAY_SYMBOL = "  \u23F5  "
PAUSE_SYMBOL = "  \u23F8  "
BACKWARD_SYMBOL = " \u29CF "
FORWARD_SYMBOL = " \u29D0 "


class Player(Viewer):

    def __init__(self, socket_port: int, *args, **kwargs):
        """
        Viewer to render visual objects.

        :param socket_port: Port number of the simulation socket.
        """

        # Init the Plotter as interactive
        super().__init__(socket_port=socket_port, store_data=True, *args, **kwargs)

        # Animation widgets
        self.__animate = True
        self.__id_frame = 0
        self.btn_play = self.add_button(fnc=self._toggle,
                                        pos=[0.5, 0.05],
                                        font='Kanopus',
                                        states=[PAUSE_SYMBOL, PLAY_SYMBOL],
                                        bc=['red4', 'green3'])
        self.btn_back = self.add_button(fnc=self._backward,
                                        pos=[0.44, 0.05],
                                        font='Kanopus',
                                        states=[BACKWARD_SYMBOL],
                                        bc='green3',
                                        c='white')
        self.btn_forw = self.add_button(fnc=self._forward,
                                        pos=[0.56, 0.05],
                                        font='Kanopus',
                                        states=[FORWARD_SYMBOL],
                                        bc='green3',
                                        c='white')
        self.slider = None

        # Timer callback
        self.remove_callback(cid=self.cid)
        self.cid = self.add_callback(event_name='timer', func=self.time_step, enable_picking=False)

    def _toggle(self, obj, evt):

        self.btn_play.switch()
        self._pause() if self.__animate else self._play()

    def _play(self):

        self.__animate = True
        if self.timer_id is not None:
            self.timer_callback(action='destroy', timer_id=self.timer_id)
        self.timer_id = self.timer_callback(action='create', dt=1)
        if self.slider is not None:
            self.slider = None
            self.sliders = []

    def _pause(self):

        self.__animate = False
        if self.timer_id is not None:
            self.timer_callback(action='destroy', timer_id=self.timer_id)
            self.timer_id = None
            self.__id_frame = self.count
        if self.slider is None:
            self.slider = self.add_slider(sliderfunc=self._slider,
                                          pos=[[0.25, 0.06], [0.75, 0.06]],
                                          c='grey3',
                                          xmin=0,
                                          xmax=self.__id_frame,
                                          value=self.__id_frame,
                                          show_value=False)

    def _backward(self, obj, evt):

        if not self.__animate:
            self.__id_frame = max(0, self.__id_frame - 1)
            self._set_frame(idx=self.__id_frame)
            self.slider.value = self.__id_frame

    def _forward(self, obj, evt):

        if not self.__animate:
            self.__id_frame = min(self.__id_frame + 1, self.count)
            self._set_frame(idx=self.__id_frame)
            self.slider.value = self.__id_frame

    def _slider(self, obj, evt):

        self.__id_frame = round(obj.value)
        self._set_frame(idx=self.__id_frame)

    def _set_frame(self, idx: int):

        self.factory.set_frame(idx=idx)
        self.render()


if __name__ == '__main__':

    # Executed code when the visualization process is launched
    from sys import argv
    Player(socket_port=int(argv[1])).launch()
