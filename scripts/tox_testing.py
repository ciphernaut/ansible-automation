#!/usr/bin/env python3
"""
Ansible Tox Testing Framework
Sets up and runs tox tests with Docker targets
"""

import os
import subprocess
import sys
import yaml
from pathlib import Path

# Mode detection
PLANNING_MODE = os.environ.get('OPENCODE_PLANNING_MODE', 'false').lower() == 'true'

def create_tox_ini(dry_run=False):
    """Create tox.ini file for Ansible testing"""
    if dry_run or PLANNING_MODE:
        print("[DRY RUN] Would create tox.ini")
        print("  Environments: py38, py39, py310, py311")
        print("  Test frameworks: pytest, ansible-lint, molecule, docker")
        return True
    
    tox_content = """[tox]
envlist = py{38,39,310,311}
skipsdist = True

[testenv]
deps = 
    pytest
    pytest-xdist
    ansible-core
    ansible-lint
    molecule
    docker
commands = 
    pytest tests/ -v
    ansible-lint
    molecule test

[testenv:py38-docker]
basepython = python3.8
deps = 
    {[testenv]deps}
    docker
commands = 
    molecule test -s docker

[testenv:py39-docker]
basepython = python3.9
deps = 
    {[testenv]deps}
    docker
commands = 
    molecule test -s docker

[testenv:molecule]
deps = 
    molecule
    docker
    testinfra
commands = 
    molecule test

[testenv:lint]
deps = 
    ansible-lint
    yamllint
    flake8
commands = 
    ansible-lint
    yamllint .
    flake8 tests/
"""
    
    with open('tox.ini', 'w') as f:
        f.write(tox_content)
    
    print("Created tox.ini")
    return True

def create_molecule_config(role_name, dry_run=False):
    """Create molecule configuration for a role"""
    if dry_run or PLANNING_MODE:
        print(f"[DRY RUN] Would create molecule config for role: {role_name}")
        print("  Platforms: ubuntu-20.04, centos-8")
        print("  Verifier: testinfra")
        return True
    
    molecule_dir = Path(role_name) / 'molecule' / 'default'
    molecule_dir.mkdir(parents=True, exist_ok=True)
    
    # Create molecule.yml
    molecule_config = {
        'dependency': {
            'name': 'galaxy'
        },
        'driver': {
            'name': 'docker'
        },
        'platforms': [
            {
                'name': 'ubuntu-20.04',
                'image': 'ubuntu:20.04',
                'pre_build_image': True
            },
            {
                'name': 'centos-8',
                'image': 'centos:8',
                'pre_build_image': True
            }
        ],
        'provisioner': {
            'name': 'ansible'
        },
        'verifier': {
            'name': 'testinfra'
        }
    }
    
    with open(molecule_dir / 'molecule.yml', 'w') as f:
        yaml.dump(molecule_config, f, default_flow_style=False)
    
    # Create converge.yml
    converge_content = f"""---
- name: Converge
  hosts: all
  tasks:
    - name: Include {role_name}
      include_role:
        name: {role_name}
"""
    
    with open(molecule_dir / 'converge.yml', 'w') as f:
        f.write(converge_content)
    
    # Create verify.yml
    verify_content = """---
- name: Verify
  hosts: all
  tasks:
    - name: Example assertion
      assert:
        that:
          - true
"""
    
    with open(molecule_dir / 'verify.yml', 'w') as f:
        f.write(verify_content)
    
    print(f"Created molecule config for role: {role_name}")
    return True

def run_tox(env=None, dry_run=False):
    """Run tox tests"""
    if dry_run or PLANNING_MODE:
        print(f"[DRY RUN] Would run tox tests for env: {env or 'all'}")
        cmd = ['tox']
        if env:
            cmd.extend(['-e', env])
        print(f"  Command: {' '.join(cmd)}")
        return True
    
    cmd = ['tox']
    if env:
        cmd.extend(['-e', env])
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"✓ Tox tests passed for env: {env or 'all'}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Tox tests failed: {e}")
        return False

def run_docker_tests(dry_run=False):
    """Run Docker-based tests"""
    print("Running Docker tests...")
    return run_tox('py39-docker', dry_run)

def setup_test_environment(dry_run=False):
    """Setup complete test environment"""
    if dry_run or PLANNING_MODE:
        print("[DRY RUN] Would setup test environment")
        print("  Files: tox.ini, tests/test_ansible.py")
        print("  Directories: tests/, tests/unit/, tests/integration/")
        return True
    
    print("Setting up test environment...")
    
    # Create tox.ini
    create_tox_ini()
    
    # Create test directory structure
    test_dirs = ['tests', 'tests/unit', 'tests/integration']
    for dir_name in test_dirs:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
    
    # Create test files
    test_content = """import pytest
from ansible.utils.display import Display

def test_ansible_import():
    \"\"\"Test that Ansible can be imported\"\"\"
    try:
        import ansible
        assert True
    except ImportError:
        assert False, "Cannot import Ansible"

def test_playbook_syntax():
    \"\"\"Test playbook syntax\"\"\"
    # Add your playbook syntax tests here
    pass
"""
    
    with open('tests/test_ansible.py', 'w') as f:
        f.write(test_content)
    
    print("✓ Test environment setup complete")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Ansible tox testing framework')
    parser.add_argument('action', choices=['setup', 'run', 'docker', 'molecule'], help='Action to perform')
    parser.add_argument('target', nargs='?', help='Target environment or role name')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    
    args = parser.parse_args()
    
    success = False
    if args.action == "setup":
        success = setup_test_environment(args.dry_run)
    elif args.action == "run":
        success = run_tox(args.target, args.dry_run)
    elif args.action == "docker":
        success = run_docker_tests(args.dry_run)
    elif args.action == "molecule" and args.target:
        success = create_molecule_config(args.target, args.dry_run)
    
    sys.exit(0 if success else 1)