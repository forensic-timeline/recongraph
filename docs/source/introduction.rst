Introduction
============

Project Overview
----------------

**ReconGraph** is a specialized forensic analysis tool that bridges the gap between raw log data and behavioral visualization. It is designed to work with forensic artifacts from Windows and Linux systems, specifically focusing on the output of the **Plaso (log2timeline)** tool.

The project has evolved from an initial focus on drone telemetry to a robust framework for general system forensics. It leverages **Graph Theory** to represent complex event sequences as directed graphs, making it easier for investigators to identify patterns of attack or system failure.

Key Features
------------

*   **Sigma Rule Integration**: Automatically matches log entries against industry-standard Sigma rules to identify high-level security events.
*   **Behavioral Modeling**: Converts sequential events into a directed graph where nodes represent detected events and edges represent temporal transitions.
*   **Weighted Analysis**: Labels graph edges with transition frequencies to highlight common behavioral "highways" and rare, potentially anomalous paths.
*   **Intelligent Log Detection**: Automatically identifies various log formats within forensic timelines, such as Apache access logs, SSH authentication logs, and general System logs.
*   **Rich Visualization Support**: Exports data to GraphML format, which can be imported into tools like Gephi or Cytoscape for advanced visual exploration.

Why Use ReconGraph?
-------------------

Traditional forensic timelines can reach hundreds of thousands of entries, making manual analysis nearly impossible. ReconGraph reduces this noise by:

1.  **Filtering**: Only focusing on events flagged by Sigma rules or specified criteria.
2.  **Structuring**: Transforming a flat list of events into a logical flow of state transitions.
3.  **Visualizing**: Providing a macro view of system activity that reveals the "story" behind the logs.
