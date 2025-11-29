# Ansible Facts Integration

## Overview

Ansible facts are automatically gathered information about target systems that can be used for dynamic configuration and target-specific decisions. Facts provide detailed system information including OS details, hardware specifications, network configuration, and more.

## Gathering Facts

### Basic Fact Gathering
```bash
# Gather facts first (default behavior)
ansible-playbook --gather-facts playbook.yml

# Explicitly enable fact gathering
ansible-playbook --gather-facts=yes playbook.yml

# Disable fact gathering for performance
ansible-playbook --gather-facts=no playbook.yml
```

### Targeted Fact Gathering
```bash
# Gather only specific facts
ansible-playbook --gather-facts --extra-vars "gather_subset=minimal" playbook.yml
ansible-playbook --gather-facts --extra-vars "gather_subset=network" playbook.yml

# Gather facts with timeout
ansible-playbook --gather-facts --extra-vars "gather_timeout=30" playbook.yml
```

## Using Facts in Playbooks

### Conditional Logic
```yaml
---
- name: Configure based on OS family
  hosts: all
  tasks:
    - name: Install package on Debian/Ubuntu
      apt:
        name: nginx
        state: present
      when: ansible_os_family == "Debian"

    - name: Install package on RHEL/CentOS
      yum:
        name: nginx
        state: present
      when: ansible_os_family == "RedHat"
```

### Dynamic Variables
```yaml
---
- name: Use facts for dynamic configuration
  hosts: all
  vars:
    config_file: "{{ '/etc/nginx/nginx.conf' if ansible_os_family == 'Debian' else '/etc/nginx/nginx.conf' }}"
    service_name: "{{ 'nginx' if ansible_distribution_major_version|int >= 8 else 'nginx' }}"
  
  tasks:
    - name: Deploy configuration
      template:
        src: nginx.conf.j2
        dest: "{{ config_file }}"
      notify: restart nginx
```

### Template Selection
```yaml
---
- name: Select templates based on distribution
  hosts: all
  tasks:
    - name: Deploy distribution-specific configuration
      template:
        src: "{{ ansible_distribution | lower }}.conf.j2"
        dest: "/etc/myapp/config.conf"
```

## Common Facts Reference

### Operating System Facts
- `ansible_os_family`: OS family (Debian, RedHat, etc.)
- `ansible_distribution`: Distribution name (Ubuntu, CentOS, etc.)
- `ansible_distribution_version`: Distribution version
- `ansible_distribution_major_version`: Major version number
- `ansible_kernel`: Kernel version
- `ansible_architecture`: System architecture (x86_64, etc.)

### Network Facts
- `ansible_default_ipv4.address`: Default IPv4 address
- `ansible_default_ipv4.gateway`: Default gateway
- `ansible_all_ipv4_addresses`: All IPv4 addresses
- `ansible_fqdn`: Fully qualified domain name
- `ansible_hostname`: Short hostname
- `ansible_domain`: Domain name

### Hardware Facts
- `ansible_memtotal_mb`: Total memory in MB
- `ansible_processor_count`: Number of CPUs
- `ansible_processor_cores`: CPU cores
- `ansible_mounts`: List of mounted filesystems
- `ansible_devices`: Available block devices

### Software Facts
- `ansible_python_version`: Python version
- `ansible_ssh_host_key_*`: SSH host keys
- `ansible_user_id`: Current user ID
- `ansible_user_uid`: Current user UID

## Advanced Usage Patterns

### Dynamic Inventory Groups
```yaml
---
- name: Group hosts by facts
  hosts: all
  tasks:
    - name: Add web servers to group
      group_by:
        key: "web_{{ ansible_os_family }}"
      when: "'nginx' in ansible_facts.packages"

    - name: Add database servers to group
      group_by:
        key: "db_{{ ansible_os_family }}"
      when: "'postgresql' in ansible_facts.packages"
```

