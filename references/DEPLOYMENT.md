# Ansible Deployment Workflows

## Deployment Patterns

### 1. Rolling Deployment
```yaml
---
- name: Rolling deployment
  hosts: webservers
  serial: 1
  tasks:
    - name: Deploy application
      git:
        repo: "{{ app_repo }}"
        dest: "{{ app_path }}"
        version: "{{ app_version }}"
    
    - name: Install dependencies
      pip:
        requirements: "{{ app_path }}/requirements.txt"
    
    - name: Restart application
      service:
        name: "{{ app_name }}"
        state: restarted
```

### 2. Blue-Green Deployment
```yaml
---
- name: Blue-green deployment
  hosts: loadbalancer
  tasks:
    - name: Switch to green environment
      haproxy:
        backend: app_servers
        state: present
        host: "{{ green_servers }}"

- name: Deploy to blue
  hosts: blue_servers
  tasks:
    - name: Deploy application
      git:
        repo: "{{ app_repo }}"
        dest: "{{ app_path }}"
        version: "{{ app_version }}"
```

### 3. Canary Deployment
```yaml
---
- name: Canary deployment
  hosts: canary_servers
  tasks:
    - name: Deploy new version
      git:
        repo: "{{ app_repo }}"
        dest: "{{ app_path }}"
        version: "{{ new_version }}"
    
    - name: Health check
      uri:
        url: "http://{{ inventory_hostname }}/health"
        method: GET
      register: health
      retries: 5
      delay: 10
      until: health.status == 200
```

## CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/ansible.yml
name: Ansible Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Ansible
        run: pip install ansible
      - name: Run Ansible
        run: ansible-playbook -i inventory deploy.yml
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    stages {
        stage('Deploy') {
            steps {
                sh 'ansible-playbook -i production deploy.yml'
            }
        }
    }
}
```

## Environment Management

### Multi-Environment Setup
```yaml
# group_vars/all.yml
app_name: myapp
app_repo: https://github.com/user/myapp.git

# group_vars/development.yml
app_version: develop
app_path: /opt/myapp-dev

# group_vars/production.yml
app_version: main
app_path: /opt/myapp
```

## Rollback Strategies

### Versioned Rollback
```yaml
---
- name: Rollback deployment
  hosts: webservers
  vars:
    rollback_version: "{{ previous_version }}"
  tasks:
    - name: Checkout previous version
      git:
        repo: "{{ app_repo }}"
        dest: "{{ app_path }}"
        version: "{{ rollback_version }}"
    
    - name: Restart services
      service:
        name: "{{ app_name }}"
        state: restarted
```

## Monitoring and Alerting

### Deployment Verification
```yaml
- name: Verify deployment
  uri:
    url: "http://{{ inventory_hostname }}:8080/health"
    method: GET
  register: health_check
  failed_when: health_check.status != 200

- name: Send alert on failure
  slack:
    token: "{{ slack_token }}"
    channel: "#deployments"
    msg: "Deployment failed on {{ inventory_hostname }}"
  when: health_check.failed
```

## Best Practices

1. **Check mode** - use `--check` for dry runs
2. **Idempotency** - ensure safe re-runs
3. **Rollback** - always have rollback plan
4. **Monitoring** - verify deployment success
5. **Testing** - test in staging first