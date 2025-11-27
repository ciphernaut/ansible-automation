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

## Change Verification System

### Purpose
Detects debugging changes made directly on targets that aren't captured in Ansible code using `ansible-playbook --check --diff`.

### When to Use
- After manual debugging sessions on target systems
- Before committing changes to version control
- During code reviews to ensure completeness
- When transitioning from development to production

### Verification Modes
- **Basic**: Quick check for untracked changes
- **Report**: Detailed JSON output for automation
- **Quiet**: Silent operation with exit codes
- **Integration**: Built into progressive deployment

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

### Change Verification Mode
```bash
# Verify debugging changes are captured in Ansible code
python3 scripts/verify_changes.py site.yml                           # Basic verification
python3 scripts/verify_changes.py deploy.yml -i inventory/hosts      # With inventory
python3 scripts/verify_changes.py debug.yml --extra-vars env=dev     # With variables
python3 scripts/verify_changes.py --report site.yml > changes.json  # Detailed report
python3 scripts/verify_changes.py --quiet playbook.yml && echo "OK"  # Silent check
```

### Progressive Deployment with Change Verification
```bash
# Deploy with automatic change verification
python3 scripts/deploy_helper.py deploy_config.yml inventory.yml --verify-changes

# Progressive deployment with verification at each stage
python3 scripts/deploy_helper.py --progressive --verify-changes config.yml inventory.yml
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