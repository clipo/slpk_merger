# SLPK Dual-Format Merger CLI

Merges two Esri SLPK files that use either:
- Compact I3S (`nodepages/*.json.gz`)
- Standard I3S (`nodes/*.json`)

## Features

- Auto-detects Compact or Standard I3S format
- Merges node trees, geometry, metadata
- Handles `3dSceneLayer.json.gz`, `metadata.json`, and `index.json`
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
