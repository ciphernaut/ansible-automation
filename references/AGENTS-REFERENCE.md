# AGENTS.md Reference for ansible-automation Skill

This document provides templates and patterns for properly referencing the ansible-automation skill in project AGENTS.md files. Based on real-world usage patterns and agent behavior analysis.

## Why This Reference Is Needed

Coding agents naturally revert to familiar patterns (direct SSH, file editing, ad-hoc operations) unless explicitly constrained. Without strong imperatives, agents will bypass Ansible workflows even when instructed to use them.

## Progressive Prohibition Pattern

Based on observed agent behavior, implement prohibitions in this order:

### Level 1: Basic Imperative
Prevents direct system access but allows Ansible ad-hoc operations.

```markdown
#### ansible-automation (IMPERATIVE)
**ALL DEVELOPMENT MUST OCCUR THROUGH ANSIBLE PLAYBOOKS - THIS IS NON-NEGOTIABLE.**

- **ABSOLUTE PROHIBITION**: NEVER use direct SSH, scp, or any direct file access to target systems
- **Development Workflow**: All changes must be made through Ansible roles/tasks → run playbook
- **FORCED COMPLIANCE**: If you catch yourself attempting direct SSH, STOP and use Ansible instead
```

### Level 2: Ansible-First Imperative (Recommended)
Prevents ad-hoc write operations within Ansible, enforcing playbook-only workflow.

```markdown
#### ansible-automation (IMPERATIVE)
**ALL DEVELOPMENT MUST OCCUR THROUGH ANSIBLE PLAYBOOKS - THIS IS NON-NEGOTIABLE.** Think of this as keyhole surgery where Ansible is your ONLY instrument:

- **ABSOLUTE PROHIBITION**: NEVER use direct SSH, scp, ansible ad-hoc copy modules, or any direct file access to target systems. ALL interactions must be through Ansible playbooks ONLY
- **Development Workflow**: Never edit files directly on target systems. All changes must be made through Ansible roles/tasks → run playbook
- **INSPECTION & DEBUGGING**: Use Ansible ad-hoc commands with read-only modules (command, shell, stat, fetch) ONLY. Never SSH directly or use write modules ad-hoc
- **Testing Strategy**: Use `--check` and `--syntax-check` before every deployment. Test individual roles with `--tags`
- **Session Continuity**: Always reference this skill first when resuming work. Re-establish ansible-automation patterns before proceeding
- **App Development via Ansible**: 
  - Python code changes → update role files/templates → run playbook
  - Configuration changes → modify Jinja2 templates → deploy via Ansible
  - System inspection → use ansible ad-hoc commands with read-only modules ONLY (ansible all -i inventory.yml -m command/shell/stat)
  - Debugging → use Ansible ad-hoc read-only commands, never direct SSH or write operations
- **Validation**: Every change must be validated through Ansible testing commands before considering complete
- **FORCED COMPLIANCE**: If you catch yourself attempting direct SSH, file access, or ad-hoc write modules, STOP and use Ansible playbook instead
```

## When to Use Each Level

### Use Level 1 (Basic) When:
- Project allows mixed Ansible/ad-hoc workflows
- Quick debugging and inspection are priorities
- Team is experienced with Ansible guardrails

### Use Level 2 (Ansible-First) When:
- **Pure Ansible-first workflows** are required
- Infrastructure as Code compliance is mandatory
- Multiple developers need consistent patterns
- Audit trails and change management are critical

## Allowed vs Forbidden Operations

### ✅ Allowed (Read-Only Ad-Hoc Modules)
```bash
ansible all -i inventory.yml -m command -a "cat /var/log/app.log"
ansible all -i inventory.yml -m shell -a "systemctl status nginx"
ansible all -i inventory.yml -m stat -a "path=/etc/nginx/nginx.conf"
ansible all -i inventory.yml -m fetch -a "src=/var/log/app.log dest=logs/"
```

### ❌ Forbidden (Write Operations)
```bash
# Direct SSH/SCP
ssh user@server "vi /etc/config"
scp config.txt user@server:/etc/

# Ad-Hoc Write Modules
ansible all -i inventory.yml -m copy -a "src=config dest=/etc/config"
ansible all -i inventory.yml -m lineinfile -a "path=/etc/config regexp='^DEBUG' line='DEBUG=true'"
ansible all -i inventory.yml -m template -a "src=config.j2 dest=/etc/config"
```

### ✅ Required (Playbook-Based)
```bash
# All changes through playbooks
ansible-playbook -i inventory.yml deploy.yml --check --diff
ansible-playbook -i inventory.yml deploy.yml --tags config
```

## Integration with Other Skills

### Context7 Integration
```markdown
#### context7 MCP Service
- Documentation for [your-specific-services-here]
```

### Custom Skills
Add your own skill requirements after the ansible-automation imperative to maintain priority.

## AGENTS.md Size Optimization

For projects with strict line limits, use the compact version:

```markdown
#### ansible-automation (IMPERATIVE)
**ANSIBLE-ONLY WORKFLOW REQUIRED** - No direct SSH, ad-hoc write modules, or file access. Use playbooks for ALL changes. Read-only ad-hoc only for debugging (command, shell, stat, fetch). Reference ansible-automation skill first when resuming work.
```

## Implementation Checklist

- [ ] Choose appropriate imperative level based on workflow requirements
- [ ] Add to AGENTS.md under "Required Skills" section
- [ ] Test with common agent workflows to verify compliance
- [ ] Update team documentation on workflow changes
- [ ] Monitor for new violation patterns and update prohibitions accordingly

## Common Violations & Solutions

| Violation | Symptom | Solution |
|-----------|---------|----------|
| Direct SSH access | Agent suggests "ssh to server" | Add Level 1 imperative |
| Ad-hoc copy modules | Agent uses `ansible -m copy` | Upgrade to Level 2 imperative |
| File editing bypass | Agent edits files directly | Strengthen "Development Workflow" section |
| Session drift | Agent forgets Ansible patterns | Add "Session Continuity" requirement |

## Evolution Pattern

Expect to strengthen imperatives over time as agents discover new shortcuts:
1. **Initial**: Basic SSH prohibition
2. **Iteration 1**: Add ad-hoc write module prohibition  
3. **Iteration 2**: Specify allowed read-only modules
4. **Future**: Likely need to address other Ansible bypass patterns

Monitor agent behavior and update prohibitions accordingly.