from typing import Optional
from PySide6.QtWidgets import QWidget, QApplication, QMainWindow, QFrame, QVBoxLayout
from PySide6.QtGui import QAction
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from SimRender.core.remote.player import Player as _Player
from SimRender.sofa.remote.viewer import Viewer


class Player(Viewer, _Player):

    def __init__(self, socket_port: int, *args, **kwargs):

        super().__init__(socket_port=socket_port, *args, **kwargs)


class PlayerQt(QMainWindow):

    def __init__(self, socket_port: int, parent: Optional[QWidget] = None):

        # Init the Qt window
        super().__init__(parent=parent)
        self.frame = QFrame()
        self.layout = QVBoxLayout()
        self.vtk_widget = QVTKRenderWindowInteractor(parent=self.frame)

        # Create the Player
        self.plt = Player(socket_port=socket_port, qt_widget=self.vtk_widget)

        # Add the menu

        # Display
        self.plt.launch()
        self.layout.addWidget(self.vtk_widget)
        self.frame.setLayout(self.layout)
        self.setCentralWidget(self.frame)
        self.show()

    def display_models(self):
        pass

    def on_close_event(self):
        self.vtk_widget.close()


if __name__ == '__main__':

    # Executed code when the visualization process is launched
    from sys import argv
    # Player(socket_port=int(argv[1])).launch()

    app = QApplication([])
    win = PlayerQt(socket_port=int(argv[1]))
    app.aboutToQuit.connect(win.on_close_event())
    app.exec()
