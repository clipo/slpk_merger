import os
import zipfile
import shutil
import json
import gzip
from tqdm import tqdm

def extract_slpk(slpk_path, extract_to):
    with zipfile.ZipFile(slpk_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def is_compact_format(extracted_path):
    return os.path.exists(os.path.join(extracted_path, 'nodepages'))

def copy_metadata_and_index(src_dir, dest_dir):
    for filename in ['metadata.json', 'index.json']:
        src = os.path.join(src_dir, filename)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dest_dir, filename))

def merge_slpks(slpk1, slpk2, output_slpk):
    temp_dir = os.path.splitext(output_slpk)[0] + '_work'
    os.makedirs(temp_dir, exist_ok=True)

    extract1 = os.path.join(temp_dir, 'slpk1')
    extract2 = os.path.join(temp_dir, 'slpk2')
    final_dir = os.path.join(temp_dir, 'merged')

    extract_slpk(slpk1, extract1)
    extract_slpk(slpk2, extract2)

    compact1 = is_compact_format(extract1)
    compact2 = is_compact_format(extract2)

    if compact1 and compact2:
        print("[INFO] Merging Compact I3S format (nodepages)...")
        # TODO: merge nodepages logic
    elif not compact1 and not compact2:
        print("[INFO] Merging Standard I3S format (nodes/*.json)...")
        # TODO: merge standard nodes logic
    else:
        raise ValueError("Cannot merge Compact and Standard I3S formats together (mismatch).")

    os.makedirs(final_dir, exist_ok=True)
    copy_metadata_and_index(extract1, final_dir)

    # Write dummy 3dSceneLayer.json.gz
    scene_layer = {
        "version": "1.7",
        "layerType": "3DObject",
        "resource": {"rootNode": "0"}
    }
    with gzip.open(os.path.join(final_dir, "3dSceneLayer.json.gz"), 'wt', encoding='utf-8') as f:
        json.dump(scene_layer, f, indent=2)

    # Package
    if os.path.exists(output_slpk):
        os.remove(output_slpk)
    shutil.make_archive(output_slpk.replace(".slpk", ""), 'zip', final_dir)
    os.rename(output_slpk.replace(".slpk", ".zip"), output_slpk)
    print("[SUCCESS] Merged SLPK created at:", output_slpk)
