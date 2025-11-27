#!/usr/bin/env python3
"""
Ansible Validation and Linting
Runs ansible-lint and validation checks
"""

import subprocess
import sys
import yaml
from pathlib import Path

def run_ansible_lint(playbook_file):
    """Run ansible-lint on playbook"""
    try:
        result = subprocess.run(
            ['ansible-lint', playbook_file],
            capture_output=True,
            text=True,
            check=True
        )
        print("✓ ansible-lint passed")
        return True
    except subprocess.CalledProcessError as e:
        print("✗ ansible-lint failed:")
        print(e.stdout)
        print(e.stderr)
        return False

def validate_playbook_syntax(playbook_file):
    """Validate playbook YAML syntax"""
    try:
        with open(playbook_file) as f:
            yaml.safe_load(f)
        print("✓ YAML syntax valid")
        return True
    except yaml.YAMLError as e:
        print(f"✗ YAML syntax error: {e}")
        return False

def run_check_mode(playbook_file, inventory_file):
    """Run playbook in check mode"""
    try:
        cmd = [
            'ansible-playbook',
            '-i', inventory_file,
            '--check',
            playbook_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✓ Check mode passed")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("✗ Check mode failed:")
        print(e.stdout)
        print(e.stderr)
        return False

def validate_all(playbook_file, inventory_file=None):
    """Run all validation checks"""
    print(f"Validating {playbook_file}...")
    
    checks = [
        validate_playbook_syntax(playbook_file),
        run_ansible_lint(playbook_file)
    ]
    
    if inventory_file:
        checks.append(run_check_mode(playbook_file, inventory_file))
    
    if all(checks):
        print("✓ All validations passed")
        return True
    else:
        print("✗ Some validations failed")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate.py <playbook.yml> [inventory.yml]")
        sys.exit(1)
    
    playbook = sys.argv[1]
    inventory = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = validate_all(playbook, inventory)
    sys.exit(0 if success else 1)