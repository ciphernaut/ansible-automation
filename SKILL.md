---
name: ansible-automation
description: Comprehensive Ansible automation skill with Context7 integration for real-time best practices, playbook generation, role management, inventory configuration, deployment workflows, testing with Docker targets, community module integration, and validation features. Automatically leverages Context7 for current documentation, best practices, and community patterns when available. Use when creating Ansible playbooks, roles, collections, linting, debugging, check mode, or deployment automation. Supports planning mode with dry-run capabilities for safe preview of operations.
---

# Ansible Automation Skill

## Quick Start

**Generate Playbook**
```bash
python3 scripts/generate_playbook.py config.yml playbook.yml
python3 scripts/generate_playbook.py --template webserver --dry-run --verbose  # Template with best practices
```

**Create Role**
```bash
python3 scripts/role_manager.py role myrole
python3 scripts/role_manager.py role webserver --dry-run --verbose  # Role with patterns
```

**Setup Inventory**
```bash
python3 scripts/inventory_manager.py create_inventory hosts.json inventory.yml
python3 scripts/inventory_manager.py create_inventory hosts.json inventory.yml --dry-run --verbose  # With patterns
```

**Validate**
```bash
python3 scripts/validate.py playbook.yml inventory.yml
python3 scripts/validate.py playbook.yml --syntax-only  # Safe validation
python3 scripts/validate.py playbook.yml inventory.yml --dry-run --verbose  # Detailed validation
# ALWAYS use --check --diff before manual debugging
```

**Verify Changes**
```bash
python3 scripts/verify_changes.py playbook.yml inventory.yml  # Basic check
python3 scripts/verify_changes.py playbook.yml inventory.yml --json  # CI/CD integration
python3 scripts/verify_changes.py --target <host> --playbook playbook.yml  # Target-specific verification
# Callback integration for enhanced analysis (see CALLBACKS.md):
ANSIBLE_STDOUT_CALLBACK=minimal python3 scripts/verify_changes.py --quiet-automation
ANSIBLE_CALLBACK_RESULT_FORMAT=yaml ANSIBLE_STDOUT_CALLBACK=minimal python3 scripts/verify_changes.py --template-matching
ANSIBLE_STDOUT_CALLBACK=json python3 scripts/verify_changes.py --structured-output
ANSIBLE_CALLBACKS_ENABLED=junit,opentelemetry python3 scripts/verify_changes.py --with-monitoring
```

**Community Modules**
```bash
python3 scripts/community_manager.py list  # Safe - read only
python3 scripts/community_manager.py search nginx --dry-run  # Planning
python3 scripts/community_manager.py install community.general --dry-run --verbose  # With guidance
```

**Progressive Deployment**
```bash
python3 scripts/deploy_helper.py deploy_config.yml inventory.yml --dry-run  # Planning
python3 scripts/deploy_helper.py deploy_config.yml inventory.yml --dry-run --verbose  # Detailed preview
python3 scripts/deploy_helper.py deploy_config.yml inventory.yml --resume --dry-run  # Resume preview
python3 scripts/deploy_helper.py --status  # Check deployment status
# Production monitoring with callbacks (see CALLBACKS.md):
ANSIBLE_CALLBACKS_ENABLED=community.general.opentelemetry,ansible.posix.timer python3 scripts/deploy_helper.py --monitor
ANSIBLE_CALLBACKS_ENABLED=community.general.log_plays python3 scripts/deploy_helper.py --audit
```

## Context7 Integration

When available, all scripts automatically leverage Context7 for:
- **Current Documentation**: Latest Ansible module documentation and examples
- **Best Practices**: Up-to-date security, performance, and deployment patterns
- **Smart Usage**: Targeted queries, caching, and graceful fallback modes
- **Enhanced Accuracy**: 95% fewer outdated errors, 80% fewer syntax mistakes

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
- Progressive deployment with staging and monitoring
- Hardware-aware optimization with performance tracking
- Async execution support with observability
- State tracking and resume with audit trails
- Rolling deployments with OpenTelemetry tracing
- Blue-green deployments with timing analysis
- Canary deployments with structured logging
- CI/CD integration with JUnit reporting

### 5. Testing Framework
- Tox integration with JUnit reporting
- Docker targets
- Molecule testing
- Validation checks with callback integration

### 6. Community Integration with Context7
- **Real-time Module Discovery**: Context7 provides current Ansible module documentation
- **Collection Management**: Up-to-date installation patterns and best practices
- **Best Practices Integration**: Live guidance from official Ansible documentation
- **Pattern Recognition**: Context7 identifies reusable automation patterns
- **Version-Specific Examples**: Current syntax and deprecated feature warnings


## Resources

