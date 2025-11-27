#!/usr/bin/env python3
"""
Ansible Playbook Generator
Generates playbooks from templates and configurations
"""

import yaml
import sys
from pathlib import Path

def generate_playbook(config_file, output_file):
    """Generate playbook from config"""
    with open(config_file) as f:
        config = yaml.safe_load(f)
    
    playbook = {
        'name': config.get('name', 'Generated Playbook'),
        'hosts': config.get('hosts', 'all'),
        'become': config.get('become', False),
        'tasks': []
    }
    
    for task in config.get('tasks', []):
        playbook['tasks'].append({
            'name': task.get('name'),
            task['module']: task.get('params', {})
        })
    
    with open(output_file, 'w') as f:
        yaml.dump([playbook], f, default_flow_style=False)
    
    print(f"Generated {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 generate_playbook.py <config.yml> <output.yml>")
        sys.exit(1)
    
    generate_playbook(sys.argv[1], sys.argv[2])