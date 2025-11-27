# Community Modules and Collections

## Essential Collections

### 1. community.general
```bash
ansible-galaxy collection install community.general
```

**Key Modules:**
- `apt_key` - APT key management
- `sysctl` - Kernel parameters
- `timezone` - System timezone
- `ufw` - Firewall management
- `docker_*` - Docker containers

### 2. community.crypto
```bash
ansible-galaxy collection install community.crypto
```

**Key Modules:**
- `openssl_*` - Certificate management
- `acme_*` - Let's Encrypt certificates
- `openssh_keypair` - SSH key generation

### 3. community.docker
```bash
ansible-galaxy collection install community.docker
```

**Key Modules:**
- `docker_*` - Docker container management
- `docker_compose` - Docker Compose

### 4. ansible.posix
```bash
ansible.galaxy collection install ansible.posix
```

**Key Modules:**
- `firewalld` - Firewalld management**
- `selinux` - SELinux configuration
- `authorized_key` - SSH keys

## Module Discovery

### Search Collections
```bash
# Search for modules
ansible-galaxy search database

# List installed collections
ansible-galaxy collection list

# Get collection info
ansible-galaxy collection info community.general
```

### Module Documentation
```bash
# Get module help
ansible-doc community.general.apt

# List all modules in collection
ansible-doc -l | grep community.general
```

## Using Community Modules

### Example: SSL Certificate
```yaml
- name: Generate SSL certificate
  community.crypto.x509_certificate:
    path: /etc/ssl/certs/app.crt
    privatekey_path: /etc/ssl/private/app.key
    provider: selfsigned
    selfsigned_not_after: "+3650d"
```

### Example: Docker Container
```yaml
- name: Run Docker container
  community.docker.docker_container:
    name: webapp
    image: nginx:latest
    state: started
    ports:
      - "80:80"
    volumes:
      - "/opt/webapp:/usr/share/nginx/html"
```

### Example: Firewall Rules
```yaml
- name: Allow HTTP traffic
  ansible.posix.firewalld:
    service: http
    state: enabled
    permanent: yes
    immediate: yes
```

## Collection Development

### Create Collection
```bash
ansible-galaxy collection init myorg.mycollection
```

### Collection Structure
```
myorg.mycollection/
├── plugins/
│   ├── modules/
│   ├── filter/
│   └── lookup/
├── roles/
├── docs/
├── tests/
└──.yml
```

### Custom Module
```python
# plugins/modules/my_module.py
from ansible.module_utils.basic import AnsibleModule

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, type='str'),
            state=dict(default='present', choices=['present', 'absent'])
        )
    )
    
    # Module logic here
    module.exit_json(changed=True)
```

## Best Practices

1. **Pin versions** for reproducibility
2. **Check compatibility** with Ansible core
3. **Use collections** over ad-hoc scripts
4. **Document usage** in playbooks
5. **Test modules** before production use

## Common Issues

### Version Conflicts
```yaml
# requirements.yml
collections:
  - name: community.general
    version: ">=3.0.0,<4.0.0"
  - name: community.docker
    version: ">=1.0.0"
```

### Namespace Conflicts
```yaml
# Use fully qualified names
- name: Install package
  community.general.apt:
    name: nginx
    state: present
```