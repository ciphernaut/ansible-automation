# Advanced Tagging Strategy

## Standard Orthogonal Tag Taxonomy

### Primary Tags (Task Groups)
- `database` - Database installation, configuration, management
- `webserver` - Web server setup and configuration  
- `network` - Network configuration and firewall rules
- `security` - Security hardening and access control

### Orthogonal Tags (Function Types)
- `install` - Package installation and initial setup
- `config` - Configuration file management
- `service` - Service management (start/stop/enable)
- `monitoring` - Monitoring and logging setup
- `backup` - Backup and recovery operations

## Tag Application Examples

```yaml
- name: Install PostgreSQL packages
  ansible.builtin.yum:
    name: postgresql-server
    state: present
  tags: ['database', 'install', 'packages']

- name: Configure PostgreSQL settings
  ansible.builtin.template:
    src: postgresql.conf.j2
    dest: /var/lib/pgsql/data/postgresql.conf
  tags: ['database', 'config', 'security']

- name: Start PostgreSQL service
  ansible.builtin.service:
    name: postgresql
    state: started
    enabled: true
  tags: ['database', 'service']
```

## Tag-Based Verification Workflow

```bash
# 1. Analyze available tags
ansible-playbook playbook.yml --list-tags

# 2. Section-by-section verification
ansible-playbook playbook.yml --tags "install" --check --diff
python3 scripts/verify_changes.py --tags "install" --save-state

# 3. Configuration verification  
ansible-playbook playbook.yml --tags "config" --check --diff
python3 scripts/verify_changes.py --tags "config" --compare-state

# 4. Full verification
ansible-playbook playbook.yml --check --diff
python3 scripts/verify_changes.py --full-verification
```

## Orthogonal Tag Development and Refactoring

### Tag Analysis Workflow

```bash
# 1. Discover all existing tags in playbook
ansible-playbook playbook.yml --list-tags

# 2. Extract tag usage patterns (custom script)
python3 scripts/verify_changes.py --analyze-tags playbook.yml

# 3. Identify missing orthogonal tags
python3 scripts/verify_changes.py --check-tag-coverage playbook.yml

# 4. Validate tag dependencies and consistency
python3 scripts/verify_changes.py --validate-tag-deps playbook.yml
```

### Refactoring Strategy

```bash
# Before refactoring - analyze current state
ansible-playbook old_playbook.yml --list-tags > current_tags.txt

# After refactoring - verify tag completeness
ansible-playbook new_playbook.yml --list-tags > new_tags.txt

# Compare tag coverage
diff current_tags.txt new_tags.txt

# Validate orthogonal tag application
python3 scripts/verify_changes.py --check-tag-coverage new_playbook.yml
```

### Tag Development Best Practices

1. **Discovery First**: Always start with `--list-tags` to understand current tag landscape
2. **Systematic Application**: Apply orthogonal tags consistently across task groups
3. **Validation**: Use tag analysis tools to ensure coverage and consistency
4. **Incremental Refactoring**: Update tags in sections, validate with `--list-tags` after each change
5. **Documentation**: Maintain tag taxonomy in project documentation for team alignment

## Tag Validation Commands

```bash
# Validate tag coverage and consistency
python3 scripts/verify_changes.py --analyze-tags playbook.yml

# Check for missing orthogonal tags
python3 scripts/verify_changes.py --check-tag-coverage playbook.yml

# Verify tag dependencies
python3 scripts/verify_changes.py --validate-tag-deps playbook.yml
```

## Best Practices

1. **Consistent Application**: Apply orthogonal tags systematically across all tasks
2. **Logical Grouping**: Use primary tags for functional areas
3. **Function Separation**: Use orthogonal tags for operation types
4. **Verification Integration**: Leverage tags for targeted verification
5. **Documentation**: Maintain tag taxonomy in project documentation