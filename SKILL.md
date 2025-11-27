---
name: ansible-automation
description: Comprehensive Ansible automation skill for playbook generation, role management, inventory configuration, deployment workflows, testing with Docker targets, community module integration, and validation features. Use when creating Ansible playbooks, roles, collections, linting, debugging, check mode, or deployment automation. Also for community module discovery, tox testing, and documentation. Supports planning mode with dry-run capabilities for safe preview of operations.
---

# Ansible Automation Skill

## Quick Start

**Generate Playbook**
```bash
python3 scripts/generate_playbook.py config.yml playbook.yml
python3 scripts/generate_playbook.py config.yml playbook.yml --dry-run  # Planning
```

**Create Role**
```bash
python3 scripts/role_manager.py role myrole
python3 scripts/role_manager.py role myrole --dry-run  # Planning
```

**Setup Inventory**
```bash
python3 scripts/inventory_manager.py create_inventory hosts.json inventory.yml
python3 scripts/inventory_manager.py create_inventory hosts.json inventory.yml --dry-run  # Planning
```

**Validate**
```bash
python3 scripts/validate.py playbook.yml inventory.yml
python3 scripts/validate.py playbook.yml --syntax-only  # Safe validation
python3 scripts/validate.py playbook.yml inventory.yml --dry-run  # Planning
```

**Community Modules**
```bash
python3 scripts/community_manager.py list  # Safe - read only
python3 scripts/community_manager.py search nginx --dry-run  # Planning
python3 scripts/community_manager.py install community.general --dry-run  # Planning
```

**Testing**
```bash
python3 scripts/tox_testing.py setup  # Safe - file creation
python3 scripts/tox_testing.py run --dry-run  # Planning
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

### Planning Workflow (Safe Operations)
1. Use `--dry-run` flags for all operations
2. Validate syntax with `--syntax-only`
3. Preview file generation before creation
4. List and search community modules (read-only)
5. Generate test environments without execution

### Development Workflow
1. Generate playbook skeleton with `--dry-run`
2. Create roles with preview mode
3. Setup inventory and validate structure
4. Test with check mode and dry-run
5. Validate and lint with safe options
6. Deploy to staging when ready

### Production Deployment
1. Use check mode first (`--check`)
2. Run with verbose logging
3. Monitor deployment
4. Verify services
5. Rollback if needed

### Mode-Specific Safety
- **OpenCode Plan Mode:** Read-only access, no file modifications or system commands
- **OpenCode Build Mode:** Full access to all tools and operations
- **Safe Operations:** YAML validation, file generation with --dry-run, read-only queries
- **Risky Operations:** Package installation, external execution require build mode