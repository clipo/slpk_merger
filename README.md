# SLPK Merger CLI Tool

This is a Python command-line tool for merging two Esri SLPK (Scene Layer Package) files into a single `.slpk`. It is I3S-aware and supports the compact nodePages structure, ensuring correct merging of node hierarchies, geometry resources, and textures.

## Features

- Extracts both input `.slpk` files
- Merges I3S node pages, offsetting IDs to avoid collisions
- Copies and remaps geometry and texture assets
- Updates `3dSceneLayer.json` metadata
- Repackages everything into a valid `.slpk` file

## Requirements

- Python 3.7 or higher
- No external libraries required (pure standard library)

## Installation

Clone or download this repo and install it locally:

```bash
pip install .
```

This will install the command `slpk-merge` to your environment.

## Usage

```bash
slpk-merge path/to/first.slpk path/to/second.slpk output_merged.slpk
```

### Example

```bash
slpk-merge sample1.slpk sample2.slpk merged_result.slpk
```

## Output

The output `.slpk` will include:

- A merged `3dSceneLayer.json` with a new UUID and updated references
- Combined `nodepages` with adjusted `index`, `parentIndex`, and `children` relationships
- Geometry and texture files with new, unique resource IDs
- A ZIP-compressed `.slpk` ready for use in:
  - ArcGIS Pro
  - ArcGIS Online
  - Any tool that supports I3S Scene Layers

## Notes

- This tool currently assumes both SLPKs use the **I3S Compact format** with `nodepages/*.json.gz`.
- Only handles `nodes/0/` and `nodes/1/` from each SLPK for simplicity (expandable).
- Geometry and texture file names must be numeric (e.g., `0.bin.gz`, `1.jpg`).

## License

MIT License
