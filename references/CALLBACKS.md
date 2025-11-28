# Callback Plugin Integration

## Available Callback Plugins

### Minimal Callback
```bash
# Basic minimal output
ANSIBLE_STDOUT_CALLBACK=minimal ansible-playbook playbook.yml

# Minimal with YAML results for template matching
ANSIBLE_CALLBACK_RESULT_FORMAT=yaml ANSIBLE_STDOUT_CALLBACK=minimal ansible-playbook playbook.yml

# Minimal with pretty YAML for better readability
ANSIBLE_CALLBACK_RESULT_FORMAT=yaml ANSIBLE_CALLBACK_FORMAT_PRETTY=true ANSIBLE_STDOUT_CALLBACK=minimal ansible-playbook playbook.yml
```
- Ultra-compact output for high-volume automation
- Default for ansible ad-hoc commands
- Reduces log noise in CI/CD pipelines
- Perfect for scripted execution where only exit codes matter
- YAML result format matches Ansible templating and variable structures
- Pretty formatting enhances readability while maintaining minimal output

### JSON Callback
```bash
ANSIBLE_STDOUT_CALLBACK=json ansible-playbook playbook.yml
```
- Structured JSON output for automation
- CI/CD pipeline integration
- Programmatic result processing

### JUnit Callback
```bash
ANSIBLE_CALLBACKS_ENABLED=junit ansible-playbook playbook.yml
```
- JUnit XML format for test results
- Test reporting and visualization
- Quality gate integration

### OpenTelemetry Callback
```bash
ANSIBLE_CALLBACKS_ENABLED=community.general.opentelemetry ansible-playbook playbook.yml
```
- Distributed tracing for deployments
- Performance monitoring and observability
- Integration with modern monitoring stacks

### Timer Callback
```bash
ANSIBLE_CALLBACKS_ENABLED=ansible.posix.timer ansible-playbook playbook.yml
```
- Task timing analysis
- Performance bottleneck identification
- Deployment optimization insights

### Log Plays Callback
```bash
ANSIBLE_CALLBACKS_ENABLED=community.general.log_plays ansible-playbook playbook.yml
```
- Detailed execution logging
- Audit trail generation
- Compliance and security monitoring

## Integration Examples

### Production Monitoring
```bash
# Combine multiple callbacks for comprehensive monitoring
ANSIBLE_CALLBACKS_ENABLED=community.general.opentelemetry,ansible.posix.timer,community.general.log_plays ansible-playbook deploy.yml
```

### CI/CD Testing
```bash
# Minimal output for automated pipelines (exit codes only)
ANSIBLE_STDOUT_CALLBACK=minimal ansible-playbook test.yml

# Minimal with YAML results for template validation
ANSIBLE_CALLBACK_RESULT_FORMAT=yaml ANSIBLE_STDOUT_CALLBACK=minimal ansible-playbook test.yml

# Structured output for automated testing
ANSIBLE_STDOUT_CALLBACK=json ANSIBLE_CALLBACKS_ENABLED=junit ansible-playbook test.yml
```

### Debugging and Analysis
```bash
# Enhanced debugging with timing and logging
ANSIBLE_CALLBACKS_ENABLED=ansible.posix.timer,community.general.log_plays ansible-playbook -vvv debug.yml
```

## Script Integration

### verify_changes.py
```bash
# Enhanced analysis with callbacks
ANSIBLE_STDOUT_CALLBACK=json python3 scripts/verify_changes.py --structured-output
ANSIBLE_CALLBACKS_ENABLED=junit,opentelemetry python3 scripts/verify_changes.py --with-monitoring
```

### deploy_helper.py
```bash
# Production deployment with monitoring
ANSIBLE_CALLBACKS_ENABLED=community.general.opentelemetry,ansible.posix.timer python3 scripts/deploy_helper.py --monitor
ANSIBLE_CALLBACKS_ENABLED=community.general.log_plays python3 scripts/deploy_helper.py --audit
```

## Configuration

### ansible.cfg Setup
```ini
[defaults]
stdout_callback = json
callback_whitelist = timer,junit,profile_roles
callback_result_format = yaml
callback_format_pretty = true

[callback_junit]
test_case_prefix = ansible
output_folder = /tmp/junit-results

[callback_opentelemetry]
endpoint = http://localhost:4317
service_name = ansible-automation
```

### Minimal Callback Configuration
```ini
[defaults]
# For template matching and readability
callback_result_format = yaml
callback_format_pretty = true

# Environment-specific overrides
# Production: minimal output
# stdout_callback = minimal

# Development: minimal with YAML
# stdout_callback = minimal
# callback_result_format = yaml
```

## Best Practices

1. **Environment-Specific**: Use different callbacks for dev vs prod
2. **Performance Impact**: Consider overhead in production environments
3. **Output Management**: Configure log rotation and cleanup
4. **Security**: Avoid logging sensitive information
5. **Integration**: Ensure compatibility with existing monitoring tools
6. **Minimal for Automation**: Use `minimal` callback for high-volume scripted execution where only success/failure matters
7. **Progressive Verbosity**: Start with `minimal`, add specific callbacks as needed for debugging
8. **Template Matching**: Use `callback_result_format=yaml` with minimal callback to match Ansible templating structure
9. **Readability**: Enable `callback_format_pretty=true` for better YAML output while maintaining minimal verbosity