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

def copy_nodepages_and_remap(source_dir, dest_dir, index_offset, resource_offset):
    os.makedirs(dest_dir, exist_ok=True)
    remapped_nodes = []
    original_index = 0
    for file in sorted(os.listdir(source_dir)):
        if not file.endswith('.json.gz'):
            continue
        path = os.path.join(source_dir, file)
        data = load_gzipped_json(path)
        for node in data.get('nodes', []):
            new_node = json.loads(json.dumps(node))  # deep copy
            new_node['index'] += index_offset
            if 'parentIndex' in new_node:
                new_node['parentIndex'] += index_offset
            if 'children' in new_node:
                new_node['children'] = [i + index_offset for i in new_node['children']]
            if 'mesh' in new_node:
                for part in ['geometry', 'material', 'attribute']:
                    if part in new_node['mesh'] and 'resource' in new_node['mesh'][part]:
                        new_node['mesh'][part]['resource'] += resource_offset
            remapped_nodes.append(new_node)
            original_index += 1
    out_path = os.path.join(dest_dir, '0.json.gz')
    write_gzipped_json({'nodes': remapped_nodes}, out_path)

def copy_nodes_data(source_nodes, dest_nodes, resource_offset):
    os.makedirs(dest_nodes, exist_ok=True)
    for file in tqdm(os.listdir(source_nodes), desc=f"Copying nodes from {source_nodes}"):
        if not file[0].isdigit():
            continue
        try:
            new_id = int(file.split('.')[0]) + resource_offset
            ext = '.' + '.'.join(file.split('.')[1:])
            shutil.copy2(os.path.join(source_nodes, file), os.path.join(dest_nodes, f"{new_id}{ext}"))
        except Exception as e:
            print(f"Skipping {file}: {e}")

def update_scene_layer(input_path, output_path):
    with gzip.open(input_path, 'rt', encoding='utf-8') as f:
        data = json.load(f)
    data['id'] = str(uuid.uuid4())
    with gzip.open(output_path, 'wt', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def merge_slpks(slpk1, slpk2, output_slpk):
    temp_dir = os.path.splitext(output_slpk)[0] + '_work'
    os.makedirs(temp_dir, exist_ok=True)

    extract1 = os.path.join(temp_dir, 'slpk1')
    extract2 = os.path.join(temp_dir, 'slpk2')
    extract_slpk(slpk1, extract1)
    extract_slpk(slpk2, extract2)

    merged_root = os.path.join(temp_dir, 'merged')
    os.makedirs(merged_root, exist_ok=True)

    # Merge nodepages
    merged_nodepages = os.path.join(merged_root, 'nodepages')
    copy_nodepages_and_remap(os.path.join(extract1, 'nodepages'), merged_nodepages, index_offset=0, resource_offset=0)
    copy_nodepages_and_remap(os.path.join(extract2, 'nodepages'), merged_nodepages, index_offset=10000, resource_offset=10000)

    # Merge nodes (geometry/textures)
    merged_nodes = os.path.join(merged_root, 'nodes')
    copy_nodes_data(os.path.join(extract1, 'nodes'), merged_nodes, resource_offset=0)
    copy_nodes_data(os.path.join(extract2, 'nodes'), merged_nodes, resource_offset=10000)

    # Copy and update scene layer
    update_scene_layer(os.path.join(extract1, '3dSceneLayer.json.gz'),
                       os.path.join(merged_root, '3dSceneLayer.json.gz'))

    # Copy metadata.json if exists
    for f in ['metadata.json']:
        for extract in [extract1, extract2]:
            src = os.path.join(extract, f)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(merged_root, f))
                break

    # Generate index.json
    index_path = os.path.join(merged_root, 'index.json')
    with open(index_path, 'w') as f:
        json.dump({
            'version': '1.7',
            'layers': [{'href': '3dSceneLayer.json.gz'}]
        }, f, indent=2)

    # Create final .slpk
    shutil.make_archive(output_slpk.replace('.slpk', ''), 'zip', merged_root)
    if os.path.exists(output_slpk):
        os.remove(output_slpk)
    os.rename(output_slpk.replace('.slpk', '') + '.zip', output_slpk)
