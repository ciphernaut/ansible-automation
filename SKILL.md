---
name: ansible-automation
description: Comprehensive Ansible automation skill with Context7 integration for real-time best practices, playbook generation, role management, inventory configuration, deployment workflows, testing with Docker targets, community module integration, and validation features. Automatically leverages Context7 for current documentation, best practices, and community patterns when available. Use when creating Ansible playbooks, roles, collections, linting, debugging, check mode, or deployment automation. Supports planning mode with dry-run capabilities for safe preview of operations.
---

# Ansible Automation Skill

## Quick Start

**Core Ansible Commands**
```bash
# Syntax validation
ansible-playbook --syntax-check playbook.yml

# Check mode - see what would change
ansible-playbook --check playbook.yml
ansible-playbook --check --diff playbook.yml  # Show actual changes

# Run with specific inventory
ansible-playbook -i inventory.yml playbook.yml

# Target specific hosts/groups
ansible-playbook -i inventory.yml --limit webservers playbook.yml

# Run specific tags
ansible-playbook --tags database,config playbook.yml

# Verbose output for debugging
ansible-playbook -v playbook.yml
ansible-playbook -vvv playbook.yml  # Very verbose
```

**Change Verification**
```bash
# Basic verification - check for untracked changes
ansible-playbook --check --diff playbook.yml

# Tag-based verification
ansible-playbook --check --diff --tags install playbook.yml
ansible-playbook --check --diff --tags config playbook.yml

# Target-specific verification
ansible-playbook --check --diff --limit host01 playbook.yml

# With callbacks for enhanced analysis (see CALLBACKS.md):
ANSIBLE_STDOUT_CALLBACK=minimal ansible-playbook --check --diff playbook.yml
ANSIBLE_CALLBACK_RESULT_FORMAT=yaml ANSIBLE_STDOUT_CALLBACK=minimal ansible-playbook --check --diff playbook.yml
ANSIBLE_STDOUT_CALLBACK=json ansible-playbook --check --diff playbook.yml
ANSIBLE_CALLBACKS_ENABLED=junit,opentelemetry ansible-playbook --check --diff playbook.yml
```

**Advanced Workflows**
```bash
# List available tags for planning
ansible-playbook --list-tags playbook.yml

# List tasks for verification
ansible-playbook --list-tasks playbook.yml

# Step-by-step execution for debugging
ansible-playbook --step --check --diff playbook.yml

# Dry run with extra variables
ansible-playbook --check --diff --extra-vars "env=dev version=1.2" playbook.yml
```

**Helper Scripts (Complex Workflows Only)**
```bash
# Progressive deployment with state management
python3 scripts/deploy_helper.py deploy_config.yml inventory.yml

# Generate playbooks from templates
python3 scripts/generate_playbook.py --template webserver --dry-run

# Community module management
python3 scripts/community_manager.py search nginx --dry-run
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

## Scripts (Complex Workflows Only)
- `generate_playbook.py` - Create playbooks from templates with Context7 best practices
- `deploy_helper.py` - Progressive deployment with state tracking and production monitoring
- `community_manager.py` - Community module discovery and management
- `tox_testing.py` - Testing framework with Docker targets and JUnit integration

**Note**: Most operations use direct ansible commands. Scripts are reserved for complex multi-step workflows that provide significant value beyond basic command execution.

### Core Ansible Parameters
- `--syntax-check`: Validate playbook syntax without execution
- `--check`: Dry run mode - show what would change without making changes
- `--diff`: Show actual differences when used with --check
- `--list-tags`: Display all available tags in playbook
- `--list-tasks`: Display all tasks in playbook
- `--tags`: Run only tasks with specified tags
- `--skip-tags`: Skip tasks with specified tags
- `--limit`: Restrict execution to specific hosts/groups
- `--extra-vars`: Pass additional variables
- `-v, -vv, -vvv`: Verbose output levels for debugging
- `--step`: Interactive step-by-step execution

### Callback Environment Variables
- `ANSIBLE_STDOUT_CALLBACK=minimal`: Ultra-compact output
- `ANSIBLE_CALLBACK_RESULT_FORMAT=yaml`: YAML results for template matching
- `ANSIBLE_CALLBACK_FORMAT_PRETTY=true`: Readable YAML formatting
- `ANSIBLE_STDOUT_CALLBACK=json`: Structured JSON output
- `ANSIBLE_CALLBACKS_ENABLED=junit,opentelemetry`: Enhanced monitoring

### Script Parameters (Complex Workflows)
- `--dry-run`: Preview operations without execution (scripts)
- `--verbose`: Detailed output with Context7 integration (scripts)
- `--monitor`: Production monitoring with callbacks (deploy_helper.py)
- `--audit`: Enable audit logging with log_plays (deploy_helper.py)

### Ansible Facts Integration
Use `ansible_facts` for dynamic configuration and target-specific decisions:

```bash
# Gather facts first
ansible-playbook --gather-facts playbook.yml

