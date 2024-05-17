import Sofa.Core
import Sofa.Gui
from os import listdir, remove

from simulation import Simulation


def createScene(node):
    node.addObject(Simulation(root=node))


if __name__ == '__main__':

    root = Sofa.Core.Node()
    createScene(root)
    Sofa.Simulation.init(root)

    Sofa.Gui.GUIManager.Init(program_name="main", gui_name="qglviewer")
    Sofa.Gui.GUIManager.createGUI(root, __file__)
    Sofa.Gui.GUIManager.SetDimension(1200, 900)
    Sofa.Gui.GUIManager.MainLoop(root)
    Sofa.Gui.GUIManager.closeGUI()

    for file in [f for f in listdir() if f.endswith('.ini') or f.endswith('.log')]:
        remove(file)
