# ReconGraph

**Reconstruction of Forensic Timelines Using Graph Theory**

`recongraph` is a Python library designed to reconstruct and visualize system behaviors and activities based on logs from various devices, such as Windows and Linux systems. It converts Plaso log2timeline CSV files into a forensic graph timeline. By parsing sequential log data and mapping them to defined events, `recongraph` builds a `MultiDiGraph` (Multi-Directed Graph) that represents the state transitions and operational flow of the target system. This graph-based approach aids in forensic analysis, anomaly detection, and understanding complex system behaviors across diverse platforms.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Python Virtual Environment Setup](#python-virtual-environment-setup)
  - [Recongraph Package Installation](#recongraph-package-installation)
  - [Sigma Rules Setup](#sigma-rules-setup)
- [Quick Start](#quick-start)
- [Input Data Format](#input-data-format)
  - [Log File](#log-file)
  - [Event File](#event-file)
- [Output](#output)
- [Documentation](#documentation)
- [License](#license)

## Features

- **Sigma Rule-Based Pattern Matching**: Leverages standardized Sigma rules to identify and label security-relevant events in raw logs.
- **Forensic Graph Construction**: Transforms sequential log entries from Plaso (log2timeline) into a directed graph, where nodes represent detected events and edges represent temporal transitions.
- **Intelligent Log Detection**: Automatically identifies various log formats (e.g., Apache, Linux auth, Syslog) and extracts relevant metadata like HTTP methods, URIs, and status codes.
- **Weighted Behavioral Mapping**: Edges are weighted by transition frequency, helping to distinguish common flows from rare or suspicious sequences.
- **Anomaly-Focused Reconstruction**: Specifically isolates and maps behaviors based on rule severity levels (Critical, High, Medium, Low).
- **Multi-Format Export**: Exports graphs to GraphML for visualization (Gephi, Cytoscape) and detailed forensic timelines to CSV.

## Prerequisites

- Python 3.13 or higher
- Git
- Python virtual environment (venv or conda)

## Python Virtual Environment Setup

Recongraph uses several Python packages to function properly. It is recommended to install the package in a virtual environment to avoid dependency conflicts. Here is a simple example of how to create and activate a virtual environment:

  1. Anaconda or Miniconda

      ```bash
      conda create -n recongraph python
      conda activate recongraph
      ```

Or using venv (recommended):

  2. Venv

      ```bash
      python -m venv venv
      source venv/bin/activate
      ```

## Recongraph Package Installation

Recongraph package installation can be done directly from PyPI using `pip` or by cloning this repository

### Installing via Pip

 ```bash
pip install recongraph
```

Or installing by cloning this repository:

### Installing from Source

  1. **Clone the Repository**

      ```bash
      git clone https://github.com/forensic-timeline/recongraph
      ```

  2. **Install Depedencies**

      ```bash
      cd recongraph
      pip install -e .
      ```

## Sigma Rules Setup

To use the recongraph tools, sigma rules are needed to label and detect events in the log files. Sigma rules can be downloaded from https://github.com/SigmaHQ/sigma. The sigma rules are released under the [Detection Rule License (DRL) 1.1](https://github.com/SigmaHQ/Detection-Rule-License).

Using git clone, you can use the sigma rules folder:

```bash
git clone https://github.com/SigmaHQ/sigma
```

## Quick Start

  Here is a simple example of how to use `recongraph` to reconstruct a forensic timeline:

  ```bash
  recongraph -f /path/to/your/plaso-file.csv -r /path/to/your/sigma-rules-folder -o output-filename.graphml
  ```

## How to Test

To ensure that the installation is correct and the code is functioning as expected, you can run the test suite provided in the ``tests/`` directory.

1.  **Install Test Dependencies**:
    Ensure you have ``pytest`` installed.

    ```bash
    pip install pytest pandas pyyaml
    ```

2.  **Run Tests**:
    Navigate to the project root directory and execute:

    ```bash
    pytest -v
    ```

    You should see output indicating that all tests have passed.

## Input Data Format

`recongraph` processes raw log data and applies Sigma rules to identify significant security events.

### Log File (`<filename>.csv`)

A sequential log file containing system activities. The tool supports supports CSV format from Plaso (log2timeline).

### Sigma Rules (`rules/` directory)

A directory containing standardized Sigma rules in `.yml` format. These rules define the logic used to detect and label events within the logs.

Sigma rules are downloaded from https://github.com/SigmaHQ/sigma.

The content of that repository is released under the following licenses:

- The Sigma specification (https://github.com/SigmaHQ/sigma-specification) and the Sigma logo are public domain
- The rules contained in the SigmaHQ repository (https://github.com/SigmaHQ) are released under the [Detection Rule License (DRL) 1.1](https://github.com/SigmaHQ/Detection-Rule-License)

## Output

The tool generates several files to aid in analysis:

- **GraphML File** (`reconstruction_edge_graph.graphml`): A directed graph where nodes are detected events and edges represent the flow between them. Suitable for visualization in Gephi or Cytoscape.
- **Event Logs CSV** (`reconstruction_event_logs.csv`): A detailed breakdown of every log entry associated with a graph node, including timestamps and raw message content.
- **Sigma Labeled CSV** (`<filename>_sigma_labeled.csv`): The input log file augmented with matching Sigma rule titles and severity levels.

## Documentation
 
Full documentation is available at [ReadTheDocs](https://recongraph.readthedocs.io/).
 
## Licenses
 
### ReconGraph
 
This project is licensed under the [MIT License](LICENSE).
 
### Third-Party Licenses
 
This project uses **Sigma Rules** for event detection.
- The **Sigma specification** and logo are public domain.
- The **detection rules** from the [SigmaHQ repository](https://github.com/SigmaHQ/sigma) are released under the [Detection Rule License (DRL) 1.1](https://github.com/SigmaHQ/Detection-Rule-License).
