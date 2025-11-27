#!/usr/bin/env python3
"""
Ansible Validation and Linting
Runs ansible-lint and validation checks
"""

import os
import subprocess
import sys
import yaml
from pathlib import Path

# Mode detection
PLANNING_MODE = os.environ.get('OPENCODE_PLANNING_MODE', 'false').lower() == 'true'

def run_ansible_lint(playbook_file, dry_run=False):
    """Run ansible-lint on playbook"""
    if dry_run or PLANNING_MODE:
        print(f"[DRY RUN] Would run ansible-lint on {playbook_file}")
        return True
    
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

def run_check_mode(playbook_file, inventory_file, dry_run=False):
    """Run playbook in check mode"""
    if dry_run or PLANNING_MODE:
        print(f"[DRY RUN] Would run ansible-playbook --check on {playbook_file}")
        return True
    
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

def validate_all(playbook_file, inventory_file=None, dry_run=False):
    """Run all validation checks"""
    print(f"Validating {playbook_file}...")
    
    checks = [
        validate_playbook_syntax(playbook_file),
        run_ansible_lint(playbook_file, dry_run)
    ]
    
    if inventory_file:
        checks.append(run_check_mode(playbook_file, inventory_file, dry_run))
    
    if all(checks):
        print("✓ All validations passed")
        return True
    else:
        print("✗ Some validations failed")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Ansible playbooks')
    parser.add_argument('playbook', help='Playbook file to validate')
    parser.add_argument('inventory', nargs='?', help='Inventory file (optional)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    parser.add_argument('--syntax-only', action='store_true', help='Only check YAML syntax')
    parser.add_argument('--lint-only', action='store_true', help='Only run ansible-lint')
    
    args = parser.parse_args()
    
    if args.syntax_only:
        success = validate_playbook_syntax(args.playbook)
    elif args.lint_only:
        success = run_ansible_lint(args.playbook, args.dry_run)
    else:
        success = validate_all(args.playbook, args.inventory, args.dry_run)
    
    sys.exit(0 if success else 1)