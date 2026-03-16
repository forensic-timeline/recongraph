Installation
============

Prerequisites
-------------

- Python 3.13 or higher
- Git
- Docker (only if using the Docker-based installation)

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

The ``sigma_rules`` directory will now contain thousands of rules (e.g., in ``rules/``) that you can pass to ReconGraph using the ``-r`` or ``--rules`` argument.


Installing via Docker
---------------------

Using Docker is the easiest way to run ReconGraph in a fully isolated environment — no Python installation is required on your host machine.

.. note::

   Make sure `Docker <https://docs.docker.com/get-docker/>`_ is installed and running before proceeding.

How the image works
^^^^^^^^^^^^^^^^^^^

The Dockerfile uses a **multi-stage build** strategy:

1. A **builder** image installs system build tools (``gcc``, ``libxml2``, ``libxslt``) and compiles all Python dependencies.
2. A lightweight **runtime** image copies only the compiled libraries and source code, keeping the final image small.
3. During the build, the **Sigma Core** rules package is automatically downloaded from GitHub and stored at ``/app/sigma`` inside the container, so no manual rules download is needed.

Step 1: Build the image
^^^^^^^^^^^^^^^^^^^^^^^

Run the following command from the project root directory (where the ``Dockerfile`` is located):

.. code-block:: bash

   docker build -t recongraph .

This command tags the resulting image as ``recongraph``.

Step 2: Prepare your data directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a local folder to hold your input log file(s). Output files will also be written here:

.. code-block:: bash

   mkdir data

Place your Plaso CSV file (e.g., ``forensic_timeline.csv``) inside this ``data/`` folder.

Step 3: Run the container
^^^^^^^^^^^^^^^^^^^^^^^^^

Mount your ``data/`` folder into the container with the ``-v`` flag:

.. code-block:: bash

   # Linux / macOS
   docker run --rm -v "$(pwd)/data:/app/data" recongraph -f forensic_timeline.csv

   # Windows (Command Prompt)
   docker run --rm -v "%cd%\data:/app/data" recongraph -f forensic_timeline.csv

   # Windows (PowerShell)
   docker run --rm -v "${PWD}\data:/app/data" recongraph -f forensic_timeline.csv

.. note::

   - ``--rm`` removes the container automatically after it finishes.
   - The ``-v`` flag maps your local ``data/`` folder to ``/app/data`` inside the container, which is the working directory.
   - All generated output files will appear in your local ``data/`` folder.

Step 4: Use custom Sigma rules (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The image ships with the bundled Sigma Core rules at ``/app/sigma``. To override this with your own rules directory, mount an additional volume and specify the path with ``-r``:

.. code-block:: bash

   # Linux / macOS
   docker run --rm \
     -v "$(pwd)/data:/app/data" \
     -v "$(pwd)/my_sigma_rules:/app/custom_sigma" \
     recongraph -f forensic_timeline.csv -r /app/custom_sigma

   # Windows (PowerShell)
   docker run --rm `
     -v "${PWD}\data:/app/data" `
     -v "${PWD}\my_sigma_rules:/app/custom_sigma" `
     recongraph -f forensic_timeline.csv -r /app/custom_sigma
