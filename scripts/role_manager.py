#!/usr/bin/env python3
"""
Ansible Role Manager
Creates and manages Ansible roles with proper structure
"""

import os
import sys
import subprocess
from pathlib import Path

def create_role(role_name, base_path="."):
    """Create a new Ansible role with standard structure"""
    role_path = Path(base_path) / role_name
    
    # Create role directory
    role_path.mkdir(exist_ok=True)
    
    # Create standard subdirectories
    subdirs = ['tasks', 'handlers', 'templates', 'files', 'vars', 'defaults', 'meta']
    for subdir in subdirs:
        (role_path / subdir).mkdir(exist_ok=True)
    
    # Create main.yml files
    main_files = {
        'tasks/main.yml': '---\n# Main tasks for {{ role_name }}\n',
        'handlers/main.yml': '---\n# Handlers for {{ role_name }}\n',
        'vars/main.yml': '---\n# Variables for {{ role_name }}\n',
        'defaults/main.yml': '---\n# Default variables for {{ role_name }}\n',
        'meta/main.yml': '---\n# Role dependencies\n# dependencies:\n#   - role: geerlingguy.nginx\n'
    }
    
    for file_path, content in main_files.items():
        full_path = role_path / file_path
        if not full_path.exists():
            with open(full_path, 'w') as f:
                f.write(content.replace('{{ role_name }}', role_name))
    
    print(f"Created role: {role_path}")

def create_collection(collection_name, base_path="."):
    """Create a new Ansible collection using ansible-galaxy"""
    try:
        result = subprocess.run(
            ['ansible-galaxy', 'collection', 'init', collection_name],
            cwd=base_path,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ Created collection: {collection_name}")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create collection: {e.stderr}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 role_manager.py <role|collection> <name> [path]")
        sys.exit(1)
    
    action = sys.argv[1]
    name = sys.argv[2]
    path = sys.argv[3] if len(sys.argv) > 3 else "."
    
    if action == "role":
        create_role(name, path)
    elif action == "collection":
        create_collection(name, path)
    else:
        print("Action must be 'role' or 'collection'")
        sys.exit(1)