# Core Ansible Parameters

## Essential Command Line Parameters

### Safety & Verification
- `--syntax-check`: Validate playbook syntax without execution
- `--check`: Dry run mode - show what would change without making changes
- `--diff`: Show actual differences when used with --check
- `--step`: Interactive step-by-step execution

### Discovery & Analysis
- `--list-tags`: Display all available tags in playbook
- `--list-tasks`: Display all tasks in playbook
- `--list-hosts`: Display all matching hosts

### Targeting & Filtering
- `--limit`: Restrict execution to specific hosts/groups
- `--tags`: Run only tasks with specified tags
- `--skip-tags`: Skip tasks with specified tags
- `--start-at-task`: Start playbook at specific task

### Variables & Configuration
- `--extra-vars`: Pass additional variables (format: "key=value" or JSON)
- `--vault-id`: Specify vault identity for decryption
- `--ask-vault-pass`: Prompt for vault password
- `--inventory`: Specify inventory file path

### Output & Debugging
- `-v, -vv, -vvv`: Verbose output levels for debugging
- `--check-mode`: Alias for --check
- `--forks`: Set number of parallel processes (default: 5)
- `--timeout`: Set connection timeout (seconds)

### Connection Options
- `--connection`: Connection type (ssh, local, etc.)
- `--user`: Remote user for connections
- `--private-key`: SSH private key file
- `--ssh-common-args`: Additional SSH arguments

## Usage Examples

### Basic Safety Checks
```bash
# Syntax validation only
ansible-playbook --syntax-check playbook.yml

# Dry run with diff output
ansible-playbook --check --diff playbook.yml

# Step-by-step execution
ansible-playbook --step playbook.yml
```

### Targeted Execution
```bash
# Limit to specific hosts
ansible-playbook --limit webservers playbook.yml

# Run specific tags only
ansible-playbook --tags install,config playbook.yml

# Skip maintenance tasks
ansible-playbook --skip-tags maintenance playbook.yml
```

### Variable Management
```bash
# Single variable
ansible-playbook --extra-vars "env=production" playbook.yml

# Multiple variables
ansible-playbook --extra-vars "env=prod version=1.2.3" playbook.yml

# JSON variables
ansible-playbook --extra-vars '{"env": "prod", "config": {"debug": true}}' playbook.yml

# Variables from file
ansible-playbook --extra-vars "@vars.json" playbook.yml
```

### Debugging & Analysis
```bash
# Verbose output
ansible-playbook -v playbook.yml
ansible-playbook -vvv playbook.yml

# List structure
ansible-playbook --list-tasks --list-tags playbook.yml

# Start at specific task
ansible-playbook --start-at-task "Configure nginx" playbook.yml
```

## Best Practices

### Safety First
1. **Always use --check --diff** before applying changes
2. **Use --syntax-check** after modifying playbooks
3. **Leverage --limit** for targeted testing
4. **Use --step** for complex debugging scenarios

### Performance Optimization
1. **Adjust --forks** for large deployments (default: 5)
2. **Use --tags** to avoid unnecessary task execution
3. **Set appropriate --timeout** for slow networks
4. **Use --skip-tags** to exclude expensive operations

### Variable Management
1. **Prefer --extra-vars** over environment variables for clarity
2. **Use JSON format** for complex variable structures
3. **Store sensitive variables** in Ansible Vault with --vault-id
4. **Validate variables** with type checking when possible

### Connection Management
1. **Specify --connection explicitly** for non-SSH connections
2. **Use --private-key** for key-based authentication
3. **Configure --ssh-common-args** for complex network setups
4. **Set appropriate --user** for privilege separation

## Advanced Combinations

### Production Deployment Workflow
```bash
# 1. Syntax check
ansible-playbook --syntax-check deploy.yml

# 2. Dry run on single host
ansible-playbook --check --diff --limit web01 deploy.yml

# 3. Staged deployment with tags
ansible-playbook --tags prepare --limit staging deploy.yml
ansible-playbook --tags deploy --limit staging deploy.yml

# 4. Production deployment
ansible-playbook --tags prepare,deploy deploy.yml
```

### Debugging Complex Issues
```bash
# High verbosity with step mode
ansible-playbook -vvv --step --check --diff problem-playbook.yml

# Start at failing task
ansible-playbook -vv --start-at-task "failing-task" playbook.yml

# Limited scope with diff
ansible-playbook --limit problematic-host --check --diff -v playbook.yml
```

### Multi-Environment Management
```bash
# Development with debug variables
ansible-playbook --extra-vars "@dev-vars.json" --tags debug deploy.yml

# Staging with production-like settings
ansible-playbook --extra-vars "@staging-vars.json" --check --diff deploy.yml

# Production with full monitoring
ansible-playbook --extra-vars "@prod-vars.json" --tags deploy,monitor deploy.yml
```