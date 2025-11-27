# Mode Configuration for Ansible Automation Skill

## OpenCode Mode Integration

This skill now relies on OpenCode's built-in mode system instead of custom environment variables.

### OpenCode Modes
- **Build Mode**: Full access to all tools and operations (default)
- **Plan Mode**: Read-only access for analysis and planning

### Safe Operations

#### Always Safe
- YAML syntax validation
- File generation with --dry-run
- Read-only operations (list, info)
- Template and configuration creation

#### Safe with --dry-run Flag
- ansible-lint with --dry-run
- ansible-playbook --check with --dry-run
- Module search with --dry-run
- Collection installation with --dry-run

## Risky Operations (Build Mode Only)

### System Modifications
- Package installation without --dry-run
- Collection installation without --dry-run
- Tox execution without --dry-run
- Docker operations without --dry-run

### External Commands
- ansible-galaxy commands (without --dry-run)
- tox commands (without --dry-run)
- molecule commands (without --dry-run)

## Usage Examples

### Planning with --dry-run
```bash
# All operations in dry-run mode
python3 scripts/validate.py playbook.yml inventory.yml --dry-run
python3 scripts/community_manager.py install community.general --dry-run
python3 scripts/tox_testing.py run py39 --dry-run
python3 scripts/role_manager.py role myrole --dry-run
python3 scripts/inventory_manager.py create_inventory hosts.json inventory.yml --dry-run
python3 scripts/generate_playbook.py --template webserver --dry-run
python3 scripts/deploy_helper.py deploy_config.yml inventory.yml --dry-run
```

### Execution in Build Mode
```bash
# Run full operations (requires build mode)
python3 scripts/community_manager.py install community.general
python3 scripts/tox_testing.py run py39
python3 scripts/validate.py playbook.yml inventory.yml
python3 scripts/deploy_helper.py deploy_config.yml inventory.yml
python3 scripts/deploy_helper.py deploy_config.yml inventory.yml --resume
```

### Progressive Deployment Mode
The `deploy_helper.py` script provides enhanced deployment capabilities:

```bash
# Progressive deployment with hardware optimization
python3 scripts/deploy_helper.py deploy_config.yml inventory.yml

# Resume from failed stage
python3 scripts/deploy_helper.py deploy_config.yml inventory.yml --resume

# Check deployment status
python3 scripts/deploy_helper.py --status

# Reset deployment state
python3 scripts/deploy_helper.py --reset

# Dry-run with verbose output
python3 scripts/deploy_helper.py deploy_config.yml inventory.yml --dry-run --verbose
```

### Hardware-Aware Optimization
The deployment system automatically detects hardware profiles and optimizes:
- **High Performance**: 16+ CPU cores, 32GB+ RAM → 20 forks, async enabled
- **Standard**: 8+ CPU cores, 16GB+ RAM → 10 forks, async enabled  
- **Minimal**: 4+ CPU cores, 8GB+ RAM → 5 forks, longer timeouts
- **Resource Constrained**: Lower specs → 2 forks, conservative settings

### Mode Switching
Use OpenCode's mode switching (Tab key by default) to switch between Plan and Build modes.