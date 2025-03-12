from sys import argv
from importlib import import_module
import Sofa, Sofa.Gui


def createScene(node: Sofa.Core.Node):

    scene = 'caduceus'
    if len(argv) == 2 and argv[1].lower() in ['caduceus', 'logo', 'tripod']:
        scene = argv[1].lower()
    simulation = import_module(scene)
    node.addObject(simulation.Simulation(node))


if __name__ == '__main__':

    root = Sofa.Core.Node('root')
    createScene(root)
    Sofa.Simulation.initRoot(root)

    Sofa.Gui.GUIManager.Init(program_name="main", gui_name="qglviewer")
    Sofa.Gui.GUIManager.createGUI(root, __file__)
    Sofa.Gui.GUIManager.SetDimension(1200, 900)
    Sofa.Gui.GUIManager.MainLoop(root)
    Sofa.Gui.GUIManager.closeGUI()
