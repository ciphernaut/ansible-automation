# Testing with Docker and Tox

## Tox Configuration

### Complete tox.ini
```ini
[tox]
envlist = py{38,39,310,311},lint,molecule
skipsdist = True

[testenv]
deps = 
    pytest
    pytest-xdist
    ansible-core
    ansible-lint
    molecule
    docker
    testinfra
commands = 
    pytest tests/ -v

[testenv:lint]
deps = 
    ansible-lint
    yamllint
    flake8
commands = 
    ansible-lint
    yamllint .
    flake8 tests/

[testenv:molecule]
deps = 
    molecule
    docker
    testinfra
commands = 
    molecule test

[testenv:py38-docker]
basepython = python3.8
deps = 
    {[testenv]deps}
    docker
commands = 
    molecule test -s docker-ubuntu20

[testenv:py39-docker]
basepython = python3.9
deps = 
    {[testenv]deps}
    docker
commands = 
    molecule test -s docker-centos8
```

## Docker Testing Targets

### Ubuntu 20.04
```yaml
# molecule/ubuntu20/molecule.yml
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: ubuntu-20.04
    image: ubuntu:20.04
    pre_build_image: true
    command: /sbin/init
provisioner:
  name: ansible
verifier:
  name: testinfra
```

### CentOS 8
```yaml
# molecule/centos8/molecule.yml
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: centos-8
    image: centos:8
    pre_build_image: true
    command: /usr/lib/systemd/systemd
provisioner:
  name: ansible
verifier:
  name: testinfra
```

## Test Structure

### Unit Tests
```python
# tests/test_playbook.py
import pytest
import yaml
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager

def test_playbook_syntax():
    """Test playbook YAML syntax"""
    with open('site.yml') as f:
        playbook = yaml.safe_load(f)
    assert isinstance(playbook, list)

def test_task_modules():
    """Test task module usage"""
    loader = DataLoader()
    vm = VariableManager()
    # Test module loading
    pass
```

### Integration Tests
```python
# tests/test_integration.py
import pytest
from testinfra.utils.ansible_runner import AnsibleRunner

def test_package_installed(host):
    """Test that packages are installed"""
    package = host.package('nginx')
    assert package.is_installed

def test_service_running(host):
    """Test that services are running"""
    service = host.service('nginx')
    assert service.is_running
```

## Molecule Testing

### Default Scenario
```yaml
# molecule/default/molecule.yml
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: instance
    image: ubuntu:20.04
    pre_build_image: true
provisioner:
  name: ansible
verifier:
  name: testinfra
```

### Converge Playbook
```yaml
# molecule/default/converge.yml
---
- name: Converge
  hosts: all
  tasks:
    - name: Include role
      include_role:
        name: myrole
```

### Verify Tests
```python
# molecule/default/tests/test_default.py
import pytest

def test_host_file(host):
    """Test host file exists"""
    assert host.file('/etc/hosts').exists

def test_package(host):
    """Test package installation"""
    assert host.package('curl').is_installed
```

## CI/CD Testing

### GitHub Actions
```yaml
# .github/workflows/test.yml
name: Test Ansible
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install tox
      run: pip install tox
    
    - name: Run tox
      run: tox -e py${{ matrix.python-version }}
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    stages {
        stage('Test') {
            parallel {
                stage('Lint') {
                    steps {
                        sh 'tox -e lint'
                    }
                }
                stage('Molecule') {
                    steps {
                        sh 'tox -e molecule'
                    }
                }
            }
        }
    }
}
```

## Best Practices

1. **Test multiple platforms** - Ubuntu, CentOS, Alpine
2. **Use check mode** - Dry run testing
3. **Idempotency** - Test re-runs
4. **Coverage** - Test all roles
5. **Automation** - CI/CD integration

## Debugging

### Verbose Testing
```bash
# Verbose molecule
molecule test --debug

# Verbose ansible
ansible-playbook -vvv playbook.yml

# Docker logs
docker logs container_name
```

### Test Isolation
```bash
# Clean test environment
molecule destroy

# Rebuild from scratch
molecule test --destroy-always
```