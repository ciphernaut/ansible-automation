# Ansible Validation and Linting

## ansible-lint Configuration

### .ansible-lint Configuration
```yaml
# .ansible-lint
exclude_paths:
  - .cache/
  - .pytest_cache/
  - .tox/

skip_list:
  - '204'  # Lines should be no longer than 120 chars
  - '303'  # Using command rather than module
  - '501'  # command should not be used in place of module

rulesdir:
  - ./rules/
```

## Common Linting Rules

### 1. YAML Syntax
```bash
# Check YAML syntax
ansible-playbook --syntax-check playbook.yml

# Use yamllint
yamllint .
```

### 2. Best Practices
```yaml
# Good: Use specific modules
- name: Install package
  package:
    name: nginx
    state: present

# Bad: Use shell when module exists
- name: Install nginx  # [303]
  shell: apt-get install -y nginx
```

### 3. Security Rules
```yaml
# Good: Use vault for secrets
- name: Set password
  user:
    name: admin
    password: "{{ vault_admin_password }}"

# Bad: Plain text passwords
- name: Set password  # [501]
  user:
    name: admin
    password: secret123
```

## Validation Workflow

### Pre-commit Hook
```bash
#!/bin/sh
# .git/hooks/pre-commit

# Run ansible-lint
ansible-lint

# Run syntax check
find . -name "*.yml" -exec ansible-playbook --syntax-check {} \;

# Run yamllint
yamllint .
```

### CI/CD Validation
```yaml
# GitHub Actions
- name: Validate Ansible
  run: |
    ansible-lint
    ansible-playbook --syntax-check site.yml
    yamllint .
```

## Testing Strategies

### 1. Unit Testing
```python
# tests/test_playbook.py
import pytest
from ansible.utils.display import Display

def test_playbook_syntax():
    """Test playbook YAML syntax"""
    # Load and validate playbook
    pass

def test_task_modules():
    """Test that tasks use correct modules"""
    # Check task module usage
    pass
```

### 2. Integration Testing
```yaml
# molecule/default/molecule.yml
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: ubuntu-20.04
    image: ubuntu:20.04
provisioner:
  name: ansible
verifier:
  name: testinfra
```

### 3. End-to-End Testing
```bash
# Test in staging environment
ansible-playbook -i staging site.yml --check
ansible-playbook -i staging site.yml
```

## Custom Rules

### Custom Linting Rule
```python
# rules/CustomRule.py
from ansiblelint.rules import AnsibleLintRule

class CustomRule(AnsibleLintRule):
    id = 'CUSTOM001'
    shortdesc = 'Custom rule description'
    description = 'Detailed description of custom rule'
    
    def matchtask(self, task, file):
        # Custom validation logic
        return False
```

## Validation Commands

### Complete Validation
```bash
#!/bin/bash
# validate.sh

echo "Running ansible-lint..."
ansible-lint

echo "Checking YAML syntax..."
find . -name "*.yml" -exec ansible-playbook --syntax-check {} \;

echo "Running yamllint..."
yamllint .

echo "Running molecule tests..."
molecule test

echo "Validation complete!"
```

### Check Mode Testing
```bash
# Dry run deployment
ansible-playbook -i production site.yml --check --diff

# Verbose check mode
ansible-playbook -i production site.yml --check -vvv
```

## Best Practices

1. **Automate validation** in CI/CD pipeline
2. **Use pre-commit hooks** for local validation
3. **Test in staging** before production
4. **Custom rules** for organization standards
5. **Regular updates** of linting rules