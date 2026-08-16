Examples & Sample Datasets
==========================

This page walks through the sample datasets shipped in the ``dataset/`` folder of
the repository and shows how to reproduce each one end to end — from a Plaso CSV,
to a GraphML graph, to the exported SVG and JSON from the visualizer.

Each sample lives in its own folder and contains four files:

.. code-block:: text

   dataset/<n>/
   ├── <name>.csv       # source Plaso (log2timeline) timeline
   ├── <name>.graphml   # ReconGraph output (nodes = events, edges = transitions)
   ├── <name>.svg       # graph exported from the visualizer
   └── <name>.json      # graph exported from the visualizer

The Sample Datasets
-------------------

.. list-table::
   :header-rows: 1
   :widths: 6 30 12 10 10

   * - #
     - Source (scenario / behavior)
     - File
     - Nodes
     - Edges
   * - 1
     - Credential access — failed logins
     - ``dataset/1/failed-login``
     - 20
     - 110
   * - 2
     - Defense evasion — Windows Firewall disabled (EVTX)
     - ``dataset/2/windows-firewall-disabled-evtx``
     - 24
     - 109
   * - 3
     - Anti-forensics — system time change (Event ID 4616)
     - ``dataset/3/4616-with-regex``
     - 29
     - 124

Prerequisites
-------------

* ReconGraph installed — see :doc:`installation`.
* A Sigma rules directory — see :doc:`data_format`. In the examples below the
  rules live at ``/path/to/sigma``; substitute your own path.

Reproducing a Sample
--------------------

The steps are identical for every sample; only the input and output filenames
change. Using sample 1 as the example:

Step 1 — Generate the GraphML
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run ReconGraph on the source CSV, pointing ``-r`` at your Sigma rules directory:

.. code-block:: bash

   recongraph \
     -f dataset/1/failed-login.csv \
     -r /path/to/sigma \
     -o dataset/1/failed-login.graphml

This writes ``failed-login.graphml`` — a directed graph where each node is a
detected event (labeled with its Sigma rule and severity) and each edge is a
weighted temporal transition.

Step 2 — Open the visualizer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open ``recongraph/visualizer.html`` in any modern web browser (no server or build
step required). Click **Load GraphML** (or drag the file onto the page) and select
the ``.graphml`` from Step 1. The graph renders with severity-colored nodes,
layout controls, a severity filter, and a node inspector.

Step 3 — Export SVG and JSON
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With the graph loaded, use the header buttons:

* **Export SVG** — saves a standalone vector image of the current graph.
* **Export JSON** — saves a simplified ``{ nodes, edges }`` structure
  (id, label, level, count, timestamp, and edge weights).

Save them next to the GraphML as ``failed-login.svg`` and ``failed-login.json``.

Repeat for the other samples by swapping the filenames, e.g. for sample 2:

.. code-block:: bash

   recongraph \
     -f dataset/2/windows-firewall-disabled-evtx.csv \
     -r /path/to/sigma \
     -o dataset/2/windows-firewall-disabled-evtx.graphml

and for sample 3:

.. code-block:: bash

   recongraph \
     -f dataset/3/4616-with-regex.csv \
     -r /path/to/sigma \
     -o dataset/3/4616-with-regex.graphml

Advanced: Strict Mode
---------------------

By default ReconGraph runs in **flexible** matching mode, which searches broadly
across log fields. The ``--strict`` flag enables logsource validation, which only
applies rules whose logsource matches the detected log type. Compare the two on
sample 2:

.. code-block:: bash

   # Strict variant
   recongraph \
     -f dataset/2/windows-firewall-disabled-evtx.csv \
     -r /path/to/sigma \
     --strict \
     -o dataset/2/windows-firewall-disabled-evtx-strict.graphml

The result is a much smaller, less tangled graph:

.. list-table::
   :header-rows: 1
   :widths: 20 15 15

   * - Mode
     - Nodes
     - Edges
   * - Flexible (default)
     - 24
     - 109
   * - Strict (``--strict``)
     - 4
     - 12

.. note::

   Strict mode is a **graph-size / complexity reducer**, not an accuracy fix.
   On Plaso *super-timelines* (which interleave NTFS USN journal, Prefetch,
   registry, and event-log rows) both modes still produce false positives — a
   generic rule can match unrelated filesystem-journal text. Strict mode mainly
   reduces the *variety* of matched rules (via logsource gating); it does not
   eliminate the noise. Treat the labeled events as leads to verify, not
   conclusions. See ``dataset/2/windows-firewall-disabled-evtx-strict.graphml``
   for the strict output.

Interpreting the Graph
----------------------

* **Node size** scales with how many log lines matched that event.
* **Node color** encodes Sigma severity (critical, high, medium, low,
  informational).
* **Edge thickness / weight** encodes how often that transition occurred.
* A large **self-loop** or a node connected to almost everything usually
  indicates an over-matching (frequently false-positive) rule rather than a
  meaningful attacker pivot — a signal to narrow your rule set or pre-filter the
  input timeline.