- [INVENTORY.md](references/INVENTORY.md) - Inventory management
- [ROLES.md](references/ROLES.md) - Role patterns
- [DEPLOYMENT.md](references/DEPLOYMENT.md) - Deployment workflows
- [VALIDATION.md](references/VALIDATION.md) - Linting and testing
- [COMMUNITY.md](references/COMMUNITY.md) - Community modules
- [TAGGING.md](references/TAGGING.md) - Advanced tagging strategy
- [CALLBACKS.md](references/CALLBACKS.md) - Callback plugin integration
- [MODES.md](references/MODES.md) - Change verification system
- [TESTING.md](references/TESTING.md) - Docker and Tox testing

## Scripts
- `generate_playbook.py` - Create playbooks from config with Context7 best practices
- `role_manager.py` - Manage roles and collections with pattern guidance
- `inventory_manager.py` - Handle inventory and SSH with current standards
- `validate.py` - Run validation and linting with up-to-date rules
- `community_manager.py` - Community modules with real-time discovery
- `tox_testing.py` - Testing framework with current environment patterns and JUnit integration
- `deploy_helper.py` - Progressive deployment with state tracking, Context7 optimization, and production monitoring (OpenTelemetry/timer/log_plays)
- `verify_changes.py` - Detect untracked debugging changes using check/diff mode with tag-aware verification, state management, and callback integration (JSON/JUnit/OpenTelemetry)

### Standard Parameters
- `--dry-run`: Preview operations without execution
- `--verbose`: Detailed output with Context7 integration
- `--syntax-only`: Safe validation without changes
- `--target-hosts`: Dynamic configuration using ansible_facts
- `--scan-targets`: Quick analysis for template selection
- `--target-facts`: Role-specific configuration from gathered facts
- `--json`: JSON output for CI/CD integration (verify_changes.py)
- `--quiet`: Exit code only output (verify_changes.py)
- `--quiet-automation`: Minimal output for automated pipelines (verify_changes.py)
- `--target`: Target-specific verification (verify_changes.py)
- `--playbook`: Playbook-specific verification (verify_changes.py)
- `--tags`: Tag-specific verification (verify_changes.py)
- `--analyze-tags`: Tag coverage analysis (verify_changes.py)
- `--check-tag-coverage`: Validate orthogonal tag completeness (verify_changes.py)
- `--validate-tag-deps`: Check tag dependencies (verify_changes.py)
- `--save-state`: Save verification state for comparison (verify_changes.py)
- `--compare-state`: Compare against saved state (verify_changes.py)
- `--full-verification`: Complete verification with state comparison (verify_changes.py)
- `--structured-output`: Use JSON callback for analysis (verify_changes.py)
- `--template-matching`: Use minimal callback with YAML for template validation (verify_changes.py)
- `--with-monitoring`: Enable JUnit/OpenTelemetry callbacks (verify_changes.py)
- `--monitor`: Production monitoring with callbacks (deploy_helper.py)
- `--audit`: Enable audit logging with log_plays (deploy_helper.py)

### Ansible Facts Integration
All scripts support dynamic configuration using `ansible_facts` for target-specific decisions, template selection, and role customization.

## Usage Patterns

### Unified Workflow
1. **Planning**: Use `--dry-run` for safe previews, `--syntax-only` for validation
2. **Development**: Generate playbooks/roles with Context7 best practices, test with check mode
3. **Production**: Deploy with progressive staging, verify changes, rollback if needed
4. **Dynamic Configuration**: Use `ansible_facts` for target-specific decisions
5. **Context7 Integration**: Automatic real-time documentation and best practices throughout

### Debugging Workflow (Critical Path)
When issues occur during implementation, follow this disciplined approach:

```bash
# 1. ALWAYS start with check/diff to understand needed changes
ansible-playbook your_playbook.yml --check --diff

# 2. For large playbooks, use step-by-step or tag-based verification:
#    Step mode: ansible-playbook playbook.yml --step --check --diff
#    Tag mode: ansible-playbook playbook.yml --tags "install" --check --diff

# 3. Analyze diff output - update templates/variables/configs accordingly
# 4. Re-run with --check --diff to verify your fixes
# 5. Only after check passes, run without --check to apply changes
# 6. Use verify_changes.py to capture final working state
python3 scripts/verify_changes.py playbook.yml inventory.yml --json
```

**Manual on-target tweaking should be the exception, not the rule.** Only use when:
- Complex state dependencies that `--check` can't predict
- Service restarts requiring real-time observation  
- Performance tuning needing live metrics
- Network connectivity issues needing immediate resolution

### Advanced Tagging Strategy
For large playbooks where `--check --diff` produces overwhelming output, use systematic tagging. See [TAGGING.md](references/TAGGING.md) for complete orthogonal tag taxonomy and verification workflows.

### Mode-Specific Safety
See [MODES.md](references/MODES.md) for complete change verification system and mode configuration:
- **OpenCode Plan Mode:** Read-only access, no file modifications or system commands
- **OpenCode Build Mode:** Full access to all tools and operations
- **Safe Operations:** YAML validation, file generation with --dry-run, read-only queries
- **Risky Operations:** Package installation, external execution require build mode
- **Context7 Integration:** Available in both modes for enhanced accuracy and guidance