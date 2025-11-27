---
name: ansible-automation
description: Comprehensive Ansible automation skill for playbook generation, role management, inventory configuration, deployment workflows, testing with Docker targets, community module integration, and validation features. Use when creating Ansible playbooks, roles, collections, linting, debugging, check mode, or deployment automation. Also for community module discovery, tox testing, and documentation.
---

# Ansible Automation Skill

## Quick Start

**Generate Playbook**
```bash
python3 scripts/generate_playbook.py config.yml playbook.yml
```

**Create Role**
```bash
python3 scripts/role_manager.py role myrole
```

**Setup Inventory**
```bash
python3 scripts/inventory_manager.py create_inventory hosts.json inventory.yml
```

**Validate**
```bash
python3 scripts/validate.py playbook.yml inventory.yml
```

**Install Community Modules**
```bash
python3 scripts/community_manager.py install_common
```

**Setup Testing**
```bash
python scripts/tox_testing.py setup
```

## Core Features

### 1. Playbook Generation
- Template-based playbook creation
- YAML configuration input
- Task automation
- Variable handling

### 2. Role Management
- Standard role structure
- Task organization
- Handler management
- Variable precedence

### 3. Inventory Configuration
- Static and dynamic inventory
- SSH configuration
- Connection methods
- Group management

### 4. Deployment Workflows
- Rolling deployments
- Blue-green deployments
- Canary deployments
- CI/CD integration

### 5. Testing Framework
- Tox integration
- Docker targets
- Molecule testing
- Validation checks

### 6. Community Integration
- Module discovery
- Collection management
- Custom modules
- Best practices

## Resources

- [INVENTORY.md](references/INVENTORY.md) - Inventory management
- [ROLES.md](references/ROLES.md) - Role patterns
- [DEPLOYMENT.md](references/DEPLOYMENT.md) - Deployment workflows
- [VALIDATION.md](references/VALIDATION.md) - Linting and testing
- [COMMUNITY.md](references/COMMUNITY.md) - Community modules

## Scripts

- `generate_playbook.py` - Create playbooks from config
- `role_manager.py` - Manage roles and collections
- `inventory_manager.py` - Handle inventory and SSH
- `validate.py` - Run validation and linting
- `community_manager.py` - Community modules
- `tox_testing.py` - Testing framework

## Usage Patterns

**Development:**
1. Generate playbook skeleton
2. Create roles for components
3. Setup inventory
4. Test with check mode
5. Validate and lint
6. Deploy to staging

**Production:**
1. Use check mode first
2. Run with verbose logging
3. Monitor deployment
4. Verify services
5. Rollback if needed