### Performance-Based Configuration
```yaml
---
- name: Configure based on system resources
  hosts: all
  tasks:
    - name: Set worker processes based on CPU count
      set_fact:
        nginx_workers: "{{ ansible_processor_count }}"
      
    - name: Configure nginx for high-memory systems
      template:
        src: nginx-high-memory.conf.j2
        dest: /etc/nginx/nginx.conf
      when: ansible_memtotal_mb > 4096

    - name: Configure nginx for low-memory systems
      template:
        src: nginx-low-memory.conf.j2
        dest: /etc/nginx/nginx.conf
      when: ansible_memtotal_mb <= 4096
```

### Environment-Specific Deployment
```bash
# Use facts in conditionals
ansible-playbook --extra-vars "target_os={{ ansible_os_family }}" playbook.yml

# Template selection based on facts
ansible-playbook --extra-vars "template={{ ansible_distribution }}" playbook.yml

# Multi-environment deployment
ansible-playbook --extra-vars "env={{ ansible_environment | default('dev') }}" playbook.yml
```

## Custom Facts

### Setting Custom Facts
```yaml
---
- name: Set custom facts
  hosts: all
  tasks:
    - name: Create custom fact directory
      file:
        path: /etc/ansible/facts.d
        state: directory
        mode: '0755'

    - name: Deploy custom fact
      copy:
        content: |
          [application]
          version=1.2.3
          environment=production
          datacenter=us-east-1
        dest: /etc/ansible/facts.d/app_info.fact
        mode: '0644'
```

### Using Custom Facts
```yaml
---
- name: Use custom facts
  hosts: all
  tasks:
    - name: Configure application version
      debug:
        msg: "Application version: {{ ansible_local.app_info.version }}"

    - name: Set environment-specific configuration
      set_fact:
        app_config: "{{ 'prod-config.yml' if ansible_local.app_info.environment == 'production' else 'dev-config.yml' }}"
```

## Best Practices

### Performance Optimization
1. **Disable fact gathering** when not needed for performance
2. **Use targeted fact gathering** with `gather_subset` for specific information
3. **Cache facts** for large deployments using fact caching
4. **Set appropriate timeouts** for slow network connections

### Fact Caching
```ini
# ansible.cfg
[gathering]
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts_cache
fact_caching_timeout = 86400
```

### Security Considerations
1. **Filter sensitive facts** in output using `no_log: true`
2. **Use fact encryption** for sensitive custom facts
3. **Limit fact exposure** in multi-tenant environments
4. **Validate fact values** before using in security contexts

### Reliability
1. **Always check fact existence** before using (`ansible_os_family is defined`)
2. **Provide default values** for missing facts (`ansible_os_family | default('Unknown')`)
3. **Use version comparisons** carefully (`ansible_distribution_version is version('20.04', '>=')`)
4. **Test across platforms** to ensure fact compatibility

## Troubleshooting

### Common Issues
1. **Missing facts**: Check if fact gathering is enabled
2. **Incorrect fact values**: Verify fact gathering permissions
3. **Performance issues**: Consider fact caching or targeted gathering
4. **Custom facts not loading**: Check file permissions and syntax

### Debugging Facts
```bash
# Gather all facts and display
ansible all -m setup

# Gather specific facts
ansible all -m setup -a 'filter=ansible_distribution*'

# Test fact gathering
ansible-playbook --check --gather-facts playbook.yml

# Debug fact usage
ansible-playbook -vvv --gather-facts playbook.yml
```

### Fact Validation
```yaml
---
- name: Validate required facts
  hosts: all
  tasks:
    - name: Check if OS is supported
      fail:
        msg: "Unsupported OS: {{ ansible_os_family }}"
      when: ansible_os_family not in ['Debian', 'RedHat']

    - name: Validate minimum memory
      fail:
        msg: "Insufficient memory: {{ ansible_memtotal_mb }}MB < 1024MB"
      when: ansible_memtotal_mb < 1024
```