ReconGraph documentation
========================

**ReconGraph** is a Python library designed to reconstruct and visualize system behaviors and activities based on forensic logs. It specialized in converting **Plaso (log2timeline)** CSV files into a structured forensic graph timeline.

By parsing sequential log data and mapping them to events identified via **Sigma rules**, `recongraph` builds a `MultiDiGraph` (Multi-Directed Graph) that represents state transitions and operational flow. This graph-based approach aids forensic investigators in anomaly detection, behavioral analysis, and understanding complex system events across diverse platforms like Windows and Linux.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   installation
   usage
   data_format
   api
   license
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

