====================
How to use - Generic
====================

This light tutorial reviews the whole project API to create, update and render 3D objects from numerical simulation data.


Step 1: Create a Viewer
-----------------------

Three viewer options are available depending on the requirements.
The :py:class:`Viewer<SimRender.core.local.viewer.Viewer>` and the :py:class:`Player<SimRender.core.local.player.Player>`
have exactly the same API, while the :py:class:`ViewerBatch<SimRender.core.local.viewer_batch.ViewerBatch>` is used to
gather several :py:class:`Viewers<SimRender.core.local.viewer.Viewer>` in a single display window.


Viewer / Player
"""""""""""""""

The :py:class:`Viewer<SimRender.core.local.viewer.Viewer>` is used to simply render a unique numerical simulation at
runtime.
By default, the simulation process and the rendering process are asynchronous, allowing to run the numerical simulation
as fast as possible while rendering it's current state in real time.
It is possible to synchronize these processes to ensure that every single simulation step will be rendered.

The :py:class:`Player<SimRender.core.local.player.Player>` is used to animate a unique numerical simulation.
It is very similar to the previous viewer, except that it is always synchronous and adds widgets in the display window
to play / pause the simulation process and to navigate trough time steps.
The storage of the past steps is automatically handled by the rendering process.

.. tabs::

    .. tab:: Viewer

        .. code-block:: python

            from SimRender.core import Viewer

            # Create the viewer
            viewer = Viewer(sync=False)

            # Create 3D object --> see the dedicated section bellow
            ...

            # Launch the rendering process
            viewer.launch()

            # Process any Python script
            for _ in range(N):

                # Step of simulation, update 3D object --> see the dedicated section bellow
                ...

                # Render the current state of the simulation
                viewer.render()

            # Close the rendering process
            viewer.shutdown()

    .. tab:: Player

        .. code-block:: python

            from SimRender.core import Player

            # Create the player
            player = Player(sync=False)

            # Create 3D object --> see the dedicated section bellow
            ...

            # Launch the rendering process
            player.launch()

            # Process any Python script
            for _ in range(N):

                # Step of simulation, update 3D object --> see the dedicated section bellow
                ...

                # Render the current state of the simulation
                player.render()

            # Close the rendering process
            player.shutdown()


Batch
"""""

The :py:class:`ViewerBatch<SimRender.core.local.viewer_batch.ViewerBatch>` is used when several numerical simulation
are running simultaneously and a viewer is needed for each.
Instead of launching a rendering process per simulation - resulting in multiple display windows - the viewers can be
launched as a batch to gather all the rendering sources in the same display window.
A tab menu is created to easily switch between the simulation renderings.

.. code-block:: python

    from SimRender.core import Viewer, ViewerBatch

    # Initialize the batch with the number of sources to get the batch keys
    batch = ViewerBatch()
    batch_keys = batch.start(nb_view=5)

    # Create several simulations with several viewers normally
    viewers = [Viewers(sync=False) for _ in range(5)]

    # Create 3D object for each viewer normally
    ...

    # Launch the viewers with the given batch keys
    for viewer, key in zip(viewers, batch_keys):
        viewer.launch(batch_key=key)

    # Process any Python script
    for _ in range(N):

        # Step of simulations, update 3D object normally
        ...

        # Render the current state of the simulations
        for viewer in viewers:
            viewer.render()

    # Close the viewers and stop the batch
    for viewer in viewers:
        viewer.shutdown()
    batch.stop()


Step 2: Create / Update objects
-------------------------------

The API to create and update 3D objects is exposed in the :py:class:`Viewer.objects<SimRender.core.local.factory.Objects>`
variable.
Each object has an `index` identifier (following the creation order) required by the update methods.


Create objects
""""""""""""""

Several object types can be created using :py:meth:`add_mesh<SimRender.core.local.factory.Objects.add_mesh>`,
:py:meth:`add_points<SimRender.core.local.factory.Objects.add_points>`,
:py:meth:`add_arrows<SimRender.core.local.factory.Objects.add_arrows>` or
:py:meth:`add_text<SimRender.core.local.factory.Objects.add_text>`.
Bellow are only the required variables, click on the respective button to get the detailed list of available options
for an object.


.. code-block:: python

    from SimRender.core import Viewer

    # Create the viewer
    viewer = Viewer()

    # Add a mesh to the viewer
    idx_mesh = viewer.objects.add_mesh(positions=...,
                                       cells=...,
                                       **kwargs)

    # Add a point cloud to the viewer
    idx_points = viewer.objects.add_points(positions=...,
                                           **kwargs)

    # Add a vector field to the viewer
    idx_arrows = viewer.object.add_arrows(positions=...,
                                          vectors=...,
                                          **kwargs)

    # Add a text to the viewer
    idx_text = viewer.objects.add_text(content=...)


Update objects
""""""""""""""

To update the created objects, the respective methods
(:py:meth:`update_mesh<SimRender.core.local.factory.Objects.update_mesh>`,
:py:meth:`update_points<SimRender.core.local.factory.Objects.update_points>`,
:py:meth:`update_arrows<SimRender.core.local.factory.Objects.update_arrows>` or
:py:meth:`update_text<SimRender.core.local.factory.Objects.update_text>`) require the object index that was given
following the creation order.
Bellow are only the required variables, click on the respective button to get the detailed list of available options
for an object.

.. code-block:: python

    from SimRender.core import Viewer

    # Create the viewer
    viewer = Viewer()

    # Add a mesh to the viewer
    viewer.objects.update_mesh(object_id=idx_mesh,
                               positions=...,
                               **kwargs)

    # Add a point cloud to the viewer
    viewer.objects.update_points(object_id=idx_points,
                                 positions=...,
                                 **kwargs)

    # Add a vector field to the viewer
    viewer.object.add_arrows(object_id=idx_arrows,
                             positions=...,
                             vectors=...,
                             **kwargs)

    # Add a text to the viewer
    viewer.objects.add_text(object_id=idx_text,
                            content=...)
