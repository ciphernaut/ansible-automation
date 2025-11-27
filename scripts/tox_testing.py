#!/usr/bin/env python3
"""
Ansible Tox Testing Framework
Sets up and runs tox tests with Docker targets
"""

import subprocess
import sys
import yaml
from pathlib import Path

def create_tox_ini():
    """Create tox.ini file for Ansible testing"""
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

def create_molecule_config(role_name):
    """Create molecule configuration for a role"""
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

def run_tox(env=None):
    """Run tox tests"""
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

def run_docker_tests():
    """Run Docker-based tests"""
    print("Running Docker tests...")
    return run_tox('py39-docker')

def setup_test_environment():
    """Setup complete test environment"""
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tox_testing.py <setup|run|docker|molecule> [role_name]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "setup":
        setup_test_environment()
    elif action == "run":
        env = sys.argv[2] if len(sys.argv) > 2 else None
        run_tox(env)
    elif action == "docker":
        run_docker_tests()
    elif action == "molecule" and len(sys.argv) > 2:
        create_molecule_config(sys.argv[2])
    else:
        print("Invalid action or missing arguments")
        sys.exit(1)