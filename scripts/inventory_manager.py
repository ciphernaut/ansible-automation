#!/usr/bin/env python3
"""
Ansible Inventory Manager
Manages Ansible inventory files and SSH configurations
"""

import yaml
import json
import sys
from pathlib import Path

def create_inventory(hosts_file, output_file):
    """Create Ansible inventory from hosts file"""
    inventory = {
        'all': {
            'children': {}
        }
    }
    
    with open(hosts_file) as f:
        hosts = json.load(f)
    
    # Group hosts by environment or type
    for host in hosts:
        group = host.get('group', 'ungrouped')
        if group not in inventory['all']['children']:
            inventory['all']['children'][group] = {
                'hosts': {},
                'vars': {}
            }
        
        inventory['all']['children'][group]['hosts'][host['name']] = {
            'ansible_host': host.get('ip', host['name']),
            'ansible_user': host.get('user', 'root'),
            'ansible_ssh_private_key_file': host.get('key_file'),
            'ansible_port': host.get('port', 22)
        }
    
    with open(output_file, 'w') as f:
        yaml.dump(inventory, f, default_flow_style=False)
    
    print(f"Created inventory: {output_file}")

def create_ssh_config(inventory_file, ssh_config_file):
    """Generate SSH config from Ansible inventory"""
    with open(inventory_file) as f:
        inventory = yaml.safe_load(f)
    
    ssh_config = []
    
    for group_name, group_data in inventory.get('all', {}).get('children', {}).items():
        for host_name, host_vars in group_data.get('hosts', {}).items():
            config_line = f"Host {host_name}\n"
            config_line += f"    HostName {host_vars.get('ansible_host', host_name)}\n"
            config_line += f"    User {host_vars.get('ansible_user', 'root')}\n"
            config_line += f"    Port {host_vars.get('ansible_port', 22)}\n"
            
            if host_vars.get('ansible_ssh_private_key_file'):
                config_line += f"    IdentityFile {host_vars['ansible_ssh_private_key_file']}\n"
            
            config_line += "    StrictHostKeyChecking no\n\n"
            ssh_config.append(config_line)
    
    with open(ssh_config_file, 'w') as f:
        f.writelines(ssh_config)
    
    print(f"Created SSH config: {ssh_config_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 inventory_manager.py <create_inventory|create_ssh> <input> <output>")
        sys.exit(1)
    
    action = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    
    if action == "create_inventory":
        create_inventory(input_file, output_file)
    elif action == "create_ssh":
        create_ssh_config(input_file, output_file)
    else:
        print("Action must be 'create_inventory' or 'create_ssh'")
        sys.exit(1)