# Use facts in conditionals
ansible-playbook --extra-vars "target_os={{ ansible_os_family }}" playbook.yml

# Template selection based on facts
ansible-playbook --extra-vars "template={{ ansible_distribution }}" playbook.yml
```

## Usage Patterns

### Unified Workflow
1. **Planning**: Use `--syntax-check` and `--check --diff` for safe previews
2. **Development**: Create playbooks with Context7 best practices, test with `--check --diff`
3. **Tag-Based Development**: Use `--list-tags` to understand structure, `--tags` for focused testing
4. **Production**: Deploy with progressive staging, verify changes with `--check --diff`
5. **Debugging**: Use `--step` or `--vvv` for detailed troubleshooting
6. **Context7 Integration**: Automatic real-time documentation and best practices throughout

### Debugging Workflow (Critical Path)
When issues occur during implementation, follow this disciplined approach:

```bash
# 1. ALWAYS start with check/diff to understand needed changes
ansible-playbook your_playbook.yml --check --diff

# 2. For large playbooks, use step-by-step or tag-based verification:
#    Step mode: ansible-playbook playbook.yml --step --check --diff
#    Tag mode: ansible-playbook playbook.yml --tags "install" --check --diff

# 3. List available tags for strategic testing
ansible-playbook --list-tags playbook.yml

# 4. Section-by-section verification
ansible-playbook --tags "install" --check --diff playbook.yml
ansible-playbook --tags "config" --check --diff playbook.yml

# 5. Analyze diff output - update templates/variables/configs accordingly
# 6. Re-run with --check --diff to verify your fixes
# 7. Only after check passes, run without --check to apply changes
# 8. Final verification with callbacks for documentation
ANSIBLE_STDOUT_CALLBACK=json ansible-playbook --check --diff playbook.yml
```

**Manual on-target tweaking should be the exception, not the rule.** Only use when:
- Complex state dependencies that `--check` can't predict
- Service restarts requiring real-time observation  
- Performance tuning needing live metrics
- Network connectivity issues needing immediate resolution

### Advanced Tagging Strategy
For large playbooks where `--check --diff` produces overwhelming output, use systematic tagging:

```bash
# 1. Discover available tags
ansible-playbook --list-tags playbook.yml

# 2. Section-by-section verification
ansible-playbook --tags "install" --check --diff playbook.yml
ansible-playbook --tags "config" --check --diff playbook.yml

# 3. Progressive deployment with tags
ansible-playbook --tags "install" playbook.yml
ansible-playbook --tags "config" playbook.yml
ansible-playbook --tags "service" playbook.yml
```

See [TAGGING.md](references/TAGGING.md) for complete orthogonal tag taxonomy and refactoring workflows.

### Mode-Specific Safety
See [MODES.md](references/MODES.md) for complete change verification system and mode configuration:

**Safe Operations (Plan Mode):**
- `ansible-playbook --syntax-check` - Syntax validation only
- `ansible-playbook --check --diff` - Dry run with no changes
- `ansible-playbook --list-tags` - Read-only tag discovery
- `ansible-playbook --list-tasks` - Read-only task analysis

**Risky Operations (Build Mode Required):**
- `ansible-playbook` - Actual execution with changes
- `ansible-galaxy install` - Collection installation
- Package installation and system modifications

**Context7 Integration:** Available in both modes for enhanced accuracy and guidance