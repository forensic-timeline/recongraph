Unit Test
=========

Recongraph package comes with *unit test suite* to validate the integrity of the package.

Prerequisite
------------

It's recommended to run the unit test suite in a virtual environment whether it's conda or venv (if you have installed and activated the required virtual environment, you can skip this step).

.. code-block:: bash

   conda create -n recongraph_test python
   conda activate recongraph_test

Or using venv (recommended):

.. code-block:: bash

   python -m venv venv
   # Windows
   vocab\Scripts\activate
   # Linux/Mac
   source venv/bin/activate

After setting up the virtual environment, you need to have the following testing packages installed:

.. code-block:: bash

   pip install pytest

And you'll need to have the dependencies installed:

.. code-block:: bash

   pip install -e .

Running the Unit Test Suite
---------------------------

To run the unit test suite, run the following command:

.. code-block:: bash

   python -m pytest tests/test_recongraph.py -v

or 

.. code-block:: bash

   pytest -v

By adhering to these steps, you can successfully run tests for your project. Testing validates code correctness and detects potential issues early, contributing to software stability and reliability. Maintaining a comprehensive test suite is essential for long-term project maintainability
