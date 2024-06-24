===============
Project Details
===============


Global Structure
----------------

The main feature of **SimRender** is to provide an interactive 3D rendering window without blocking the execution of
the python code.
This is achieved using two different processes: the first one is the main process launch by the user (called *local
process* in the documentation), from which an other process is launched automatically to display the interactive 3D
rendering (called *remote process* in the documentation).

.. figure:: /_static/img/structure.png
    :align: center


Viewer
------

As shown in the figure above, the *local Viewer* is used in the simulation process and the *remote Viewer* is dedicated
to the 3D rendering window.

The *local Viewer* is a simple user interface to launch, update and close the 3D rendering.
The *local Factory* is accessible through this object to provide the visualization data.

The *remote Viewer* runs in a dedicated python process, launched with the
`subprocess <https://docs.python.org/3/library/subprocess.html>`_ module.
It creates and display the 3D rendering window designed with
`Vedo <https://vedo.embl.es/>`_, accessing objects data through the *remote Factory*.
A timer callback is checking for new rendering steps in the *remote Factory* so that the rendering window remains
interactive.


Factory
-------

*Factories* are used to synchronize the *Viewers* and the shared data access.

The *local Factory* has methods to easily initialize and update the visualization data for several 3D object types
(point clouds, meshes, arrows).

Then, the *remote Factory* will recover these data to create and update the 3D objects in the *remote Viewer*.


Memory
------

The *Memories* are the bridge to communicate data between the *local* and the *remote* processes.
To achieve this, a
`multiprocessing.SharedMemory <https://docs.python.org/3/library/multiprocessing.shared_memory.html>`_ is created for
each visualization data and used as buffer for a
`numpy.ndarray <https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html>`_.
