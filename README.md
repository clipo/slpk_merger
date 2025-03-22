# SLPK Merger CLI

Merge two Esri SLPK (Scene Layer Package) files into one using an I3S-aware Python tool.

## Features

- Supports both Compact (`nodepages/*.json.gz`) and Standard (`nodes/*.json`) I3S formats
- Remaps node and resource IDs
- Shows progress bars for large files
- Outputs a valid `.slpk` ready for ArcGIS

## Installation

```bash
pip install -r requirements.txt
pip install .
```

## Usage

```bash
slpk-merge input1.slpk input2.slpk output.slpk
```

## Requirements

- Python 3.7+
- tqdm
