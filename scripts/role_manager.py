#!/usr/bin/env python3
"""
Ansible Role Manager
Creates and manages Ansible roles with proper structure
"""

import os
import sys
import subprocess
from pathlib import Path

# Mode detection
PLANNING_MODE = os.environ.get('OPENCODE_PLANNING_MODE', 'false').lower() == 'true'

def create_role(role_name, base_path=".", dry_run=False):
    """Create a new Ansible role with standard structure"""
    role_path = Path(base_path) / role_name
    
    if dry_run or PLANNING_MODE:
        print(f"[DRY RUN] Would create role: {role_path}")
        print(f"  Directories: tasks, handlers, templates, files, vars, defaults, meta")
        print(f"  Files: tasks/main.yml, handlers/main.yml, vars/main.yml, defaults/main.yml, meta/main.yml")
        return True
    
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
    return True

def create_collection(collection_name, base_path=".", dry_run=False):
    """Create a new Ansible collection using ansible-galaxy"""
    if dry_run or PLANNING_MODE:
        print(f"[DRY RUN] Would create collection: {collection_name}")
        print(f"  Command: ansible-galaxy collection init {collection_name}")
        return True
    
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage Ansible roles and collections')
    parser.add_argument('action', choices=['role', 'collection'], help='Action to perform')
    parser.add_argument('name', help='Role or collection name')
    parser.add_argument('path', nargs='?', default='.', help='Base path (default: current directory)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    
    args = parser.parse_args()
    
    success = False
    if args.action == "role":
        success = create_role(args.name, args.path, args.dry_run)
    elif args.action == "collection":
        success = create_collection(args.name, args.path, args.dry_run)
    
    sys.exit(0 if success else 1)