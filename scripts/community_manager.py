#!/usr/bin/env python3
"""
Ansible Community Module Manager
Discovers and installs community modules and collections
"""

import subprocess
import json
import sys
from pathlib import Path

def search_community_modules(search_term):
    """Search for community modules"""
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

def install_collection(collection_name):
    """Install Ansible collection"""
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

def install_common_collections():
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
        install_collection(collection)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 community_manager.py <search|install|list|info|install_common> [term|collection]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "search" and len(sys.argv) > 2:
        search_community_modules(sys.argv[2])
    elif action == "install" and len(sys.argv) > 2:
        install_collection(sys.argv[2])
    elif action == "list":
        list_installed_collections()
    elif action == "info" and len(sys.argv) > 2:
        get_collection_info(sys.argv[2])
    elif action == "install_common":
        install_common_collections()
    else:
        print("Invalid action or missing arguments")
        sys.exit(1)