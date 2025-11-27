# Ansible Inventory Management

## Inventory Types

### Static Inventory (INI format)
```ini
[webservers]
web1.example.com ansible_user=ubuntu
web2.example.com ansible_user=ubuntu

[database]
db1.example.com ansible_user=admin

[all:vars]
ansible_ssh_private_key_file=~/.ssh/ansible_key
```

### YAML Inventory
```yaml
all:
  children:
    webservers:
      hosts:
        web1.example.com:
          ansible_user: ubuntu
        web2.example.com:
          ansible_user: ubuntu
    database:
      hosts:
        db1.example.com:
          ansible_user: admin
  vars:
    ansible_ssh_private_key_file: ~/.ssh/ansible_key
```

### Dynamic Inventory
Use scripts or cloud plugins:
```bash
# AWS
ansible-inventory -i aws_ec2.yml --list

# Script
ansible-inventory -i inventory.sh --list
```

## SSH Configuration

### SSH Config Generation
```bash
python3 scripts/inventory_manager.py create_ssh inventory.yml ssh_config
```

### Key Management
```bash
# Generate key
ssh-keygen -t rsa -b 4096 -f ansible_key

# Copy to hosts
ssh-copy-id -i ansible_key.pub user@host
```

## Connection Methods

### SSH (Default)
```yaml
ansible_connection: ssh
ansible_port: 22
ansible_user: ubuntu
```

### WinRM (Windows)
```yaml
ansible_connection: winrm
ansible_port: 5986
ansible_user: Administrator
ansible_password: "{{ winrm_password }}"
```

### Docker
```yaml
ansible_connection: docker
ansible_host: container_name
```

## Best Practices

1. **Use groups** for logical organization
2. **Separate secrets** from inventory
3. **Use variables** for common settings
4. **Test connectivity** before deployment
5. **Document inventory structure**