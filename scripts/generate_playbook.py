#!/usr/bin/env python3
"""
Ansible Playbook Generator
Generates playbooks from templates and configurations
"""

import os
import yaml
import sys
from pathlib import Path

# Import guardrails for context preservation
GUARDRAILS_AVAILABLE = False
AnsibleGuardrails = None

try:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from ansible_guardrails import AnsibleGuardrails
    GUARDRAILS_AVAILABLE = True
except ImportError:
    pass

def generate_playbook(config_file, output_file, dry_run=False, verbose=False):
    """Generate playbook from config with guardrails validation"""
    
    # Initialize guardrails if available
    guardrails = None
    if GUARDRAILS_AVAILABLE and AnsibleGuardrails:
        try:
            guardrails = AnsibleGuardrails()
        except Exception as e:
            if verbose:
                print(f"  ⚠️  Guardrails initialization failed: {e}")
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
        task_dict = {
            'name': task.get('name'),
            task['module']: task.get('params', {})
        }
        
        # Validate task with guardrails
        if guardrails:
            operation_type = f"{task['module']}_operations"
            analysis = guardrails.analyze_operation(operation_type, task.get('params', {}))
            
            if analysis["guardrails_violations"] and verbose:
                print(f"    ⚠️  Task '{task.get('name')}' guardrails warnings:")
                for violation in analysis["guardrails_violations"]:
                    print(f"      • {violation}")
            
            # Add guardrails recommendations as comments if needed
            if analysis["recommended_modules"]:
                task_dict['_guardrails_recommended'] = analysis["recommended_modules"]
        
        playbook['tasks'].append(task_dict)
    
    with open(output_file, 'w') as f:
        yaml.dump([playbook], f, default_flow_style=False)
    
    print(f"Generated {output_file}")
    
    # Offer to verify changes if this is an update to existing playbook
    if Path(output_file).exists():
        script_dir = Path(__file__).parent
        verify_script = script_dir / "verify_changes.py"
        
        if verify_script.exists():
            print(f"💡 Tip: Use '{verify_script} {output_file}' to verify changes are captured")
    
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