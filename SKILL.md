---
name: ansible-automation
description: Comprehensive Ansible automation skill with Context7 integration for real-time best practices, playbook generation, role management, inventory configuration, deployment workflows, testing with Docker targets, community module integration, and validation features. Automatically leverages Context7 for current documentation, best practices, and community patterns when available. Use when creating Ansible playbooks, roles, collections, linting, debugging, check mode, or deployment automation. Supports planning mode with dry-run capabilities for safe preview of operations.
---

# Ansible Automation Skill

## Quick Start

**Core Ansible Commands**
```bash
# Syntax validation and check mode
ansible-playbook --syntax-check playbook.yml
ansible-playbook --check --diff playbook.yml

# Targeted execution
ansible-playbook -i inventory.yml --limit webservers --tags database,config playbook.yml

# Debugging
ansible-playbook -vvv --step playbook.yml
```

**Change Verification**
```bash
# Preview changes with diff
ansible-playbook --check --diff playbook.yml

# Tag-based verification
ansible-playbook --check --diff --tags install playbook.yml

# Target-specific verification  
ansible-playbook --check --diff --limit host01 playbook.yml
```

**Helper Scripts (Complex Workflows Only)**
```bash
# Progressive deployment
python3 scripts/deploy_helper.py deploy_config.yml inventory.yml

# Generate playbooks
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

### Core Features
- **Playbook Generation**: Template-based creation with Context7 best practices
- **Role Management**: Standard structure, task organization, variable precedence  
- **Inventory Configuration**: Static/dynamic inventory, SSH configuration
- **Deployment Workflows**: Progressive deployment, monitoring, state tracking
- **Testing Framework**: Tox integration, Docker targets, validation checks
- **Community Integration**: Real-time module discovery and best practices via Context7


## Resources

**Core References:**
- [Parameters Reference](references/parameters.md) - Core Ansible parameters and usage
- [Usage Patterns](references/usage-patterns.md) - Comprehensive workflows and best practices
- [Guardrails Framework](references/guardrails.md) - Context preservation and anti-pattern prevention

**Configuration:**
- [Callback Environment Variables](references/callbacks-env.md) - Callback configuration
- [Script Parameters](references/script-parameters.md) - Helper script parameters
- [Ansible Facts Integration](references/ansible-facts.md) - Dynamic configuration with facts

**Specialized Topics:**
- [INVENTORY.md](references/INVENTORY.md) - Inventory management
- [ROLES.md](references/ROLES.md) - Role patterns
- [DEPLOYMENT.md](references/DEPLOYMENT.md) - Deployment workflows
- [VALIDATION.md](references/VALIDATION.md) - Linting and testing
- [COMMUNITY.md](references/COMMUNITY.md) - Community modules
- [TAGGING.md](references/TAGGING.md) - Advanced tagging strategy
- [CALLBACKS.md](references/CALLBACKS.md) - Callback plugin integration
- [MODES.md](references/MODES.md) - Change verification system
- [TESTING.md](references/TESTING.md) - Docker and Tox testing

**Integration:**
- [AGENTS.md Reference](references/AGENTS-REFERENCE.md) - For projects using this skill in their AGENTS.md

## Scripts (Complex Workflows Only)

- `generate_playbook.py` - Template-based playbook creation
- `deploy_helper.py` - Progressive deployment with state tracking
- `community_manager.py` - Community module discovery and management
- `tox_testing.py` - Testing framework with Docker targets
- `ansible_guardrails.py` - Context preservation and anti-pattern prevention
- `context_preserver.py` - Maintains best practices across sessions

**Note**: Most operations use direct ansible commands. Scripts handle complex multi-step workflows.

## Context Preservation & Guardrails

Sophisticated system to prevent AI context attrition and maintain Ansible best practices. See [Guardrails Framework](references/guardrails.md) for complete details.

**Key Features:**
- Anti-pattern detection (direct SSH, shell commands, manual editing)
- Operation analysis with proper Ansible module suggestions
- Compliance checking against best practices
- Session tracking across multiple AI sessions

**Quick Examples:**
```bash
# Check compliance
python3 scripts/ansible_guardrails.py --check-compliance "ssh to server and edit config"

# Analyze operations
python3 scripts/ansible_guardrails.py -i inventory.yml --analyze-operation "file_operations:edit_file"

# Generate debugging playbooks
python3 scripts/ansible_guardrails.py -i inventory.yml --generate-debug-playbook "service not starting"
```

## Usage Patterns

See [Usage Patterns](references/usage-patterns.md) for comprehensive workflows including unified development/deployment workflows, debugging procedures, advanced tagging strategies, and environment-specific patterns.