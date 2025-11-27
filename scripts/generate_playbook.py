#!/usr/bin/env python3
"""
Ansible Playbook Generator
Generates playbooks from templates and configurations
"""

import os
import yaml
import sys
from pathlib import Path

def generate_playbook(config_file, output_file, dry_run=False, verbose=False):
    """Generate playbook from config"""
    if dry_run:
        print(f"[DRY RUN] Would generate {output_file} from {config_file}")
        # Preview what would be generated
        with open(config_file) as f:
            config = yaml.safe_load(f)
        
        if verbose:
            print(f"  📋 Planned Playbook Structure:")
            print(f"  📝 Name: {config.get('name', 'Generated Playbook')}")
            print(f"  🏠 Hosts: {config.get('hosts', 'all')}")
            print(f"  📋 Tasks: {len(config.get('tasks', []))}")
            
            if config.get('vars'):
                print(f"  🔧 Variables: {len(config.get('vars', {}))}")
            if config.get('become'):
                print(f"  👑 Become: {config.get('become')}")
                
            print(f"  📁 Output file: {output_file}")
        else:
            print(f"  Playbook name: {config.get('name', 'Generated Playbook')}")
            print(f"  Hosts: {config.get('hosts', 'all')}")
            print(f"  Tasks: {len(config.get('tasks', []))}")
        
        return True
    
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
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Ansible playbooks from config')
    parser.add_argument('config', help='Configuration file')
    parser.add_argument('output', help='Output playbook file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be generated')
    parser.add_argument('--verbose', action='store_true', help='Show detailed planning information')
    parser.add_argument('--preview', action='store_true', help='Preview playbook structure')
    
    args = parser.parse_args()
    
    success = generate_playbook(args.config, args.output, args.dry_run or args.preview, args.verbose)
    sys.exit(0 if success else 1)