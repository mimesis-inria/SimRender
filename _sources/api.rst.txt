===
API
===


Core
----


.. autoclass:: SimRender.core.local.viewer.Viewer
    :special-members: __init__
    :members: launch, render, shutdown

.. autoclass:: SimRender.core.local.player.Player
    :special-members: __init__
    :members: launch, render, shutdown

.. autoclass:: SimRender.core.local.viewer_batch.ViewerBatch
    :members: start, stop

.. autoclass:: SimRender.core.local.factory.Objects
    :members: add_mesh, update_mesh, add_points, update_points, add_arrows, update_arrows, add_lines, update_lines, add_text, update_text


SOFA
----

.. autoclass:: SimRender.sofa.local.viewer.Viewer
    :special-members: __init__
    :members: launch, render, shutdown

.. autoclass:: SimRender.sofa.local.factory.Objects
    :members: add_sofa_mesh, add_sofa_points, add_sofa_arrows, add_scene_graph
