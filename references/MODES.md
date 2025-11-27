# Mode Configuration for Ansible Automation Skill

## Environment Variables

### Planning Mode Detection
```bash
export OPENCODE_PLANNING_MODE=true   # Enable planning mode
export OPENCODE_PLANNING_MODE=false  # Disable planning mode (default)
```

## Safe Operations (Planning Mode)

### Always Safe
- YAML syntax validation
- File generation with --dry-run
- Read-only operations (list, info)
- Template and configuration creation

### Safe with Flags
- ansible-lint with --dry-run
- ansible-playbook --check with --dry-run
- Module search with --dry-run
- Collection installation with --dry-run

## Risky Operations (Execution Mode Only)

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

### Planning Mode
```bash
# Set environment
export OPENCODE_PLANNING_MODE=true

# All operations become dry-run automatically
python3 scripts/validate.py playbook.yml inventory.yml
python3 scripts/community_manager.py install community.general
python3 scripts/tox_testing.py run py39
```

### Manual Dry-Run
```bash
# Override with explicit flag
python3 scripts/validate.py playbook.yml --dry-run
python3 scripts/role_manager.py role myrole --dry-run
python3 scripts/inventory_manager.py create_inventory hosts.json inventory.yml --dry-run
```

### Execution Mode
```bash
# Disable planning mode
export OPENCODE_PLANNING_MODE=false

# Run full operations
python3 scripts/community_manager.py install community.general
python3 scripts/tox_testing.py run py39
```