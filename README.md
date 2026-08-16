# ReconGraph

**Reconstruction of Forensic Timelines Using Graph Theory**

`recongraph` is a Python library and CLI that reconstructs and visualizes system
behavior from logs of various devices (e.g. Windows and Linux). It converts Plaso
`log2timeline` CSV files into a forensic graph timeline: by parsing sequential log
data and matching it against **Sigma rules**, `recongraph` builds a `MultiDiGraph`
(Multi-Directed Graph) representing the state transitions and operational flow of
the target system. This aids forensic analysis, anomaly detection, and
understanding complex system behavior across platforms.

This tool is based on the paper:
[Forensic Event Reconstruction for Drones](https://ieeexplore.ieee.org/document/9702864).

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Set Up a Virtual Environment](#set-up-a-virtual-environment)
  - [Install from PyPI](#install-from-pypi)
  - [Install from Source](#install-from-source)
  - [Install via Docker](#install-via-docker)
- [Sigma Rules Setup](#sigma-rules-setup)
- [Quick Start](#quick-start)
  - [Run Locally](#run-locally)
  - [Run with Docker](#run-with-docker)
- [Command-Line Options](#command-line-options)
- [Input Data Format](#input-data-format)
- [Output](#output)
- [Visualizing the Graph](#visualizing-the-graph)
- [Examples](#examples)
- [How to Test](#how-to-test)
- [Documentation](#documentation)
- [Licenses](#licenses)

## Features

- **Sigma Rule-Based Pattern Matching**: Leverages standardized Sigma rules to identify and label security-relevant events in raw logs.
- **Forensic Graph Construction**: Transforms sequential log entries from Plaso (log2timeline) into a directed graph, where nodes represent detected events and edges represent temporal transitions.
- **Intelligent Log Detection**: Automatically identifies various log formats (e.g., Apache, Linux auth, Syslog) and extracts relevant metadata like HTTP methods, URIs, and status codes.
- **Weighted Behavioral Mapping**: Edges are weighted by transition frequency, helping to distinguish common flows from rare or suspicious sequences.
- **Anomaly-Focused Reconstruction**: Specifically isolates and maps behaviors based on rule severity levels (Critical, High, Medium, Low).
- **Multi-Format Export**: Exports graphs to GraphML for visualization (Gephi, Cytoscape, or the bundled web visualizer) and detailed forensic timelines to CSV.

## Prerequisites

- **Python 3.13 or higher**
- **Git**
- **pip** (and, recommended, a virtual environment via `venv` or `conda`)
- **Sigma rules** — see [Sigma Rules Setup](#sigma-rules-setup)

> Prefer a zero-setup, dependency-free environment? Skip straight to
> [Install via Docker](#install-via-docker) — no local Python required.

## Installation

There are three ways to install `recongraph`: from **PyPI**, from **source**, or
via **Docker**. For the PyPI and source methods, set up a virtual environment
first.

### Set Up a Virtual Environment

Using `venv` (recommended):

```bash
python -m venv venv

# Activate it:
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows (PowerShell / CMD)
```

Or using Anaconda / Miniconda:

```bash
conda create -n recongraph python=3.13
conda activate recongraph
```

### Install from PyPI

```bash
pip install recongraph
```

### Install from Source

1. **Clone the repository**

   ```bash
   git clone https://github.com/forensic-timeline/recongraph
   ```

2. **Install the package (editable mode)**

   ```bash
   cd recongraph
   pip install -e .
   ```

### Install via Docker

This is the **recommended approach** for a fully isolated, dependency-free
environment — no Python installation required on your machine.

> **Prerequisite**: [Docker](https://docs.docker.com/get-docker/) must be installed and running.

The image uses a **multi-stage build** to keep the final image small:

1. A **builder** stage installs build tools and compiles the Python dependencies.
2. A **runtime** stage copies only the compiled libraries and source code, and
   automatically downloads the **Sigma Core** rules into `/app/sigma`.

**Step 1 — Build the image** (run once, from the project root):

```bash
docker build -t recongraph .
```

**Step 2 — Prepare a data directory** for your input logs and output files:

```bash
mkdir data
```

Place your Plaso CSV file (e.g., `forensic_timeline.csv`) inside `data/`.

You are now ready to run the container — see [Run with Docker](#run-with-docker).

## Sigma Rules Setup

`recongraph` uses Sigma rules to label and detect events. **You must provide a
rules directory** — without one, no events are matched and the resulting graph is
empty. The rules directory is resolved in this order:

1. the `-r/--rules` command-line option, if given; otherwise
2. the `SIGMA_RULES_PATH` environment variable, if set.

Download the official rules from [SigmaHQ/sigma](https://github.com/SigmaHQ/sigma):

```bash
git clone https://github.com/SigmaHQ/sigma
```

You can then point `-r` at the cloned `sigma/rules` directory (or any folder of
`.yml` rules).

> **Docker note**: the Docker image already bundles the Sigma Core rules at
> `/app/sigma` and sets `SIGMA_RULES_PATH=/app/sigma`, so they are used
> automatically — no `-r` needed. Pass `-r` only to override with your own rules.

Sigma rules are released under the
[Detection Rule License (DRL) 1.1](https://github.com/SigmaHQ/Detection-Rule-License).

## Quick Start

### Run Locally

```bash
recongraph -f /path/to/plaso-file.csv \
           -r /path/to/sigma/rules \
           -o reconstruction_edge_graph.graphml
```

Add `--export-csv` and `--export-sigma` to also produce the detailed event-log
CSV and the Sigma-labeled CSV:

```bash
recongraph -f forensic_timeline.csv \
           -r ./sigma/rules \
           -o result.graphml \
           --export-csv \
           --export-sigma
```

### Run with Docker

Mount your local `data/` folder into the container and pass your arguments. The
bundled Sigma Core rules are used automatically (via `SIGMA_RULES_PATH`), so no
`-r` is required:

```bash
# Linux / macOS
docker run --rm -v "$(pwd)/data:/app/data" recongraph \
  -f forensic_timeline.csv \
  -o result.graphml \
  --export-csv \
  --export-sigma

# Windows (PowerShell)
docker run --rm -v "${PWD}\data:/app/data" recongraph `
  -f forensic_timeline.csv `
  -o result.graphml
```

To use **your own** rules instead, mount them as an extra volume and point `-r`
at the mount:

```bash
docker run --rm \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/my_sigma_rules:/app/custom_sigma" \
  recongraph -f forensic_timeline.csv -r /app/custom_sigma
```

Alternatively, use **Docker Compose** (mounts `./data` automatically):

```bash
docker compose run --rm recongraph -f forensic_timeline.csv -o result.graphml
```

> `--rm` removes the container after it finishes. All output files are written
> back to your local `data/` folder.

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-f`, `--file` | Path to the input file (CSV or TXT). **Required.** | — |
| `-r`, `--rules` | Path to the Sigma rules directory. | `$SIGMA_RULES_PATH` if set, else none |
| `-o`, `--output` | Output filename for the GraphML file. | `reconstruction_edge_graph.graphml` |
| `--export-csv` | Also export detailed event logs to a CSV file. | `reconstruction_event_logs.csv` |
| `--export-sigma` | Also export the Sigma-labeled DataFrame to a CSV file. | `<input>_sigma_labeled.csv` |
| `--strict` | Disable flexible matching (enable strict logsource validation). | flexible mode |

## Input Data Format

### Log File (`<filename>.csv`)

A sequential log file of system activities. `recongraph` supports the CSV format
produced by Plaso (`log2timeline`).

### Sigma Rules (rules directory)

A directory of standardized Sigma rules in `.yml` format that define the detection
logic used to label events. See [Sigma Rules Setup](#sigma-rules-setup).

## Output

The tool generates the following files:

- **GraphML File** (`reconstruction_edge_graph.graphml`): A directed graph where
  nodes are detected events and edges represent the flow between them. Suitable
  for the bundled visualizer, Gephi, or Cytoscape.
- **Event Logs CSV** (`reconstruction_event_logs.csv`, with `--export-csv`): A
  detailed breakdown of every log entry associated with a graph node, including
  timestamps and raw message content.
- **Sigma Labeled CSV** (`<filename>_sigma_labeled.csv`, with `--export-sigma`):
  The input log file augmented with matching Sigma rule titles and severity levels.

## Visualizing the Graph

The repository ships with a standalone, single-file web visualizer at
[`recongraph/visualizer.html`](recongraph/visualizer.html). It requires no build
step or server:

1. Open `recongraph/visualizer.html` in a web browser.
2. Click **Load GraphML** (or drag the file onto the page) and select your
   `reconstruction_edge_graph.graphml`.

The visualizer provides force-directed, circular, hierarchical, and radial
layouts, severity filtering, node search, a node inspector, and SVG/JSON export.

## Examples

The [`dataset/`](dataset/) folder contains ready-made sample datasets, each with
its source Plaso CSV, the resulting GraphML, and the SVG/JSON exported from the
visualizer:

| # | Scenario / behavior | Folder |
|---|---------------------|--------|
| 1 | Credential access — failed logins | [`dataset/1/`](dataset/1/) |
| 2 | Defense evasion — Windows Firewall disabled (EVTX) | [`dataset/2/`](dataset/2/) |
| 3 | Anti-forensics — system time change (Event ID 4616) | [`dataset/3/`](dataset/3/) |

For a full step-by-step walkthrough on reproducing these samples (generating the
GraphML, exporting SVG/JSON, and a flexible-vs-strict comparison), see the
[Examples & Sample Datasets](https://recongraph.readthedocs.io/en/latest/examples.html)
page in the documentation.

## How to Test

The test suite lives in the `tests/` directory.

1. **Install the test dependencies**:

   ```bash
   pip install pytest pandas pyyaml
   ```

2. **Run the tests** from the project root:

   ```bash
   pytest -v
   ```

   You should see output indicating that all tests pass.

## Documentation

Full documentation is available at
[ReadTheDocs](https://recongraph.readthedocs.io/), including a step-by-step
[Examples & Sample Datasets](https://recongraph.readthedocs.io/en/latest/examples.html)
walkthrough.

## Licenses

### ReconGraph

This project is licensed under the [MIT License](LICENSE).

### Third-Party Licenses

This project uses **Sigma Rules** for event detection:

- The **Sigma specification** and logo are public domain.
- The **detection rules** from the [SigmaHQ repository](https://github.com/SigmaHQ/sigma)
  are released under the
  [Detection Rule License (DRL) 1.1](https://github.com/SigmaHQ/Detection-Rule-License).
