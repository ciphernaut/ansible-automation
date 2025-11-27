# Ansible Automation Skill

Comprehensive Ansible automation skill for playbook generation, role management, inventory configuration, deployment workflows, testing with Docker targets, community module integration, and validation features.

## Quick Start

### Generate Playbook
```bash
python3 scripts/generate_playbook.py config.yml playbook.yml
```

### Create Role
```bash
python3 scripts/role_manager.py role myrole
```

### Setup Inventory
```bash
python3 scripts/inventory_manager.py create_inventory hosts.json inventory.yml
```

### Validate
```bash
python3 scripts/validate.py playbook.yml inventory.yml
```

### Install Community Modules
```bash
python3 scripts/community_manager.py install_common
```

### Setup Testing
```bash
python3 scripts/tox_testing.py setup
```

## Features

- **Playbook Generation** - Template-based creation
- **Role Management** - Standard structure & handlers
- **Inventory Configuration** - SSH & connection methods
- **Deployment Workflows** - Rolling, blue-green, canary
- **Testing Framework** - Tox + Docker targets
- **Community Integration** - Module discovery & installation
- **Validation** - ansible-lint, syntax checks, check mode

## Requirements

- Python 3.8+
- Ansible Core
- ansible-lint
- molecule (for testing)
- Docker (for container testing)

## Installation

```bash
git clone https://github.com/your-username/ansible-automation.git
cd ansible-automation
chmod +x scripts/*.py
```

## Usage

See [SKILL.md](SKILL.md) for complete documentation and usage patterns.

## License

MIT License - see LICENSE file for details.