#!/usr/bin/env python3
"""
Ansible Inventory Manager
Manages Ansible inventory files and SSH configurations
"""

import os
import yaml
import json
import sys
from pathlib import Path

def create_inventory(hosts_file, output_file, dry_run=False, verbose=False):
    """Create Ansible inventory from hosts file"""
    if dry_run:
        print(f"[DRY RUN] Would create inventory: {output_file}")
        with open(hosts_file) as f:
            hosts = json.load(f)
        
        if verbose:
            print(f"  📋 Planned Inventory Structure:")
            print(f"  📁 Output file: {output_file}")
            print(f"  🏠 Total hosts: {len(hosts)}")
            
            # Group analysis
            groups = {}
            for host in hosts:
                group = host.get('group', 'ungrouped')
                groups[group] = groups.get(group, 0) + 1
                print(f"  📂 Group '{group}': {groups[group]} hosts")
            
            print(f"  📋 Host Details:")
            for host in hosts:
                group = host.get('group', 'ungrouped')
                ip = host.get('ip', host['name'])
                user = host.get('user', 'root')
                port = host.get('port', 22)
                key_file = host.get('key_file', None)
                
                print(f"    🖥️ {host['name']}")
                print(f"      📍 IP: {ip}")
                print(f"      👤 User: {user}")
                print(f"      🔌 Port: {port}")
                if key_file:
                    print(f"      🔑 Key: {key_file}")
                print(f"      📂 Group: {group}")
        else:
            print(f"  Hosts: {len(hosts)}")
            for host in hosts:
                group = host.get('group', 'ungrouped')
                print(f"    {host['name']} -> {group}")
        
        return True
    
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
    return True

def create_ssh_config(inventory_file, ssh_config_file, dry_run=False, verbose=False):
    """Generate SSH config from Ansible inventory"""
    if dry_run:
        print(f"[DRY RUN] Would create SSH config: {ssh_config_file}")
        
        if verbose:
            print(f"  📋 Planned SSH Configuration:")
            print(f"  📁 Output file: {ssh_config_file}")
            
            with open(inventory_file) as f:
                inventory = yaml.safe_load(f)
                
            host_count = 0
            for group_name, group_data in inventory.get('all', {}).get('children', {}).items():
                host_count += len(group_data.get('hosts', {}))
                
            print(f"  🔌 Total SSH entries: {host_count}")
            
            # Group summary
            for group_name, group_data in inventory.get('all', {}).get('children', {}).items():
                hosts = group_data.get('hosts', {})
                print(f"  📂 Group '{group_name}': {len(hosts)} hosts")
                
                # Host details in verbose mode
                if verbose and hosts:
                    for host_name, host_vars in hosts.items():
                        ip = host_vars.get('ansible_host', host_name)
                        user = host_vars.get('ansible_user', 'root')
                        port = host_vars.get('ansible_port', 22)
                        key_file = host_vars.get('ansible_ssh_private_key_file')
                        
                        print(f"    🖥️ {host_name}")
                        print(f"      📍 IP: {ip}")
                        print(f"      👤 User: {user}")
                        print(f"      🔌 Port: {port}")
                        if key_file:
                            print(f"      🔑 Key: {key_file}")
        else:
            with open(inventory_file) as f:
                inventory = yaml.safe_load(f)
                
            host_count = 0
            for group_name, group_data in inventory.get('all', {}).get('children', {}).items():
                host_count += len(group_data.get('hosts', {}))
                
            print(f"  SSH entries: {host_count}")
        
        return True
    
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
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage Ansible inventory and SSH configs')
    parser.add_argument('action', choices=['create_inventory', 'create_ssh'], help='Action to perform')
    parser.add_argument('input', help='Input file')
    parser.add_argument('output', help='Output file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--verbose', action='store_true', help='Show detailed planning information')
    
    args = parser.parse_args()
    
    success = False
    if args.action == "create_inventory":
        success = create_inventory(args.input, args.output, args.dry_run, args.verbose)
    elif args.action == "create_ssh":
        success = create_ssh_config(args.input, args.output, args.dry_run, args.verbose)
    
    sys.exit(0 if success else 1)