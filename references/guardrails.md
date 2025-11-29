# Context Preservation & Guardrails

## Overview

The ansible-automation skill includes a sophisticated context preservation system to prevent AI context attrition and maintain Ansible best practices across multiple sessions and interactions.

## Guardrails Framework (`ansible_guardrails.py`)

### Anti-Pattern Detection
The guardrails framework identifies non-Ansible patterns that violate Infrastructure as Code principles:

- **Direct SSH Commands**: Detects attempts to use SSH directly instead of Ansible modules
- **Shell Command Execution**: Identifies raw shell commands that should be replaced with proper modules
- **Manual File Editing**: Flags manual file editing that bypasses Ansible's idempotency
- **Ad-hoc System Changes**: Detects system changes made outside of Ansible control

### Operation Analysis
Analyzes proposed operations and suggests proper Ansible modules:

```bash
# Analyze operations for Ansible-native alternatives
python3 scripts/ansible_guardrails.py -i inventory.yml --analyze-operation "file_operations:edit_file"

# Example output:
# WARNING: Direct file editing detected
# SUGGESTION: Use ansible.builtin.copy or ansible.builtin.template module
# EXAMPLE: ansible.builtin.copy:
#            src: config.j2
#            dest: /etc/app/config.conf
```

### Compliance Checking
Validates proposed actions against Ansible best practices:

```bash
# Check compliance of proposed actions
python3 scripts/ansible_guardrails.py --check-compliance "ssh to server and edit config"

# Example output:
# ❌ NON-COMPLIANT: Direct SSH access detected
# ✅ COMPLIANT ALTERNATIVE: Use ansible.builtin.raw for emergency access only
# ✅ COMPLIANT ALTERNATIVE: Use ansible.builtin.user for user management
```

### Variable Discovery
Uses ansible-inventory tools to understand variable hierarchy and truth values:

```bash
# Discover variable truth across inventory
python3 scripts/ansible_guardrails.py -i inventory.yml --discover-var app_version --host web01

# Example output:
# Variable: app_version
# Host: web01
# Final Value: "1.2.3"
# Precedence Chain:
#   - group_vars/all.yml: "1.0.0"
#   - group_vars/webservers.yml: "1.2.0" 
#   - host_vars/web01.yml: "1.2.3"
```

## Context Preservation (`context_preserver.py`)

### Session Tracking
Maintains context across multiple AI sessions:

```bash
# Start new session
python3 scripts/context_preserver.py --session-id session_123 --track-operation "playbook_deployment"

# List active sessions
python3 scripts/context_preserver.py --list-sessions

# Example output:
# Active Sessions:
#   session_123: Started 2024-01-15 10:30:00, Last: 2024-01-15 11:45:00
#   session_124: Started 2024-01-15 11:00:00, Last: 2024-01-15 11:30:00
```

### Best Practice Reminders
Provides timely reminders about Ansible patterns based on recent operations:

```bash
# Get best practice reminders
python3 scripts/context_preserver.py --get-reminders

# Example output:
# Recent Operations Analysis:
#   - 3 playbook executions detected
#   - 0 check-mode violations ✅
#   - 2 opportunities for idempotency improvements
#   
# Recommendations:
#   - Consider using --check --diff before production deployments
#   - Review variable precedence for complex configurations
```

### Operation History
Tracks recent operations for pattern recognition and compliance monitoring:

```bash
# Export session context
python3 scripts/context_preserver.py --export-context --session-id session_123

# Example output:
# Session Context:
#   Operations: 12
#   Playbooks: deploy.yml, config.yml, rollback.yml
#   Tags Used: install, configure, service
#   Compliance Score: 95%
#   Last Guardrails Check: Passed
```

## Usage Examples

### Compliance Checking
```bash
# Check if proposed action follows Ansible best practices
python3 scripts/ansible_guardrails.py --check-compliance "ssh to server and edit nginx config"

# Output:
# ❌ VIOLATION: Direct SSH and manual file editing
# ✅ ALTERNATIVE: Use ansible.builtin.template with notify handler
# Example:
#   - name: Configure nginx
#     ansible.builtin.template:
#       src: nginx.conf.j2
#       dest: /etc/nginx/nginx.conf
#     notify: restart nginx
```

### Operation Analysis
```bash
# Get Ansible-native alternatives for common operations
python3 scripts/ansible_guardrails.py -i inventory.yml --analyze-operation "service_management"

# Output:
# Operation: service_management
# Ansible Alternatives:
#   - ansible.builtin.service: Start/stop/restart services
#   - ansible.builtin.systemd: Modern systemd service control
#   - ansible.builtin.sysvinit: Traditional SysV init systems
```

