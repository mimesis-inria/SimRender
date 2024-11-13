=======
Install
=======

Requirements
------------

**SimRender** has the following dependencies:

.. table::
    :widths: 30 30 50

    +-----------------------+--------------+----------------------------------------------------+
    | **Dependency**        | **Type**     | **Install**                                        |
    +=======================+==============+====================================================+
    | :Numpy:`Numpy <>`     | **Required** | :guilabel:`pip install numpy`                      |
    +-----------------------+--------------+----------------------------------------------------+
    | :Vedo:`Vedo <>`       | **Required** | :guilabel:`pip install vedo`                       |
    +-----------------------+--------------+----------------------------------------------------+
    | :PySide:`PySide6 <>`  | **Required** | :guilabel:`pip install pyside6`                    |
    +-----------------------+--------------+----------------------------------------------------+
    | :SP3:`SofaPython3 <>` | Optional     | :SP3:`Follow instructions <menu/Compilation.html>` |
    +-----------------------+--------------+----------------------------------------------------+

.. note::
    The :SOFA:`SOFA <>` dependency is not mandatory if you do not use :SOFA:`SOFA <>` in your simulations.
    **SimRender** is compatible with any numerical simulation written in Python, only the additional features for
    :SOFA:`SOFA <>` will not be usable.


Install
-------

Install with *pip*
""""""""""""""""""

**SimRender** can be easily installed with :guilabel:`pip` for users:

.. code-block:: bash

    $ pip install git+https://github.com/mimesis-inria/SimRender.git

Then, you should be able to run:

.. code-block:: python

    import SimRender

Install from sources
""""""""""""""""""""

**SimRender** can also be installed from sources for developers:

.. code-block:: bash

    git clone https://github.com/mimesis-inria/SimRender.git
    cd SimRender
    pip install -e .

You should be able to run:

.. code-block:: python

    import SimRender
