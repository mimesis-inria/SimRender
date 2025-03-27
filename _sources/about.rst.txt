===============
Project Details
===============


Global Structure
----------------

The main feature of **SimRender** is to provide an interactive 3D rendering window to render a running numerical
simulation without blocking the execution of the python process.
This is achieved using two different python processes: the first one is the main process launch by the user (called
*local process* in the documentation), from which an other subprocess is launched to display the interactive 3D
rendering window (called *remote process* in the documentation).

.. figure:: /_static/img/structure.png
    :align: center


Viewer
------

As shown in the figure above, the *local Viewer* is used in the simulation process and the *remote Viewer* is dedicated
to the 3D rendering window.

The *local Viewer* is a simple user interface to launch, render and close the 3D rendering.
The *local Factory* is accessible through this interface to create and update 3D objects with simulated data.

The *remote Viewer* runs in a dedicated python `subprocess <https://docs.python.org/3/library/subprocess.html>`_.
It creates and display the 3D objects using `vedo <https://vedo.embl.es/>`_, getting data through the *remote Factory*.
A timer callback is checking for new rendering steps in the *remote Factory* so that the rendering window remains
interactive.


Factory
-------

*Factories* are used to synchronize the *Viewers* and the access shared data between processes.

The *local Factory* is a simple user interface to init and update the visualization data fields for several 3D object
types (point clouds, meshes, arrows, lines and 2D text).

Then, the *remote Factory* will access these data fields to create and update the 3D objects in the *remote Viewer*.


Memory
------

The *Memories* are the shared access to data between the *local* and the *remote* processes.
A `SharedMemory <https://docs.python.org/3/library/multiprocessing.shared_memory.html>`_ is created for each data field
and used as buffer for a `numpy array <https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html>`_.
