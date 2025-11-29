# Usage Patterns

## Unified Workflow

### 1. Planning Phase
Use `--syntax-check` and `--check --diff` for safe previews:
```bash
# Validate playbook syntax
ansible-playbook --syntax-check playbook.yml

# Preview changes without execution
ansible-playbook --check --diff playbook.yml

# Target specific hosts for planning
ansible-playbook --check --diff --limit staging playbook.yml
```

### 2. Development Phase
Create playbooks with Context7 best practices, test with `--check --diff`:
```bash
# Test with verbose output
ansible-playbook --check --diff -v playbook.yml

# Test specific sections
ansible-playbook --check --diff --tags install playbook.yml
```

### 3. Tag-Based Development
Use `--list-tags` to understand structure, `--tags` for focused testing:
```bash
# Discover available tags
ansible-playbook --list-tags playbook.yml

# Test specific functionality
ansible-playbook --check --diff --tags database,config playbook.yml
```

### 4. Production Deployment
Deploy with progressive staging, verify changes with `--check --diff`:
```bash
# Staged deployment
ansible-playbook --tags prepare --limit staging playbook.yml
ansible-playbook --check --diff --tags deploy --limit staging playbook.yml
ansible-playbook --tags deploy --limit production playbook.yml
```

### 5. Debugging Phase
Use `--step` or `--vvv` for detailed troubleshooting:
```bash
# Step-by-step execution
ansible-playbook --step --check --diff playbook.yml

# Verbose debugging
ansible-playbook -vvv --check --diff playbook.yml
```

### 6. Context7 Integration
Automatic real-time documentation and best practices throughout all phases.

## Debugging Workflow (Critical Path)

When issues occur during implementation, follow this disciplined approach:

### Step 1: Initial Analysis
```bash
# ALWAYS start with check/diff to understand needed changes
ansible-playbook your_playbook.yml --check --diff
```

### Step 2: Focused Investigation
For large playbooks, use step-by-step or tag-based verification:
```bash
# Step mode for interactive debugging
ansible-playbook playbook.yml --step --check --diff

# Tag mode for section-specific testing
ansible-playbook playbook.yml --tags "install" --check --diff
```

### Step 3: Strategic Planning
```bash
# List available tags for strategic testing
ansible-playbook --list-tags playbook.yml
```

### Step 4: Section-by-Section Verification
```bash
# Test individual sections
ansible-playbook --tags "install" --check --diff playbook.yml
ansible-playbook --tags "config" --check --diff playbook.yml
ansible-playbook --tags "service" --check --diff playbook.yml
```

### Step 5: Analysis and Correction
- Analyze diff output - update templates/variables/configs accordingly
- Re-run with `--check --diff` to verify your fixes
- Only after check passes, run without `--check` to apply changes

### Step 6: Final Verification
```bash
# Final verification with callbacks for documentation
ANSIBLE_STDOUT_CALLBACK=json ansible-playbook --check --diff playbook.yml
```

## Manual Intervention Guidelines

**Manual on-target tweaking should be the exception, not the rule.** Only use when:

### Valid Use Cases
- **Complex state dependencies** that `--check` can't predict
- **Service restarts** requiring real-time observation  
- **Performance tuning** needing live metrics
- **Network connectivity issues** needing immediate resolution

### Anti-Patterns to Avoid
- **Manual file editing** instead of fixing playbook logic
- **Direct command execution** bypassing Ansible's idempotency
- **Ad-hoc configuration changes** without playbook updates
- **Workaround application** instead of root cause analysis

## Advanced Tagging Strategy

For large playbooks where `--check --diff` produces overwhelming output, use systematic tagging:

### Phase 1: Discovery
```bash
# Discover available tags
ansible-playbook --list-tags playbook.yml
```

### Phase 2: Section Verification
```bash
# Section-by-section verification
ansible-playbook --tags "install" --check --diff playbook.yml
ansible-playbook --tags "config" --check --diff playbook.yml
ansible-playbook --tags "service" --check --diff playbook.yml
```

### Phase 3: Progressive Deployment
```bash
# Progressive deployment with tags
ansible-playbook --tags "install" playbook.yml
ansible-playbook --tags "config" playbook.yml
ansible-playbook --tags "service" playbook.yml
```

### Tag Organization Best Practices
- **Orthogonal tags**: Separate concerns (install, config, service)
- **Environment tags**: dev, staging, production
- **Component tags**: web, database, cache
- **Action tags**: deploy, update, rollback

See [TAGGING.md](references/TAGGING.md) for complete orthogonal tag taxonomy and refactoring workflows.

## Mode-Specific Safety

