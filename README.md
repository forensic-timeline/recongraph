# ReconGraph

**Reconstruction of Forensic Timelines Using Graph Theory**

`recongraph` is a Python library designed to reconstruct and visualize system behaviors and activities based on logs from various devices, such as Windows and Linux systems. It converts Plaso log2timeline CSV files into a forensic graph timeline. By parsing sequential log data and mapping them to defined events, `recongraph` builds a `MultiDiGraph` (Multi-Directed Graph) that represents the state transitions and operational flow of the target system. This graph-based approach aids in forensic analysis, anomaly detection, and understanding complex system behaviors across diverse platforms.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Python Virtual Environment Setup](#python-virtual-environment-setup)
  - [Recongraph Package Installation](#recongraph-package-installation)
  - [Installing via Docker](#installing-via-docker)
  - [Sigma Rules Setup](#sigma-rules-setup)
- [Quick Start](#quick-start)
  - [Running with Docker](#running-with-docker)
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

Another way of installing Recongraph is by using Docker. This is the **recommended approach** if you want a fully isolated, dependency-free environment — no Python installation required on your machine.

### Installing via Docker

> **Prerequisites**: [Docker](https://docs.docker.com/get-docker/) must be installed and running.

The Docker image uses a **multi-stage build** to keep the final image small and efficient:
1. A **builder** stage installs all build tools and compiles Python dependencies.
2. A **runtime** stage copies only the compiled libraries and source code, and automatically downloads the Sigma Core rules package.

**Step 1 — Build the image** (run once from the project root directory):

```bash
docker build -t recongraph .
```

This will:
- Install all Python dependencies
- Copy the `recongraph` source code into the image
- Automatically download and bundle the **Sigma Core** rules into `/app/sigma` inside the container

**Step 2 — Prepare your data directory**

Create a local folder to hold your input log files and to receive the output files:

```bash
mkdir data
```
Place your Plaso CSV file (e.g., `forensic_timeline.csv`) inside this `data/` folder.

**Step 3 — Run the container**

Mount your `data/` folder into the container and pass your arguments:

```bash
# Linux / macOS
docker run --rm -v "$(pwd)/data:/app/data" recongraph -f forensic_timeline.csv

# Windows (Command Prompt)
docker run --rm -v "%cd%\data:/app/data" recongraph -f forensic_timeline.csv

# Windows (PowerShell)
docker run --rm -v "${PWD}\data:/app/data" recongraph -f forensic_timeline.csv
```

> The `--rm` flag removes the container automatically after it finishes.
> All output files will appear in your local `data/` folder.

**Using your own Sigma rules (optional)**

The image ships with the Sigma Core rules by default (stored at `/app/sigma`). To use a custom rules directory from your local machine, mount it as an additional volume:

```bash
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

### Running with Docker

If you are using the Docker image, place your input file in a local `data/` folder and run:

```bash
# Uses the bundled Sigma Core rules
docker run --rm -v "$(pwd)/data:/app/data" recongraph \
  -f forensic_timeline.csv \
  -o result.graphml \
  --export-csv \
  --export-sigma
```

Output files (`result.graphml`, `reconstruction_event_logs.csv`, etc.) will be written back to your local `data/` folder.

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
