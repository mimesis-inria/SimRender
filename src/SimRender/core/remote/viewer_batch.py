from typing import List, Optional
import sys
from PySide6.QtWidgets import QWidget, QApplication, QMainWindow, QFrame, QVBoxLayout, QComboBox
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vedo import Plotter

from SimRender.core.remote.factory import Factory


class ViewerBatch(QMainWindow):

    def __init__(self, socket_ports: List[int], parent: Optional[QWidget] = None):

        # Init the Qt window
        super().__init__(parent=parent)
        self.frame = QFrame()
        self.layout = QVBoxLayout()
        self.vtk_widget = QVTKRenderWindowInteractor(parent=self.frame)

        # Create the Vedo Plotter
        self.plt = Plotter(interactive=True, qt_widget=self.vtk_widget)

        # Init the Factories
        self.factories: List[Factory] = []
        for socket_port in socket_ports:
            self.factories.append(Factory(socket_port=socket_port, plotter=self.plt))
            self.factories[-1].listen()
        self.active_factory = self.factories[0]
        if len(self.factories) > 1:
            for factory in self.factories[1:]:
                factory.active = False

        # Create source selection combobox
        source_cbox = QComboBox(parent=self.frame)
        source_cbox.addItems([f'Simulation n°{i + 1}' for i in range(len(self.factories))])
        source_cbox.currentIndexChanged.connect(self.select_cbox_source)

        # Add visual objects from the factory
        self.plt.add(self.active_factory.vedo_objects)

        # Timer callback
        self.plt.add_callback(event_name='timer', func=self.time_step, enable_picking=True)
        self.timer_id = self.plt.timer_callback(action='create', dt=1)
        self.count = 0

        self.plt.show(axes=4)
        self.layout.addWidget(self.vtk_widget)
        self.layout.addWidget(source_cbox)
        self.frame.setLayout(self.layout)
        self.setCentralWidget(self.frame)
        self.show()

    def select_cbox_source(self, idx: int) -> None:
        """
        Signal connected to the QCombobox to change the simulation source.

        :param idx: Index of the item selected in the QCombobox.
        """

        if self.factories[idx] != self.active_factory:
            self.plt.remove(self.active_factory.vedo_objects)
            self.active_factory = self.factories[idx]
            self.plt.add(self.active_factory.vedo_objects)
            self.plt.render()

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
            self.plt.render()

    def on_close_event(self):
        self.vtk_widget.close()


if __name__ == '__main__':

    app = QApplication([])

    # Executed code when the visualization process is launched
    batch_socket_ports = [int(port) for port in sys.argv[1].split(' ')]
    win = ViewerBatch(socket_ports=batch_socket_ports)
    win.showMaximized()

    app.aboutToQuit.connect(win.on_close_event)
    app.exec()