See [MODES.md](references/MODES.md) for complete change verification system and mode configuration:

### Safe Operations (Plan Mode)
- `ansible-playbook --syntax-check` - Syntax validation only
- `ansible-playbook --check --diff` - Dry run with no changes
- `ansible-playbook --list-tags` - Read-only tag discovery
- `ansible-playbook --list-tasks` - Read-only task analysis

### Risky Operations (Build Mode Required)
- `ansible-playbook` - Actual execution with changes
- `ansible-galaxy install` - Collection installation
- Package installation and system modifications

### Context7 Integration
Available in both modes for enhanced accuracy and guidance.

## Environment-Specific Patterns

### Development Environment
```bash
# Rapid iteration with verbose output
ansible-playbook --check --diff -v dev-playbook.yml

# Test specific features
ansible-playbook --tags feature-x --check --diff dev-playbook.yml

# Step-by-step debugging
ansible-playbook --step --check --diff dev-playbook.yml
```

### Staging Environment
```bash
# Full verification before production
ansible-playbook --check --diff staging-playbook.yml

# Performance testing with timing
ANSIBLE_CALLBACKS_ENABLED=timer ansible-playbook --check --diff staging-playbook.yml

# Comprehensive testing
ansible-playbook --tags all --check --diff staging-playbook.yml
```

### Production Environment
```bash
# Staged deployment with monitoring
ansible-playbook --tags prepare --limit batch1 production-playbook.yml
ansible-playbook --tags deploy --limit batch1 production-playbook.yml

# Full monitoring and audit
ANSIBLE_CALLBACKS_ENABLED=junit,opentelemetry ansible-playbook production-playbook.yml

# Rollback capability
ansible-playbook --tags rollback production-playbook.yml
```

## Performance Optimization Patterns

### Large-Scale Deployments
```bash
# Parallel execution with fork control
ansible-playbook --forks 20 large-deployment.yml

# Targeted deployment to reduce scope
ansible-playbook --limit "webservers:!maintenance" deployment.yml

# Batch processing for rolling updates
ansible-playbook --limit "batch1" deployment.yml
ansible-playbook --limit "batch2" deployment.yml
```

### Network Optimization
```bash
# Connection pipelining for faster execution
ansible-playbook --ssh-extra-args="-o ControlMaster=auto" deployment.yml

# Timeout adjustment for slow networks
ansible-playbook --timeout 300 deployment.yml

# Fact gathering optimization
ansible-playbook --gather-facts --extra-vars "gather_subset=minimal" deployment.yml
```

## Error Handling Patterns

### Pre-Flight Validation
```bash
# Comprehensive validation
ansible-playbook --syntax-check playbook.yml
ansible-playbook --list-tasks playbook.yml
ansible-playbook --check --diff playbook.yml
```

### Incremental Recovery
```bash
# Identify failure point
ansible-playbook --list-tasks playbook.yml
ansible-playbook --start-at-task "failing-task" --check --diff playbook.yml

# Resume from failure point
ansible-playbook --start-at-task "after-failure" playbook.yml
```

### Rollback Procedures
```bash
# Tag-based rollback
ansible-playbook --tags rollback playbook.yml

# State reconciliation
python3 scripts/state_reconciliation.py --rollback --inventory production.ini
```

## Integration Patterns

### CI/CD Pipeline Integration
```bash
# Automated testing
ansible-playbook --check --diff --syntax-check ci-playbook.yml

# JUnit reporting for test results
ANSIBLE_CALLBACKS_ENABLED=junit ansible-playbook test-playbook.yml

# Structured output for processing
ANSIBLE_STDOUT_CALLBACK=json ansible-playbook deploy-playbook.yml
```

### Monitoring Integration
```bash
# OpenTelemetry for observability
ANSIBLE_CALLBACKS_ENABLED=opentelemetry ansible-playbook deploy-playbook.yml

# Performance profiling
ANSIBLE_CALLBACKS_ENABLED=timer,profile_tasks ansible-playbook deploy-playbook.yml
```

### Configuration Management
```bash
# Environment-specific configuration
ansible-playbook --extra-vars "@prod-vars.json" deploy-playbook.yml

# Secret management with vault
ansible-playbook --vault-id prod@prompt deploy-playbook.yml
```

## Best Practices Summary

1. **Always start with --check --diff** before making changes
2. **Use tags strategically** to manage complexity
3. **Leverage Context7 integration** for current best practices
4. **Implement progressive deployment** for production safety
5. **Use appropriate callbacks** for monitoring and debugging
6. **Maintain audit trails** for compliance and troubleshooting
7. **Test incrementally** to identify issues early
8. **Document manual interventions** and incorporate into playbooks