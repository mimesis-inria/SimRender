===============
Getting started
===============

This light tutorial reviews the whole project API to create, update and render 3D objects from numerical simulation data.


Create a Viewer
---------------

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

.. note::
    Press :guilabel:`b` key to switch between backgrounds !

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


Create and update 3D objects
----------------------------

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

    # Update a mesh in the viewer
    viewer.objects.update_mesh(object_id=idx_mesh,
                               positions=...,
                               **kwargs)

    # Update a point cloud in the viewer
    viewer.objects.update_points(object_id=idx_points,
                                 positions=...,
                                 **kwargs)

    # Update a vector in the viewer
    viewer.object.update_arrows(object_id=idx_arrows,
                                positions=...,
                                vectors=...,
                                **kwargs)

    # Add a text to the viewer
    viewer.objects.update_text(object_id=idx_text,
                               content=...)


Using SOFA simulations
----------------------

Creating and updating 3D objects can be automated for SOFA numerical simulation:

* either with automated updates of manually defined 3D objects;
* either with automated creation and updates of 3D objects for some components detected in the scene graph.


Automated updates
"""""""""""""""""

A dedicated :py:class:`Viewer<SimRender.sofa.local.viewer.Viewer>` must be used to access the API to create 3D objects
for SOFA.
The methods to create and update objects is still available using the
:py:class:`viewer.objects<SimRender.sofa.local.factory.Objects>`, with new methods called
:guilabel:`viewer.objects.add_sofa_<object>()`.
These *create* methods do no longer require a static value for each data fields, but a SOFA Data that the *Factory* will
access at each call to the :guilabel:`viewer.render()` method to automatically update the 3D object.

.. code-block:: python

    # This is also working with the BatchViewer and the Player
    from SimRender.sofa import Viewer
    import Sofa


    def create_scene(root: Sofa.Core.Node):
        """
        Define a SOFA scene graph
        """

        root.addObject('RequiredPlugin', ...)

        root.addObject('DefaultAnimationLoop')
        root.addObject('CollisionPipeline', ...)
        root.addObject('BruteForceBroadPhase', ...)
        root.addObject('BVHNarrowPhase', ...)
        root.addObject('DefaultContactManager', ...)

        root.addObject('MeshOBJLoader', ...)

        mecha = root.addChild('mecha')
        mecha.addObject('EulerImplicitSolver', ...)
        mecha.addObject('CGLinearSolver', ...)
        mecha.addObject('TetrahedronSetTopologyContainer', ...)
        mecha.addObject('TetrahedronSetGeometryAlgorithms', ...)
        mecha.addObject('MechanicalObject', ...)
        mecha.addObject('DiagonalMass', ...)
        mecha.addObject('TetrahedronFEMForceField', ...)
        mecha.addObject('FixedConstraint', ...)

        visu = mecha.addChild('visu')
        visu.addObject('OglModel', ...)
        visu.addObject('BarycentricMapping', ...)


    if __name__ == '__main__':

        # SOFA: create and init the scene graph
        root = Sofa.Core.Node('root')
        create_scene(root)
        Sofa.Simulation.init(root)

        # SimRender: create the viewer, create objects and start the rendering
        viewer = Viewer(root_node=root)
        viewer.objects.add_sofa_mesh(positions_data=root.mecha.visu.ogl.position,
                                     cells_data=root.mecha.visu.ogl.triangles,
                                     **kwargs)
        viewer.objects.add_sofa_points(positions_data=root.mecha.mo.position,
                                       **kwargs)
        viewer.launch()

        # SOFA: run the time steps
        while viewer.is_open:
            Sofa.Simulation.animate(root, root.dt.value)
            # SimRender: update the rendering view, 3D objects are automatically updated
            viewer.render()

        # SimRender: close the rendering
        viewer.shutdown()


Automated scene graph detection
"""""""""""""""""""""""""""""""

The :py:class:`viewer.objects<SimRender.sofa.local.factory.Objects>` also has an additional method to automatically
create and update some SOFA components: :py:meth:`update_mesh<SimRender.sofa.local.factory.Objects.add_scene_graph>`.
The scene graph is explored to detect component types in a pre-defined list (soon extended):

    +------------------------+-----------------------------------------------------------------+
    | **Models**             | **Components**                                                  |
    +========================+=================================================================+
    | :guilabel:`Visual`     | OglModel                                                        |
    +------------------------+-----------------------------------------------------------------+
    | :guilabel:`Behavior`   | FixedConstraint, MechanicalObject                               |
    +------------------------+-----------------------------------------------------------------+
    | :guilabel:`ForceField` | ConstantForceField                                              |
    +------------------------+-----------------------------------------------------------------+
    | :guilabel:`Collision`  | PointCollisionModel, LineCollisionModel, TriangleCollisionModel |
    +------------------------+-----------------------------------------------------------------+

Then, 3D objects are automatically created like in the section above to be automatically updated then.

.. code-block:: python

    # This is also working with the BatchViewer and the Player
    from SimRender.sofa import Viewer
    import Sofa


    def create_scene(root: Sofa.Core.Node):
        ...


    if __name__ == '__main__':

        # SOFA: create and init the scene graph
        root = Sofa.Core.Node('root')
        create_scene(root)
        Sofa.Simulation.init(root)

        # SimRender: create the viewer, explore scene graph and start the rendering
        viewer = Viewer(root_node=root)
        viewer.objects.add_scene_graph(visual_models=True,
                                       behavior_models=True,
                                       force_fields=True,
                                       collision_models=True)
        viewer.launch()

        # SOFA: run the time steps
        while viewer.is_open:
            Sofa.Simulation.animate(root, root.dt.value)
            # SimRender: update the rendering view
            viewer.render()

        # SimRender: close the rendering
        viewer.shutdown()
