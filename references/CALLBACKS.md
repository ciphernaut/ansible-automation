# Callback Plugin Integration

## Available Callback Plugins

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

[callback_junit]
test_case_prefix = ansible
output_folder = /tmp/junit-results

[callback_opentelemetry]
endpoint = http://localhost:4317
service_name = ansible-automation
```

## Best Practices

1. **Environment-Specific**: Use different callbacks for dev vs prod
2. **Performance Impact**: Consider overhead in production environments
3. **Output Management**: Configure log rotation and cleanup
4. **Security**: Avoid logging sensitive information
5. **Integration**: Ensure compatibility with existing monitoring tools