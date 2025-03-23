import os
import zipfile
import shutil
import json
import gzip
from tqdm import tqdm

def extract_slpk(slpk_path, extract_to):
    with zipfile.ZipFile(slpk_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def is_compact_folder_format(path):
    nodes_dir = os.path.join(path, 'nodes')
    if not os.path.exists(nodes_dir):
        return False
    for entry in os.listdir(nodes_dir):
        sub = os.path.join(nodes_dir, entry)
        if os.path.isdir(sub) and os.path.exists(os.path.join(sub, '3dNodeIndexDocument.json.gz')):
            return True
    return False

def copy_metadata_and_index(src_dir, dest_dir):
    for filename in ['metadata.json', 'index.json']:
        src = os.path.join(src_dir, filename)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dest_dir, filename))

def copy_node_folders(src_nodes, dest_nodes):
    os.makedirs(dest_nodes, exist_ok=True)
    for node_name in tqdm(os.listdir(src_nodes), desc=f"Copying nodes from {src_nodes}"):
        src_path = os.path.join(src_nodes, node_name)
        dest_path = os.path.join(dest_nodes, node_name)
        try:
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dest_path)
        except Exception as e:
            print(f"Skipping {node_name}: {e}")

def merge_slpks(slpk1, slpk2, output_slpk):
    temp_dir = os.path.splitext(output_slpk)[0] + '_work'
    os.makedirs(temp_dir, exist_ok=True)

    extract1 = os.path.join(temp_dir, 'slpk1')
    extract2 = os.path.join(temp_dir, 'slpk2')
    final_dir = os.path.join(temp_dir, 'merged')

    extract_slpk(slpk1, extract1)
    extract_slpk(slpk2, extract2)

    def load_version(path):
        json_path = os.path.join(path, "3dSceneLayer.json.gz")
        with gzip.open(json_path, "rt", encoding="utf-8") as f:
            return json.load(f).get("version", "unknown")

    v1 = load_version(extract1)
    v2 = load_version(extract2)
    if v1 != v2:
        raise ValueError(f"SLPK version mismatch: {os.path.basename(slpk1)} is v{v1}, {os.path.basename(slpk2)} is v{v2}.\n"
                         "Please re-export both using the same I3S version from ArcGIS Pro.")

    if not (is_compact_folder_format(extract1) and is_compact_folder_format(extract2)):
        raise ValueError("One or both SLPKs do not use folder-based Compact I3S format (with 3dNodeIndexDocument.json.gz).")

    print("[INFO] Merging Compact folder-based I3S nodes...")
    os.makedirs(final_dir, exist_ok=True)
    copy_metadata_and_index(extract1, final_dir)

    # Copy node folders from both inputs
    copy_node_folders(os.path.join(extract1, "nodes"), os.path.join(final_dir, "nodes"))
    copy_node_folders(os.path.join(extract2, "nodes"), os.path.join(final_dir, "nodes"))

    # Copy scene layer JSON
    shutil.copy2(os.path.join(extract1, "3dSceneLayer.json.gz"), os.path.join(final_dir, "3dSceneLayer.json.gz"))

    # Package
    if os.path.exists(output_slpk):
        os.remove(output_slpk)
    shutil.make_archive(output_slpk.replace(".slpk", ""), 'zip', final_dir)
    os.rename(output_slpk.replace(".slpk", ".zip"), output_slpk)
    print("[SUCCESS] Merged SLPK created at:", output_slpk)
