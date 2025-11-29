# Script Parameters

## Common Script Parameters

### Safety & Preview
- `--dry-run`: Preview operations without execution (available on most scripts)
- `--check`: Validate configuration and dependencies without making changes
- `--syntax-check`: Validate script syntax and configuration files

### Output & Debugging
- `--verbose`: Detailed output with Context7 integration (scripts)
- `--debug`: Enable debug-level logging and stack traces
- `--quiet`: Suppress non-essential output for automated execution

### Monitoring & Auditing
- `--monitor`: Production monitoring with callbacks (deploy_helper.py)
- `--audit`: Enable audit logging with log_plays (deploy_helper.py)
- `--trace`: Enable detailed execution tracing

### Configuration
- `--config`: Specify alternative configuration file
- `--inventory`: Override inventory file path
- `--output`: Specify output file or directory

## Script-Specific Parameters

### generate_playbook.py
```bash
# Template selection
--template webserver          # Use webserver template
--template database           # Use database template

# Output control
--output deploy.yml           # Output to specific file
--dry-run                     # Preview generated playbook
--context7-enabled           # Enable Context7 best practices

# Customization
--extra-vars "env=prod"      # Add extra variables
--tags install,config         # Add tags to tasks
```

### deploy_helper.py
```bash
# Deployment control
--config deploy_config.yml    # Deployment configuration
--inventory production.ini    # Target inventory
--stage staging               # Deployment stage

# Monitoring & safety
--monitor                     # Enable production monitoring
--audit                       # Enable audit logging
--check                       # Dry run deployment
--rollback                    # Rollback capability

# Performance
--parallel 10                # Parallel deployment limit
--timeout 300                # Operation timeout
```

### community_manager.py
```bash
# Module management
--search nginx                # Search for nginx modules
--install community.mongodb   # Install specific collection
--update                      # Update installed collections

# Context7 integration
--context7-docs              # Get current documentation
--context7-examples           # Get usage examples
--context7-guidance           # Get best practice guidance

# Output control
--dry-run                     # Preview operations
--verbose                     # Detailed output
```

### tox_testing.py
```bash
# Testing control
--environment py38,py39        # Test environments
--tags integration             # Test tags to run
--parallel 4                  # Parallel test execution

# Output & reporting
--junit-xml reports/          # JUnit XML output
--coverage                    # Enable coverage reporting
--verbose                     # Detailed test output

# Docker integration
--docker-targets              # Enable Docker testing
--docker-image ubuntu:20.04   # Custom Docker image
```

### ansible_guardrails.py
```bash
# Compliance checking
--check-compliance "operation" # Check specific operation
--analyze-operation "task"     # Analyze for Ansible alternatives
--generate-debug-playbook "issue" # Generate debugging playbook

# Variable discovery
--discover-var variable_name   # Discover variable truth
--host hostname               # Specific host analysis
--inventory inventory.yml      # Inventory file

# Output control
--verbose                     # Detailed analysis output
--json                        # JSON format output
```

### context_preserver.py
```bash
# Session management
--session-id session_123       # Specific session ID
--list-sessions               # List all sessions
--cleanup-sessions             # Clean old sessions

# Context tracking
--track-operation "task"       # Track specific operation
--get-reminders               # Get best practice reminders
--export-context               # Export session context

# Configuration
--config context_config.yml    # Configuration file
--verbose                     # Detailed output
```

## Usage Examples

### Safe Playbook Generation
```bash
# Generate with Context7 best practices and preview
python3 scripts/generate_playbook.py \
  --template webserver \
  --context7-enabled \
  --dry-run \
  --verbose
```

### Production Deployment
```bash
# Full monitoring deployment with rollback capability
python3 scripts/deploy_helper.py \
  --config production.yml \
  --inventory production.ini \
  --monitor \
  --audit \
  --rollback
```

### Community Module Management
```bash
# Search and install with current documentation
python3 scripts/community_manager.py \
  --search nginx \
  --context7-docs \
  --dry-run

python3 scripts/community_manager.py \
  --install community.nginx \
  --context7-guidance \
  --verbose
```

### Comprehensive Testing
```bash
# Full test suite with reporting
python3 scripts/tox_testing.py \
  --environment py38,py39,py310 \
  --junit-xml reports/ \
  --coverage \
  --docker-targets \
  --parallel 4
```

### Guardrails Compliance
```bash
# Check operation compliance
python3 scripts/ansible_guardrails.py \
  --check-compliance "ssh to server and edit config" \
  --verbose

# Generate debugging playbook
python3 scripts/ansible_guardrails.py \
  -i inventory.yml \
  --generate-debug-playbook "service not starting" \
  --json
```

## Best Practices

### Safety First
1. **Always use --dry-run** before executing operations
2. **Enable --verbose** for complex operations to understand behavior
3. **Use --check** to validate configuration before deployment
4. **Enable --monitor and --audit** for production deployments

### Performance Optimization
1. **Use --parallel** for operations that support it
2. **Set appropriate --timeout** values for network operations
3. **Leverage --context7-enabled** for current best practices
4. **Use --tags** to limit scope when testing

### Output Management
1. **Use --junit-xml** for CI/CD integration
2. **Enable --coverage** for development testing
3. **Use --json** for programmatic processing
4. **Leverage --quiet** for automated script execution

### Context7 Integration
1. **Enable Context7** for current documentation and examples
2. **Use --context7-docs** when exploring new modules
3. **Leverage --context7-guidance** for best practice compliance
4. **Use --context7-examples** for implementation patterns

## Error Handling

### Common Issues
1. **Missing dependencies**: Use --check to validate requirements
2. **Configuration errors**: Use --syntax-check to validate config files
3. **Network timeouts**: Adjust --timeout values appropriately
4. **Permission issues**: Use --verbose to identify specific problems

### Recovery Strategies
1. **Rollback capability**: Enable --rollback for deployment scripts
2. **Session preservation**: Use context_preserver.py for session recovery
3. **Audit trails**: Enable --audit for compliance and debugging
4. **Debug mode**: Use --debug for detailed troubleshooting information