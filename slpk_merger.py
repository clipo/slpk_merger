import os
import zipfile
import shutil
import gzip
import json
import uuid
import math
import copy

def extract_slpk(slpk_path, extract_to):
    with zipfile.ZipFile(slpk_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def load_gzipped_json(path):
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        return json.load(f)

def extract_nodes_from_nodepage(path):
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        data = json.load(f)
        return data.get("nodes", [])

def merge_nodepages_fixed(nodepages_a, nodepages_b, offset_index=10000, offset_resource=10000):
    merged = []
    merged.extend(copy.deepcopy(nodepages_a))
    for node in nodepages_b:
        new_node = copy.deepcopy(node)
        new_node["index"] += offset_index
        if "parentIndex" in new_node:
            new_node["parentIndex"] += offset_index
        if "children" in new_node:
            new_node["children"] = [child + offset_index for child in new_node["children"]]
        if "mesh" in new_node:
            mesh = new_node["mesh"]
            for part in ["attribute", "geometry", "material"]:
                if part in mesh and "resource" in mesh[part]:
                    mesh[part]["resource"] += offset_resource
        merged.append(new_node)
    return merged

def write_nodepages_chunks(merged_nodes, output_dir, nodes_per_page=1000):
    os.makedirs(output_dir, exist_ok=True)
    total_pages = math.ceil(len(merged_nodes) / nodes_per_page)
    for page_num in range(total_pages):
        start = page_num * nodes_per_page
        end = start + nodes_per_page
        chunk = {"nodes": merged_nodes[start:end]}
        out_path = os.path.join(output_dir, f"{page_num}.json.gz")
        with gzip.open(out_path, "wt", encoding="utf-8") as f:
            json.dump(chunk, f)
    return total_pages

def copy_and_remap_assets_safe(source_dirs, output_dir, resource_offset=10000):
    os.makedirs(output_dir, exist_ok=True)
    resource_map = {}
    for source_path, base_resource_id in source_dirs:
        for root, _, files in os.walk(source_path):
            for file in files:
                if file.endswith(('.bin.gz', '.bin', '.jpg', '.dds.gz')):
                    old_path = os.path.join(root, file)
                    relative_dir = os.path.relpath(root, source_path)
                    try:
                        stem = os.path.splitext(file)[0]
                        if stem.endswith(".bin"):
                            stem = os.path.splitext(stem)[0]
                        resource_id = int(stem)
                    except ValueError:
                        continue
                    new_id = base_resource_id + resource_id + resource_offset
                    new_dir = os.path.join(output_dir, relative_dir)
                    os.makedirs(new_dir, exist_ok=True)
                    ext = os.path.splitext(file)[1]
                    new_filename = f"{new_id}{ext}"
                    new_path = os.path.join(new_dir, new_filename)
                    shutil.copy2(old_path, new_path)
                    resource_map[base_resource_id + resource_id] = new_id
    return resource_map

def update_3dscene_layer_json(input_path, output_path):
    with gzip.open(input_path, 'rt', encoding='utf-8') as f:
        scene_layer_data = json.load(f)
    scene_layer_data['id'] = str(uuid.uuid4())
    scene_layer_data['version'] = scene_layer_data.get('version', '1.7')
    if 'resource' not in scene_layer_data:
        scene_layer_data['resource'] = {}
    scene_layer_data['resource']['nodePages'] = {
        "href": "nodepages"
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scene_layer_data, f, indent=2)

def merge_slpks(slpk1, slpk2, output_slpk):
    base_dir = os.path.splitext(output_slpk)[0]
    os.makedirs(base_dir, exist_ok=True)

    extract1 = os.path.join(base_dir, 'slpk1')
    extract2 = os.path.join(base_dir, 'slpk2')
    merged_nodepages_dir = os.path.join(base_dir, 'nodepages')
    merged_assets_dir = os.path.join(base_dir, 'assets')

    extract_slpk(slpk1, extract1)
    extract_slpk(slpk2, extract2)

    # Merge nodepages
    np1 = extract_nodes_from_nodepage(os.path.join(extract1, 'nodepages/0.json.gz'))
    np2 = extract_nodes_from_nodepage(os.path.join(extract2, 'nodepages/0.json.gz'))
    merged_nodes = merge_nodepages_fixed(np1, np2)
    write_nodepages_chunks(merged_nodes, merged_nodepages_dir)

    # Copy and remap geometries/textures
    source_assets = [
        (os.path.join(extract1, "nodes/0/geometries"), 0),
        (os.path.join(extract2, "nodes/1/geometries"), 0),
        (os.path.join(extract1, "nodes/0/textures"), 0),
        (os.path.join(extract2, "nodes/1/textures"), 0),
    ]
    copy_and_remap_assets_safe(source_assets, merged_assets_dir)

    # Update and save 3dSceneLayer.json
    updated_json_path = os.path.join(base_dir, "3dSceneLayer.json")
    update_3dscene_layer_json(os.path.join(extract1, '3dSceneLayer.json.gz'), updated_json_path)

    # Build final directory
    for sub in ["geometries", "textures"]:
        src_path = os.path.join(merged_assets_dir, sub)
        if os.path.exists(src_path):
            shutil.copytree(src_path, os.path.join(base_dir, sub), dirs_exist_ok=True)
    shutil.copytree(merged_nodepages_dir, os.path.join(base_dir, "nodepages"), dirs_exist_ok=True)

    # Package into .slpk
    shutil.make_archive(base_dir, 'zip', base_dir)
    os.rename(f"{base_dir}.zip", output_slpk)
