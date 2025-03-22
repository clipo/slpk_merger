# SLPK Merger CLI

Merge two Esri SLPK (Scene Layer Package) files into one using an I3S-aware Python tool.

## Installation

```bash
pip install -r requirements.txt
pip install .
```

## Usage

```bash
slpk-merge first.slpk second.slpk merged_output.slpk
```

## Features

- Merges compact I3S nodepages
- Remaps geometry/texture references
- Progress bars via `tqdm` for long operations

## Requirements

- Python 3.7+
- tqdm
