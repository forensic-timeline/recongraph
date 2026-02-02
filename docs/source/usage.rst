Usage
=====

Command Line Interface
----------------------

ReconGraph can be used from the command line to process Plaso CSV files or raw logs.

.. code-block:: bash

   recongraph [-h] -f FILE [-o OUTPUT] [-r RULES] [--export-csv [EXPORT_CSV]] [--export-sigma [EXPORT_SIGMA]] [--strict]

Arguments:
^^^^^^^^^^

*   ``-f``, ``--file``: Path to the input log file (**Plaso CSV** or raw TXT). **Required**.
*   ``-o``, ``--output``: Output filename for the GraphML file (default: ``reconstruction_edge_graph.graphml``).
*   ``-r``, ``--rules``: Path to the directory containing **Sigma rules** (.yml files).
*   ``--export-csv``: Export detailed event logs to a separate CSV file (``reconstruction_event_logs.csv``).
*   ``--export-sigma``: Export the full sigma-labeled DataFrame to a CSV file.
*   ``--strict``: Disable flexible matching mode (enforce strict logsource validation).

Example:
^^^^^^^^

.. code-block:: bash

   recongraph -f forensic_timeline.csv -r ./sigma_rules/ 

Library Usage
-------------

You can integrate ReconGraph into your own forensic analysis scripts using the unified facade.

.. code-block:: python
 
    from recongraph import ReconGraph
 
    # Initialize the pipeline
    pipeline = ReconGraph(
        input_file='forensic_timeline.csv', 
        rules_dir='rules/'
    )

   # Execute the pipeline with custom output names
   pipeline.run_all(
       graph_output='analysis_graph.graphml',
       csv_output='event_details.csv',
       sigma_output='labeled_source.csv'
   )

Running Tests
-------------

To ensure that the installation is correct and the code is functioning as expected, you can run the test suite provided in the ``tests/`` directory.

1.  **Install Test Dependencies**:
    Ensure you have ``pytest`` installed.

    .. code-block:: bash

       pip install pytest pandas pyyaml

2.  **Run Tests**:
    Navigate to the project root directory and execute:

    .. code-block:: bash

       pytest tests/

    You should see output indicating that all tests have passed.
