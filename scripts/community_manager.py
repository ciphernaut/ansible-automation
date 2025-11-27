#!/usr/bin/env python3
"""
Ansible Community Module Manager
Discovers and installs community modules and collections
"""

import os
import subprocess
import json
import sys
from pathlib import Path

def search_community_modules(search_term, dry_run=False):
    """Search for community modules"""
    if dry_run:
        print(f"[DRY RUN] Would search for modules: {search_term}")
        print(f"  Command: ansible-galaxy search {search_term}")
        return True
    
    try:
        result = subprocess.run(
            ['ansible-galaxy', 'search', search_term],
            capture_output=True,
            text=True,
            check=True
        )
        print("Search results:")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Search failed: {e.stderr}")
        return False

def install_collection(collection_name, dry_run=False):
    """Install Ansible collection"""
    if dry_run:
        print(f"[DRY RUN] Would install collection: {collection_name}")
        print(f"  Command: ansible-galaxy collection install {collection_name}")
        return True
    
    try:
        result = subprocess.run(
            ['ansible-galaxy', 'collection', 'install', collection_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ Installed collection: {collection_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {collection_name}: {e.stderr}")
        return False

def list_installed_collections():
    """List installed collections"""
    collections_path = Path.home() / '.ansible' / 'collections' / 'ansible_collections'
    
    if not collections_path.exists():
        print("No collections installed")
        return
    
    print("Installed collections:")
    for namespace in collections_path.iterdir():
        if namespace.is_dir():
            for collection in namespace.iterdir():
                if collection.is_dir():
                    print(f"  {namespace.name}.{collection.name}")

def get_collection_info(collection_name):
    """Get information about a collection"""
    try:
        namespace, name = collection_name.split('.')
        collection_path = Path.home() / '.ansible' / 'collections' / 'ansible_collections' / namespace / name
        
        if collection_path.exists():
            meta_file = collection_path / 'meta' / 'runtime.yml'
            if meta_file.exists():
                with open(meta_file) as f:
                    print(f"Collection info for {collection_name}:")
                    print(f.read())
            else:
                print(f"Collection {collection_name} is installed but no metadata found")
        else:
            print(f"Collection {collection_name} not found")
    except ValueError:
        print("Collection name must be in format 'namespace.name'")

def install_common_collections(dry_run=False):
    """Install commonly used collections"""
    common_collections = [
        'community.general',
        'community.crypto',
        'community.docker',
        'ansible.posix',
        'community.windows'
    ]
    
    print("Installing common collections...")
    for collection in common_collections:
        install_collection(collection, dry_run)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage Ansible community modules and collections')
    parser.add_argument('action', choices=['search', 'install', 'list', 'info', 'install_common'], help='Action to perform')
    parser.add_argument('term', nargs='?', help='Search term or collection name')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    
    args = parser.parse_args()
    
    success = False
    if args.action == "search" and args.term:
        success = search_community_modules(args.term, args.dry_run)
    elif args.action == "install" and args.term:
        success = install_collection(args.term, args.dry_run)
    elif args.action == "list":
        success = list_installed_collections()
    elif args.action == "info" and args.term:
        success = get_collection_info(args.term)
    elif args.action == "install_common":
        success = install_common_collections(args.dry_run)
    
    sys.exit(0 if success else 1)