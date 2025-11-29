# Callback Environment Variables

## Standard Output Callbacks

### Minimal Callback
```bash
# Ultra-compact output for automated scripts
ANSIBLE_STDOUT_CALLBACK=minimal ansible-playbook playbook.yml
```

### YAML Callback
```bash
# YAML results for template matching and parsing
ANSIBLE_STDOUT_CALLBACK=yaml ansible-playbook playbook.yml
ANSIBLE_CALLBACK_RESULT_FORMAT=yaml ansible-playbook playbook.yml
ANSIBLE_CALLBACK_FORMAT_PRETTY=true ansible-playbook playbook.yml
```

### JSON Callback
```bash
# Structured JSON output for programmatic processing
ANSIBLE_STDOUT_CALLBACK=json ansible-playbook playbook.yml
```

## Enhanced Monitoring Callbacks

### JUnit Integration
```bash
# Generate JUnit XML reports for CI/CD integration
ANSIBLE_CALLBACKS_ENABLED=junit ansible-playbook playbook.yml
```

### OpenTelemetry Integration
```bash
# Enable distributed tracing for observability
ANSIBLE_CALLBACKS_ENABLED=opentelemetry ansible-playbook playbook.yml
```

### Multiple Callbacks
```bash
# Combine multiple callbacks for comprehensive monitoring
ANSIBLE_CALLBACKS_ENABLED=junit,opentelemetry,profile_tasks ansible-playbook playbook.yml
```

## Environment Variable Reference

### Output Formatting
- `ANSIBLE_STDOUT_CALLBACK=minimal`: Ultra-compact output
- `ANSIBLE_CALLBACK_RESULT_FORMAT=yaml`: YAML results for template matching
- `ANSIBLE_CALLBACK_FORMAT_PRETTY=true`: Readable YAML formatting
- `ANSIBLE_STDOUT_CALLBACK=json`: Structured JSON output

### Enhanced Monitoring
- `ANSIBLE_CALLBACKS_ENABLED=junit,opentelemetry`: Enhanced monitoring

## Usage Examples

### CI/CD Pipeline Integration
```bash
# Generate comprehensive reports for CI/CD
ANSIBLE_CALLBACKS_ENABLED=junit,opentelemetry,timer \
ANSIBLE_JUNIT_DIR=./reports/ \
ANSIBLE_OPENTELEMETRY_SERVICE_NAME=ci-pipeline \
ansible-playbook --check --diff deploy.yml
```

### Debugging Complex Playbooks
```bash
# Enhanced debugging with multiple callbacks
ANSIBLE_CALLBACKS_ENABLED=debug,timer,profile_tasks \
ansible-playbook -vvv --step --check --diff complex-playbook.yml
```

### Production Deployment Monitoring
```bash
# Full observability for production deployments
ANSIBLE_CALLBACKS_ENABLED=opentelemetry,junit,timer \
ANSIBLE_OPENTELEMETRY_SERVICE_NAME=production-deploy \
ANSIBLE_JUNIT_DIR=./deployment-reports/ \
ansible-playbook deploy.yml
```

## Best Practices

1. **Use minimal callback for automated scripts** - Reduces noise and improves parsing
2. **Enable timer callback for performance analysis** - Identifies slow tasks
3. **Use JUnit for CI/CD integration** - Standardized test reporting
4. **Enable OpenTelemetry for distributed systems** - Correlates with application traces
5. **Combine callbacks strategically** - Multiple callbacks provide comprehensive insights

## Integration with Scripts

### verify_changes.py
```bash
# Enhanced analysis with callbacks
ANSIBLE_STDOUT_CALLBACK=json python3 scripts/verify_changes.py --structured-output
ANSIBLE_CALLBACKS_ENABLED=junit,opentelemetry python3 scripts/verify_changes.py --with-monitoring
```

### deploy_helper.py
```bash
# Production deployment with monitoring
ANSIBLE_CALLBACKS_ENABLED=opentelemetry,timer python3 scripts/deploy_helper.py --monitor
ANSIBLE_CALLBACKS_ENABLED=junit python3 scripts/deploy_helper.py --audit
```