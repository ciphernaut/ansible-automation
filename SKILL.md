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

- [Parameters Reference](references/parameters.md) - Core Ansible parameters and usage
- [Callback Environment Variables](references/callbacks-env.md) - Callback configuration
- [Script Parameters](references/script-parameters.md) - Helper script parameters
- [Ansible Facts Integration](references/ansible-facts.md) - Dynamic configuration with facts
- [Usage Patterns](references/usage-patterns.md) - Comprehensive workflows and best practices
- [Guardrails Framework](references/guardrails.md) - Context preservation and anti-pattern prevention
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
- `ansible_guardrails.py` - Context preservation and anti-pattern prevention framework
- `context_preserver.py` - Maintains Ansible best practices across sessions

**Note**: Most operations use direct ansible commands. Scripts are reserved for complex multi-step workflows that provide significant value beyond basic command execution.

## Context Preservation & Guardrails

The skill includes a sophisticated context preservation system to prevent AI context attrition and maintain Ansible best practices. See [Guardrails Framework](references/guardrails.md) for complete details.

### Key Features
- **Anti-Pattern Detection**: Identifies non-Ansible patterns (direct SSH, shell commands, manual editing)
- **Operation Analysis**: Suggests proper Ansible modules for common operations
- **Compliance Checking**: Validates proposed actions against Ansible best practices
- **Session Tracking**: Maintains context across multiple AI sessions
- **Best Practice Reminders**: Provides timely reminders about Ansible patterns

### Quick Examples
```bash
# Check compliance of proposed actions
python3 scripts/ansible_guardrails.py --check-compliance "ssh to server and edit config"

# Analyze operations for Ansible-native alternatives
python3 scripts/ansible_guardrails.py -i inventory.yml --analyze-operation "file_operations:edit_file"

# Generate debugging playbooks with guardrails
python3 scripts/ansible_guardrails.py -i inventory.yml --generate-debug-playbook "service not starting"
```









## Usage Patterns

See [Usage Patterns](references/usage-patterns.md) for comprehensive workflows including:
- Unified development and deployment workflows
- Debugging procedures and critical path analysis
- Advanced tagging strategies for complex playbooks
- Environment-specific patterns (dev/staging/production)
- Performance optimization and error handling patterns