# Ansible Role Patterns

## Role Structure
```
role_name/
├── tasks/
│   └── main.yml
├── handlers/
│   └── main.yml
├── templates/
├── files/
├── vars/
│   └── main.yml
├── defaults/
│   └── main.yml
└── meta/
    └── main.yml
```

## Common Role Patterns

### 1. Service Installation
```yaml
# tasks/main.yml
- name: Install package
  package:
    name: "{{ service_package }}"
    state: present

- name: Start and enable service
  service:
    name: "{{ service_name }}"
    state: started
    enabled: true
```

### 2. Configuration Management
```yaml
# tasks/main.yml
- name: Create config directory
  file:
    path: "{{ config_dir }}"
    state: directory
    mode: '0755'

- name: Deploy config template
  template:
    src: config.j2
    dest: "{{ config_dir }}/config.conf"
    notify: restart service
```

### 3. User Management
```yaml
# tasks/main.yml
- name: Create user
  user:
    name: "{{ app_user }}"
    system: true
    shell: /bin/bash
    create_home: true

- name: Set up SSH key
  authorized_key:
    user: "{{ app_user }}"
    state: present
    key: "{{ ssh_public_key }}"
```

## Role Dependencies

### Meta Dependencies
```yaml
# meta/main.yml
dependencies:
  - role: geerlingguy.nginx
  - role: geerlingguy.php
    vars:
      php_enable_webserver: false
```

### Conditional Dependencies
```yaml
# meta/main.yml
dependencies:
  - role: geerlingguy.firewall
    when: configure_firewall | default(true)
```

## Variable Precedence

1. Command line values (-e, --extra-vars)
2. Role defaults (defaults/main.yml)
3. Inventory vars
4. Playbook vars
5. Role vars (vars/main.yml)

## Best Practices

1. **Idempotent tasks** - can run multiple times safely
2. **Handlers** - use for service restarts
3. **Defaults** - provide sensible defaults
4. **Variables** - make roles configurable
5. **Testing** - use molecule for role testing