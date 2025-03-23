import os
import zipfile
import shutil
import gzip
import json
import uuid
from tqdm import tqdm

def extract_slpk(slpk_path, extract_to):
    with zipfile.ZipFile(slpk_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def load_gzipped_json(path):
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        return json.load(f)

def write_gzipped_json(data, path):
    with gzip.open(path, 'wt', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def collect_node_folders(base_dir):
    return sorted([
        f for f in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, f)) and ('-' in f or f.isdigit())
    ])

def remap_folder_node_structure(source_dir, dest_dir, start_id):
    os.makedirs(dest_dir, exist_ok=True)
    folder_map = {}
    current_id = start_id

    for folder in tqdm(collect_node_folders(source_dir), desc=f"Remapping {source_dir}"):
        src_path = os.path.join(source_dir, folder)
        new_folder = f"{current_id}"
        dest_path = os.path.join(dest_dir, new_folder)
        shutil.copytree(src_path, dest_path)

        # Update 3dNodeIndexDocument.json.gz
        index_doc_path = os.path.join(dest_path, "3dNodeIndexDocument.json.gz")
        if os.path.exists(index_doc_path):
            index_data = load_gzipped_json(index_doc_path)
            index_data['id'] = new_folder
            if 'children' in index_data:
                index_data['children'] = [str(start_id + int(child.split('-')[0])) for child in index_data['children']]
            write_gzipped_json(index_data, index_doc_path)

        folder_map[folder] = new_folder
        current_id += 1

    return folder_map

def update_3dscene_layer_json(input_path, output_path):
    with gzip.open(input_path, 'rt', encoding='utf-8') as f:
        scene_layer_data = json.load(f)
    scene_layer_data['id'] = str(uuid.uuid4())
    if 'resource' not in scene_layer_data:
        scene_layer_data['resource'] = {}
    scene_layer_data['resource']['rootNode'] = "0"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(scene_layer_data, f, indent=2)

def merge_slpks(slpk1, slpk2, output_slpk):
    base_dir = os.path.splitext(output_slpk)[0]
    os.makedirs(base_dir, exist_ok=True)

    extract1 = os.path.join(base_dir, 'slpk1')
    extract2 = os.path.join(base_dir, 'slpk2')
    merged_nodes_dir = os.path.join(base_dir, 'merged_nodes')

    extract_slpk(slpk1, extract1)
    extract_slpk(slpk2, extract2)

    remap_folder_node_structure(extract1, merged_nodes_dir, start_id=0)
    remap_folder_node_structure(extract2, merged_nodes_dir, start_id=10000)

    # Copy and update 3dSceneLayer.json
    scene_json_path = os.path.join(base_dir, '3dSceneLayer.json')
    input_scene_path = os.path.join(extract1, '3dSceneLayer.json.gz')
    update_3dscene_layer_json(input_scene_path, scene_json_path)

    # Copy node folders to root
    for folder in os.listdir(merged_nodes_dir):
        src = os.path.join(merged_nodes_dir, folder)
        dst = os.path.join(base_dir, folder)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)

    # Determine final output path
    slpk_path = output_slpk if output_slpk.endswith('.slpk') else output_slpk + '.slpk'
    if os.path.exists(slpk_path):
        os.remove(slpk_path)

    # Create and rename archive
    shutil.make_archive(base_dir, 'zip', base_dir)
    os.replace(f"{base_dir}.zip", slpk_path)
