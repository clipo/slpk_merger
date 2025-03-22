# SLPK Folder-Node Merger CLI

This tool merges two Esri SLPK files that use folder-based node structures (e.g., `0/`, `0-0/`).

## Features

- Automatically detects folder-based I3S node format
- Remaps node folders and internal JSON references
- Merges assets and repackages into a valid `.slpk`
- Progress bars via `tqdm`

## Installation

```bash
pip install -r requirements.txt
pip install .
```

## Usage

```bash
slpk-merge input1.slpk input2.slpk merged_output.slpk
```

## Requirements

- Python 3.7+
- tqdm