### Debugging Playbook Generation
```bash
# Generate debugging playbooks with guardrails compliance
python3 scripts/ansible_guardrails.py -i inventory.yml --generate-debug-playbook "service not starting"

# Output:
# Generated: debug-service.yml
# Features:
#   - Service status checking
#   - Log file analysis
#   - Configuration validation
#   - Dependency checking
#   - All tasks follow best practices ✅
```

### Variable Discovery
```bash
# Understand variable precedence and final values
python3 scripts/ansible_guardrails.py -i inventory.yml --discover-var database_host --host app01

# Output:
# Variable Analysis: database_host
# Target Host: app01
# Final Value: "db01.production.local"
# Precedence Chain:
#   1. group_vars/all.yml: "localhost"
#   2. group_vars/production.yml: "db.production.local"
#   3. host_vars/app01.yml: "db01.production.local" ✅
```

## Integration Points

All major scripts automatically integrate guardrails:

### Inventory Manager Integration
```bash
# Validates inventory creation patterns
python3 scripts/inventory_manager.py create --template production --guardrails-check

# Automatic validation:
# - SSH configuration best practices
# - Group organization standards
# - Variable naming conventions
# - Security configuration compliance
```

### Playbook Generator Integration
```bash
# Checks task compliance and suggests proper modules
python3 scripts/generate_playbook.py --template webserver --guardrails-enabled

# Automatic enhancements:
# - Module selection guidance
# - Idempotency improvements
# - Error handling patterns
# - Security best practices
```

### Deploy Helper Integration
```bash
# Provides deployment recommendations and validates approaches
python3 scripts/deploy_helper.py deploy.yml inventory.yml --guardrails-validation

# Deployment safety checks:
# - Rollback capability verification
# - Progressive deployment validation
# - Monitoring integration checks
# - Compliance validation
```

### Context Preserver Integration
```bash
# Maintains best practice awareness across sessions
python3 scripts/context_preserver.py --track-operation "deployment" --auto-reminders

# Session continuity:
# - Operation pattern tracking
# - Best practice reinforcement
# - Compliance monitoring
# - Context preservation
```

## Best Practices

### Guardrails Integration
1. **Always check compliance** before implementing new approaches
2. **Use operation analysis** to find proper Ansible modules
3. **Leverage variable discovery** for complex configurations
4. **Generate debugging playbooks** with built-in compliance

### Context Preservation
1. **Enable session tracking** for long-running projects
2. **Use operation history** for pattern analysis
3. **Configure reminders** for team consistency
4. **Export context** for documentation and handoffs

### Compliance Monitoring
1. **Regular compliance checks** for ongoing operations
2. **Pattern analysis** to identify improvement opportunities
3. **Score tracking** for quality metrics
4. **Integration with CI/CD** for automated validation

## Configuration

### Guardrails Configuration
```yaml
# guardrails_config.yml
compliance_rules:
  strict_ssh: true
  require_idempotency: true
  enforce_check_mode: true
  
analysis_patterns:
  suggest_modules: true
  provide_examples: true
  security_focused: true
  
variable_discovery:
  show_precedence: true
  include_defaults: true
  validate_types: true
```

### Context Preservation Configuration
```yaml
# context_config.yml
session_management:
  max_sessions: 10
  session_timeout: 86400
  auto_cleanup: true
  
reminders:
  check_mode_frequency: 5
  compliance_frequency: 10
  best_practice_frequency: 3
  
tracking:
  operation_history: 100
  pattern_analysis: true
  export_format: json
```

## Troubleshooting

### Common Issues
1. **Guardrails not triggering**: Check script integration and configuration
2. **Context not preserved**: Verify session management settings
3. **False positives**: Adjust compliance rules and patterns
4. **Performance issues**: Optimize tracking and analysis settings

### Debug Commands
```bash
# Test guardrails functionality
python3 scripts/ansible_guardrails.py --test-compliance

# Verify context preservation
python3 scripts/context_preserver.py --status

# Check integration status
python3 scripts/deploy_helper.py --guardrails-status
```

### Recovery Procedures
```bash
# Reset context preservation
python3 scripts/context_preserver.py --reset-sessions

# Rebuild guardrails cache
python3 scripts/ansible_guardrails.py --rebuild-cache

# Export diagnostic information
python3 scripts/context_preserver.py --export-diagnostic
```