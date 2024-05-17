from typing import Optional
from os import listdir, remove
from os.path import join, abspath, dirname, exists, sep
from numpy import array, load, save
from vedo import Plotter, Mesh, TetMesh, Points, Text2D
from vedo.colors import get_color


class MeshSelector(Plotter):

    def __init__(self, mesh_file: str, selection_file: Optional[str] = None):
        """
        Implementation of a vedo.Plotter that allows selecting the points of a data.

        :param mesh_file: Path to the data file.
        :param selection_file: Path to an existing selection file.
        """

        Plotter.__init__(self)

        self.__mesh_file = mesh_file
        self.__selection_file = selection_file

        # Create the meshed PCD
        try:
            self.msh = Mesh(self.__mesh_file)
        except TypeError:
            self.msh = TetMesh(self.__mesh_file)
        self.msh.alpha(0.9).lw(1).c('grey')
        self.pts = Points(self.msh.vertices)
        self.pts.force_opaque().point_size(15)

        # Default selection of the PCD
        color = array(list(get_color('lightgreen')) + [1.]) * 255
        self.default_color = array([color for _ in range(self.pts.nvertices)])
        self.selection = [] if selection_file is None else load(self.__selection_file).tolist()
        self.indicator = Text2D('Nb selected points: 0', pos='bottom-left', s=0.7)

        # Cursor to access 3D coordinates of the data
        self.id_cursor = -1

        # Create mouse and keyboard callbacks
        self.add_callback('KeyPress', self.__callback_key_press)
        self.add_callback('MouseMove', self.__callback_mouse_move)
        self.add_callback('LeftButtonPress', self.__callback_left_click)
        self.add_callback('RightButtonPress', self.__callback_right_click)

    def launch(self, **kwargs):
        """
        Launch the Plotter. Specify Plotter.show() arguments in kwargs.
        """

        # Plotter legends
        self.render()
        instructions = "MOUSE CONTROL\n" \
                       "  Left-click to select a point.\n" \
                       "  Right-click to unselect a point.\n\n" \
                       "KEYBOARD CONTROL\n" \
                       "  Press 'z' to remove the last selected point.\n" \
                       "  Press 'c' to clear the selection."
        self.add(Text2D(txt=instructions, pos='top-left', s=0.6, bg='grey', c='white', alpha=0.9))
        self.add(self.indicator)

        # Add the data to the Plotter & Color the data with the existing selection
        self.add(self.msh, self.pts)
        self.__update()

        # Launch Plotter
        self.show(**kwargs).close()

    def save(self,
             file: Optional[str] = None,
             overwrite: bool = False):
        """
        Save the current selection.
        """

        # Get the file name
        if file is None and self.__selection_file is None:
            filename = 'selection.npy'
        elif file is None:
            filename = self.__selection_file.split(sep)[-1]
        else:
            filename = file.split(sep)[-1]
        filename = filename.split('.')[0]

        # Get the file dir
        if file is None and self.__selection_file is None:
            filedir = abspath(dirname(self.__mesh_file))
        elif file is None:
            filedir = abspath(dirname(self.__selection_file))
        else:
            filedir = sep.join(file.split(sep)[:-1])

        # Indexing file
        file = join(filedir, filename) if len(filedir) > 0 else filename
        if exists(file):
            if overwrite:
                remove(file)
            else:
                nb_file = len([f for f in listdir(filedir) if f[:len(filename)] == filename])
                file = join(filedir, f'{filename}_{nb_file}')

        # Save selection
        save(f'{file}.npy', array(self.selection, dtype=int))
        print(f'Saved selection at {file}.npy')

    def __update(self, color_cursor: bool = True):
        """
        Update the PCD colors.
        """

        # Add the cursor to selection if a cell is flown over
        id_cells = self.selection.copy()
        if self.id_cursor != -1 and color_cursor:
            id_cells += [self.id_cursor]
        self.indicator.text(f'Nb selected points: {len(self.selection)}')

        # RGBA color
        selection_color = list(get_color('tomato')) + [1.]
        mesh_color = self.default_color.copy()
        mesh_color[id_cells] = array(selection_color) * 255
        self.pts.pointcolors = mesh_color
        self.render()

    def __callback_key_press(self, event):
        """
        KeyPressEvent callback.
        """

        # If 'z' pressed, remove the last selected cell
        if event.keypress == 'z' and len(self.selection) > 0:
            self.selection.pop()
            self.__update()

        # If 'c' pressed, clear the selection
        elif event.keypress == 'c':
            self.selection = []
            self.__update()

    def __callback_mouse_move(self, event):
        """
        MouseMoveEvent callback.
        """

        # Mouse is on the object : color the current cell
        if isinstance(event.actor, Points):
            self.id_cursor = self.pts.closest_point(event.picked3d, return_point_id=True)
            self.__update()

        # Mouse is not on the object: uncolor the previous cell
        else:
            if self.id_cursor != -1:
                self.id_cursor = -1
                self.__update()

    def __callback_left_click(self, event):
        """
        LeftButtonPressEvent callback.
        """

        # Mouse is on the object: color the clicked point
        if isinstance(event.actor, Points):
            self.id_cursor = self.pts.closest_point(event.picked3d, return_point_id=True)
            if self.id_cursor >= 0 and self.id_cursor not in self.selection:
                self.selection.append(self.id_cursor)
                self.__update()

    def __callback_right_click(self, event):
        """
        RightButtonPressEvent callback.
        """

        # Mouse is on the object: uncolor the clicked point
        if isinstance(event.actor, Points):
            self.id_cursor = self.pts.closest_point(event.picked3d, return_point_id=True)
            if self.id_cursor >= 0 and self.id_cursor in self.selection:
                self.selection.remove(self.id_cursor)
                self.__update(color_cursor=False)


if __name__ == '__main__':

    for file in ['constraints', 'forces']:

        if not exists(f := join('data', f'{file}.npy')):
            save(f, array([]))

        plt = MeshSelector(mesh_file=join('data', 'volume.vtk'),
                           selection_file=f)
        plt.launch(title=f'{file}_selection')
        plt.save(overwrite=True)
