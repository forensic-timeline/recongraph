Installation
============

Prerequisites
-------------

- Python 3.13 or higher
- Git

Installing via Pip (Recommended)
--------------------------------

The easiest way to install ReconGraph is directly from PyPI:

.. code-block:: bash

   pip install recongraph


Installing from Source
----------------------

Alternatively, you can install the latest development version by cloning the repository. We recommend using a virtual environment (like Anaconda or venv) to manage dependencies.

Step 1: Set up Environment (Optional but Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using Anaconda:

.. code-block:: bash

   conda create -n recongraph python
   conda activate recongraph

Or using venv (recommended):

.. code-block:: bash

   python -m venv venv
   # Windows
   vocab\Scripts\activate
   # Linux/Mac
   source venv/bin/activate

Step 2: Clone the Repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   git clone https://github.com/forensic-timeline/recongraph.git

Step 3: Install Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Navigate to the project directory and install the package in editable mode:

.. code-block:: bash

   cd recongraph
   pip install -e .

Step 4: Verify Installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   python -c "import recongraph; print(recongraph.__version__)"

If successful, this will print the version number.

Step 5: Download Sigma Rules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ReconGraph requires a collection of Sigma rules to detect events.

.. code-block:: bash

   git clone https://github.com/SigmaHQ/sigma.git sigma_rules

The `sigma_rules` directory will now contain thousands of rules (e.g., in `rules/`) that you can pass to ReconGraph using the `-r` or `--rules` argument.

