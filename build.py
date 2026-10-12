#!/usr/bin/env python3
"""
SteadyCraft Build Script
Validates manifests, verifies UUIDs and JSON syntax, and bundles packages into:
  - dist/SteadyCraft_BP.mcpack
  - dist/SteadyCraft_RP.mcpack
  - dist/SteadyCraft.mcaddon
"""
import os
import sys
import json
import zipfile
import uuid
import shutil
import hashlib

def print_step(msg):
    print(f"\033[1;34m==>\033[0m \033[1m{msg}\033[0m")

def print_success(msg):
    print(f"\033[1;32m✔\033[0m {msg}")

def print_error(msg):
    print(f"\033[1;31m✖ ERROR:\033[0m {msg}", file=sys.stderr)

def validate_json_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        print_error(f"Malformed JSON in {file_path}: {e}")
        sys.exit(1)

def validate_manifest(manifest_path, pack_type):
    data = validate_json_file(manifest_path)
    
    header = data.get("header", {})
    modules = data.get("modules", [])

    header_uuid = header.get("uuid")
    if not header_uuid:
        print_error(f"{pack_type} manifest header missing UUID!")
        sys.exit(1)

    try:
        uuid.UUID(header_uuid)
    except ValueError:
        print_error(f"Invalid UUID in {pack_type} header: {header_uuid}")
        sys.exit(1)

    module_uuids = set()
    for mod in modules:
        mod_uuid = mod.get("uuid")
        if not mod_uuid:
            print_error(f"{pack_type} manifest module missing UUID!")
            sys.exit(1)
        try:
            uuid.UUID(mod_uuid)
        except ValueError:
            print_error(f"Invalid UUID in {pack_type} module: {mod_uuid}")
            sys.exit(1)
        
        if mod_uuid == header_uuid or mod_uuid in module_uuids:
            print_error(f"Duplicate UUID detected in {pack_type}: {mod_uuid}")
            sys.exit(1)
        module_uuids.add(mod_uuid)

    print_success(f"Validated {pack_type} manifest ({header.get('name')}, v{'.'.join(map(str, header.get('version', [])))})")
    return data

def zip_directory_contents(src_dir, output_zip_path):
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(src_dir):
            for file in sorted(files):
                if file.startswith("."):
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, src_dir)
                zf.write(file_path, arcname=rel_path)

def create_mcaddon(bp_dir, rp_dir, output_mcaddon_path):
    with zipfile.ZipFile(output_mcaddon_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Pack BP into SteadyCraft_BP/ subfolder
        for root, _, files in os.walk(bp_dir):
            for file in sorted(files):
                if file.startswith("."):
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.join("SteadyCraft_BP", os.path.relpath(file_path, bp_dir))
                zf.write(file_path, arcname=rel_path)

        # Pack RP into SteadyCraft_RP/ subfolder
        for root, _, files in os.walk(rp_dir):
            for file in sorted(files):
                if file.startswith("."):
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.join("SteadyCraft_RP", os.path.relpath(file_path, rp_dir))
                zf.write(file_path, arcname=rel_path)

def get_file_stats(file_path):
    size_kb = os.path.getsize(file_path) / 1024.0
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return size_kb, sha256.hexdigest()[:12]

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    bp_dir = os.path.join(root_dir, "BP")
    rp_dir = os.path.join(root_dir, "RP")
    dist_dir = os.path.join(root_dir, "dist")

    print_step("Validating project files...")
    bp_manifest = validate_manifest(os.path.join(bp_dir, "manifest.json"), "Behavior Pack")
    rp_manifest = validate_manifest(os.path.join(rp_dir, "manifest.json"), "Resource Pack")

    # Validate camera presets JSON
    cameras_dir = os.path.join(bp_dir, "cameras/presets")
    if os.path.exists(cameras_dir):
        for f in os.listdir(cameras_dir):
            if f.endswith(".json"):
                validate_json_file(os.path.join(cameras_dir, f))
                print_success(f"Validated camera preset: {f}")

    # Validate UI JSON
    ui_dir = os.path.join(rp_dir, "ui")
    if os.path.exists(ui_dir):
        for f in os.listdir(ui_dir):
            if f.endswith(".json"):
                validate_json_file(os.path.join(ui_dir, f))
                print_success(f"Validated UI definition: {f}")

    print_step("Building distribution packages in dist/...")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir, exist_ok=True)

    version_tuple = bp_manifest.get("header", {}).get("version", [0, 1, 0])
    version_str = f"v{'.'.join(map(str, version_tuple))}"

    bp_mcpack = os.path.join(dist_dir, f"SteadyCraft_BP_{version_str}.mcpack")
    rp_mcpack = os.path.join(dist_dir, f"SteadyCraft_RP_{version_str}.mcpack")
    addon_mcaddon = os.path.join(dist_dir, f"SteadyCraft_{version_str}.mcaddon")

    zip_directory_contents(bp_dir, bp_mcpack)
    bp_size, bp_hash = get_file_stats(bp_mcpack)
    print_success(f"Created {os.path.basename(bp_mcpack)} ({bp_size:.1f} KB, sha256:{bp_hash})")

    zip_directory_contents(rp_dir, rp_mcpack)
    rp_size, rp_hash = get_file_stats(rp_mcpack)
    print_success(f"Created {os.path.basename(rp_mcpack)} ({rp_size:.1f} KB, sha256:{rp_hash})")

    create_mcaddon(bp_dir, rp_dir, addon_mcaddon)
    addon_size, addon_hash = get_file_stats(addon_mcaddon)
    print_success(f"Created {os.path.basename(addon_mcaddon)} ({addon_size:.1f} KB, sha256:{addon_hash})")

    print_step("Build completed successfully!")

if __name__ == "__main__":
    main()
