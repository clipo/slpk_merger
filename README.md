# SLPK Compact I3S Merger CLI

Merges two Esri SLPK files using the Compact I3S format (e.g., Integrated Mesh layers).

## Features

- Supports `nodepages/` and `nodes/` from Compact I3S
- Automatically remaps node indices and file references
- Merges `3dSceneLayer.json.gz` and `metadata.json`
- Generates required `index.json` for ArcGIS compatibility
- Shows progress bars using `tqdm`

## Installation

```bash
pip install -r requirements.txt
pip install .
```

## Usage

```bash
slpk-merge slpk1.slpk slpk2.slpk merged_output.slpk
```

## Requirements

- Python 3.7+
