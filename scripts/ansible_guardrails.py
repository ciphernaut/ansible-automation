#!/usr/bin/env python3
"""
Ansible Guardrails Framework
Prevents AI from falling into non-Ansible patterns and enforces proper IaC thinking
"""

import argparse
import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Import context preservation
CONTEXT_AVAILABLE = False
try:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from context_preserver import preserve_ansible_context, get_ansible_reminders
    CONTEXT_AVAILABLE = True
except ImportError:
    pass

class AnsibleGuardrails:
    def __init__(self, inventory_path: Optional[str] = None):
        self.inventory_path = inventory_path
        self.operation_log = []
        self.decision_tree = self._load_decision_tree()
        
    def _load_decision_tree(self) -> Dict[str, Any]:
        """Load decision tree for Ansible-native operations"""
        return {
            "file_operations": {
                "edit_file": ["template", "lineinfile", "blockinfile", "copy"],
                "create_file": ["copy", "template", "file"],
                "delete_file": ["file", "lineinfile"],
                "check_content": ["stat", "shell", "command"],
                "modify_permissions": ["file", "template"]
            },
            "service_operations": {
                "start_service": ["systemd", "service"],
                "stop_service": ["systemd", "service"],
                "restart_service": ["systemd", "service"],
                "check_status": ["service_facts", "systemd", "shell"],
                "enable_service": ["systemd", "service"]
            },
            "package_operations": {
                "install_package": ["apt", "yum", "dnf", "package", "pip"],
                "remove_package": ["apt", "yum", "dnf", "package", "pip"],
                "update_packages": ["apt", "yum", "dnf", "package"],
                "check_installed": ["package_facts", "command"]
            },
            "user_operations": {
                "create_user": ["user", "group"],
                "delete_user": ["user"],
                "manage_keys": ["authorized_key", "user"],
                "check_user": ["user", "getent"]
            },
            "network_operations": {
                "download_file": ["get_url", "uri"],
                "check_connectivity": ["wait_for", "uri", "shell"],
                "manage_firewall": ["ufw", "firewalld", "iptables"],
                "dns_operations": ["shell", "lineinfile"]
            }
        }
    
    def analyze_operation(self, operation_type: str, operation_details: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze proposed operation and suggest Ansible-native approach"""
        
        # Preserve context if available
        if CONTEXT_AVAILABLE:
            try:
                preserve_ansible_context(operation_type, operation_details)
            except Exception:
                pass  # Silently fail if context preservation fails
        analysis = {
            "operation_type": operation_type,
            "proposed_approach": operation_details,
            "ansible_native": False,
            "recommended_modules": [],
            "guardrails_violations": [],
            "suggested_tasks": []
        }
        
        # Check if operation has Ansible-native solution
        if operation_type in self.decision_tree:
            analysis["ansible_native"] = True
            analysis["recommended_modules"] = self.decision_tree[operation_type]
        
        # Check for common anti-patterns
        violations = self._check_guardrails_violations(operation_type, operation_details)
        analysis["guardrails_violations"] = violations
        
        # Generate suggested Ansible tasks
        if analysis["ansible_native"]:
            analysis["suggested_tasks"] = self._generate_ansible_tasks(operation_type, operation_details)
        
        return analysis
    
    def _check_guardrails_violations(self, operation_type: str, operation_details: Dict[str, Any]) -> List[str]:
        """Check for common AI-Ansible anti-patterns"""
        violations = []
        
        # Check for direct shell commands
        if "shell" in str(operation_details).lower() and operation_type != "network_operations":
            violations.append("SHELL_AVOIDANCE: Consider using specific Ansible modules instead of shell")
        
        # Check for direct SSH operations
        if "ssh" in str(operation_details).lower():
            violations.append("SSH_DIRECTIVE: Use Ansible inventory instead of direct SSH")
        
        # Check for manual file editing without state management
        if operation_type == "file_operations" and "edit" in str(operation_details).lower():
            if "state" not in str(operation_details).lower():
                violations.append("STATELESS_EDITING: File operations should include state management")
        
        # Check for missing inventory consideration
        if "hosts" not in str(operation_details).lower() and self.inventory_path:
            violations.append("INVENTORY_NEGLECT: Operations should specify target hosts/groups")
        
        # Check for missing idempotence
        if "check_mode" not in str(operation_details).lower() and operation_type in ["file_operations", "service_operations"]:
            violations.append("IDEMPOTENCE_MISSING: Consider check mode validation")
        
        return violations
    
    def _generate_ansible_tasks(self, operation_type: str, operation_details: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate Ansible task templates for operation"""
        tasks = []
        
        if operation_type == "file_operations":
            if operation_details.get("action") == "edit_file":
                tasks.append({
                    "name": f"Ensure {operation_details.get('file_path', 'config file')} has correct content",
                    "lineinfile": {
                        "path": operation_details.get("file_path"),
                        "line": operation_details.get("content", ""),
                        "create": operation_details.get("create", False),
                        "backup": True
                    }
                })
            elif operation_details.get("action") == "create_file":
                tasks.append({
                    "name": f"Create {operation_details.get('file_path', 'file')}",
                    "copy": {
                        "content": operation_details.get("content", ""),
                        "dest": operation_details.get("file_path"),
                        "backup": True
                    }
                })
        
        elif operation_type == "service_operations":
            if operation_details.get("action") == "start_service":
                tasks.append({
                    "name": f"Ensure {operation_details.get('service_name', 'service')} is running",
                    "systemd": {
                        "name": operation_details.get("service_name"),
                        "state": "started",
                        "enabled": operation_details.get("enabled", True)
                    }
                })
        
        return tasks
    
    def discover_variable_truth(self, variable_name: Optional[str] = None, host: Optional[str] = None, group: Optional[str] = None) -> Dict[str, Any]:
        """Discover variable truth using ansible-inventory tools"""
        if not self.inventory_path:
            return {"error": "No inventory path provided"}
        
        discovery = {
            "inventory_path": self.inventory_path,
            "variable_name": variable_name,
            "timestamp": datetime.now().isoformat(),
            "inventory_structure": {},
            "variable_values": {},
            "precedence_info": {}
        }
        
        try:
            # Get complete inventory structure
            result = subprocess.run([
                "ansible-inventory", "-i", self.inventory_path, "--list"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                discovery["inventory_structure"] = json.loads(result.stdout)
            
            # Get inventory graph with variables
            result = subprocess.run([
                "ansible-inventory", "-i", self.inventory_path, "--graph", "--vars"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                discovery["graph_with_vars"] = result.stdout
            
            # Get specific variable information
            if variable_name:
                if host:
                    result = subprocess.run([
                        "ansible-inventory", "-i", self.inventory_path, "--host", host, "--vars"
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        discovery["variable_values"][host] = self._parse_vars_output(result.stdout, variable_name)
                
                elif group:
                    result = subprocess.run([
                        "ansible-inventory", "-i", self.inventory_path, "--group", group, "--vars"
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        discovery["variable_values"][group] = self._parse_vars_output(result.stdout, variable_name)
                
                else:
                    # Search for variable across all hosts
                    result = subprocess.run([
                        "ansible-inventory", "-i", self.inventory_path, "--vars"
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        all_vars = result.stdout
                        discovery["variable_values"]["all_hosts"] = self._parse_vars_output(all_vars, variable_name)
            
        except subprocess.TimeoutExpired:
            discovery["error"] = "Variable discovery timed out"
        except Exception as e:
            discovery["error"] = f"Variable discovery failed: {e}"
        
        return discovery
    
    def _parse_vars_output(self, vars_output: str, target_var: str) -> Dict[str, str]:
        """Parse variable output to find target variable values"""
        var_values = {}
        
        for line in vars_output.split('\n'):
            if target_var and target_var in line:
                # Extract variable value from ansible-inventory output
                if '=' in line:
                    var_part = line.split('=')[1].strip()
                    var_values[target_var] = var_part.strip('"\'')
        
        return var_values
    
    def propose_ansible_solution(self, problem_description: str, target_hosts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Propose Ansible-native solution for a given problem"""
        solution = {
            "problem": problem_description,
            "proposed_solution": {},
            "ansible_tasks": [],
            "debugging_approach": [],
            "verification_tasks": []
        }
        
        # Analyze problem type
        problem_lower = problem_description.lower()
        
        if "file" in problem_lower or "config" in problem_lower:
            solution["proposed_solution"] = self._analyze_file_problem(problem_description)
        elif "service" in problem_lower or "running" in problem_lower:
            solution["proposed_solution"] = self._analyze_service_problem(problem_description)
        elif "package" in problem_lower or "install" in problem_lower:
            solution["proposed_solution"] = self._analyze_package_problem(problem_description)
        elif "user" in problem_lower or "permission" in problem_lower:
            solution["proposed_solution"] = self._analyze_user_problem(problem_description)
        elif "network" in problem_lower or "connect" in problem_lower:
            solution["proposed_solution"] = self._analyze_network_problem(problem_description)
        
        # Generate debugging approach
        solution["debugging_approach"] = [
            "Use ansible-playbook --check --diff for dry-run analysis",
            "Use ansible-inventory --graph --vars to understand variable hierarchy",
            "Use appropriate Ansible modules instead of shell commands",
            "Implement proper error handling and idempotence"
        ]
        
        # Generate verification tasks
        solution["verification_tasks"] = [
            {
                "name": "Verify changes were applied correctly",
                "assert": {
                    "that": "verification_condition_here"
                }
            }
        ]
        
        return solution
    
    def _analyze_file_problem(self, problem: str) -> Dict[str, Any]:
        """Analyze file-related problems and suggest Ansible solutions"""
        return {
            "type": "file_operation",
            "recommended_modules": ["template", "lineinfile", "copy", "stat"],
            "approach": "Use file management modules with proper state handling",
            "example_tasks": [
                {
                    "name": "Ensure configuration file has correct content",
                    "template": {
                        "src": "templates/config.j2",
                        "dest": "/etc/app/config.conf",
                        "backup": True,
                        "notify": "restart service"
                    }
                }
            ]
        }
    
    def _analyze_service_problem(self, problem: str) -> Dict[str, Any]:
        """Analyze service-related problems"""
        return {
            "type": "service_operation",
            "recommended_modules": ["systemd", "service", "service_facts"],
            "approach": "Use service management modules with proper state checking",
            "example_tasks": [
                {
                    "name": "Ensure service is running and enabled",
                    "systemd": {
                        "name": "app-service",
                        "state": "started",
                        "enabled": True
                    }
                }
            ]
        }
    
    def _analyze_package_problem(self, problem: str) -> Dict[str, Any]:
        """Analyze package-related problems"""
        return {
            "type": "package_operation",
            "recommended_modules": ["apt", "yum", "dnf", "package", "package_facts"],
            "approach": "Use package management modules with proper state handling",
            "example_tasks": [
                {
                    "name": "Ensure package is installed",
                    "package": {
                        "name": "required-package",
                        "state": "present"
                    }
                }
            ]
        }
    
    def _analyze_user_problem(self, problem: str) -> Dict[str, Any]:
        """Analyze user/permission-related problems"""
        return {
            "type": "user_operation",
            "recommended_modules": ["user", "group", "authorized_key", "getent"],
            "approach": "Use user management modules with proper security",
            "example_tasks": [
                {
                    "name": "Ensure user exists with correct permissions",
                    "user": {
                        "name": "app-user",
                        "state": "present",
                        "groups": ["app-group"],
                        "shell": "/bin/bash"
                    }
                }
            ]
        }
    
    def _analyze_network_problem(self, problem: str) -> Dict[str, Any]:
        """Analyze network-related problems"""
        return {
            "type": "network_operation",
            "recommended_modules": ["uri", "get_url", "wait_for", "ufw"],
            "approach": "Use network modules with proper error handling",
            "example_tasks": [
                {
                    "name": "Ensure network connectivity",
                    "wait_for": {
                        "host": "{{ target_host }}",
                        "port": 80,
                        "timeout": 30
                    }
                }
            ]
        }
    
    def generate_debugging_playbook(self, problem: str, inventory: str, output_path: str = "/tmp/debug_playbook.yml") -> Dict[str, Any]:
        """Generate debugging playbook with proper Ansible patterns"""
        playbook = {
            "name": f"Debugging: {problem}",
            "hosts": "{{ target_hosts | default('all') }}",
            "become": True,
            "vars": {
                "debug_timestamp": "{{ ansible_date_time }}",
                "problem_description": problem
            },
            "tasks": []
        }
        
        # Add inventory discovery tasks
        playbook["tasks"].extend([
            {
                "name": "Discover inventory structure",
                "debug": {
                    "msg": "Current host: {{ inventory_hostname }}, Groups: {{ group_names }}"
                }
            },
            {
                "name": "Show variable hierarchy for debugging",
                "debug": {
                    "msg": "Key variables for {{ inventory_hostname }}: Environment: {{ ansible_env }}, Distribution: {{ ansible_distribution }}, Custom vars: {{ hostvars[inventory_hostname] | dict2items | selectattr('1', 'in', custom_vars_list) | list }}"
                }
            }
        ])
        
        # Add problem-specific debugging tasks
        solution = self.propose_ansible_solution(problem)
        for task in solution.get("ansible_tasks", []):
            task["name"] = f"DEBUG: {task.get('name', 'Debug task')}"
            task["tags"] = ["debug"]
            playbook["tasks"].append(task)
        
        # Add verification tasks
        for task in solution.get("verification_tasks", []):
            task["name"] = f"VERIFY: {task.get('name', 'Verification')}"
            task["tags"] = ["verify"]
            playbook["tasks"].append(task)
        
        # Save playbook
        try:
            import yaml
            with open(output_path, 'w') as f:
                yaml.dump(playbook, f, default_flow_style=False)
            
            return {
                "success": True,
                "playbook_path": output_path,
                "tasks_count": len(playbook["tasks"]),
                "debug_tags": ["debug", "verify"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate playbook: {e}"
            }
    
    def check_ansible_compliance(self, proposed_action: str) -> Dict[str, Any]:
        """Check if proposed action follows Ansible best practices"""
        compliance = {
            "compliant": True,
            "violations": [],
            "recommendations": [],
            "ansible_alternatives": []
        }
        
        action_lower = proposed_action.lower()
        
        # Check for shell command usage
        if any(cmd in action_lower for cmd in ["ssh ", "scp ", "rsync "]):
            compliance["compliant"] = False
            compliance["violations"].append("DIRECT_SSH_USAGE: Use Ansible inventory instead of direct SSH")
            compliance["ansible_alternatives"].append("Use ansible-playbook with proper inventory targeting")
        
        # Check for manual file editing
        if any(cmd in action_lower for cmd in ["vi ", "nano ", "vim ", "echo "]) and "file" in action_lower:
            compliance["compliant"] = False
            compliance["violations"].append("MANUAL_FILE_EDITING: Use Ansible file modules instead of manual editing")
            compliance["ansible_alternatives"].append("Use template, lineinfile, or copy modules")
        
        # Check for service management
        if "systemctl" in action_lower:
            compliance["compliant"] = False
            compliance["violations"].append("DIRECT_SYSTEMCTL: Use systemd or service modules")
            compliance["ansible_alternatives"].append("Use systemd module for service management")
        
        # Check for package management
        if any(cmd in action_lower for cmd in ["apt-get ", "yum install ", "pip install "]):
            compliance["compliant"] = False
            compliance["violations"].append("DIRECT_PACKAGE_INSTALL: Use Ansible package modules")
            compliance["ansible_alternatives"].append("Use apt, yum, or package modules")
        
        return compliance

def main():
    parser = argparse.ArgumentParser(
        description="Ansible Guardrails Framework - Enforce Ansible-native thinking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i inventory/hosts --analyze-operation "edit_file:/etc/nginx.conf"
  %(prog)s -i inventory/hosts --discover-var app_version
  %(prog)s -i inventory/hosts --generate-debug-playbook "nginx not starting"
  %(prog)s --check-compliance "ssh to server and edit config file"
        """
    )
    
    # Show context reminders if available
    if CONTEXT_AVAILABLE:
        try:
            reminders = get_ansible_reminders()
            if reminders:
                print("📋 Ansible Reminders:")
                for reminder in reminders[:3]:  # Show top 3
                    print(f"  • {reminder}")
                print()
        except Exception:
            pass
    
    parser.add_argument("-i", "--inventory", help="Inventory file path")
    parser.add_argument("--analyze-operation", 
                       help="Analyze operation and suggest Ansible-native approach (format: type:details)")
    parser.add_argument("--discover-var", help="Discover variable truth across inventory")
    parser.add_argument("--host", help="Target host for variable discovery")
    parser.add_argument("--group", help="Target group for variable discovery")
    parser.add_argument("--generate-debug-playbook", help="Generate debugging playbook for problem")
    parser.add_argument("--output-dir", default="/tmp/ansible_guardrails",
                       help="Output directory for generated files")
    parser.add_argument("--check-compliance", help="Check if action follows Ansible best practices")
    
    args = parser.parse_args()
    
    # Initialize guardrails
    guardrails = AnsibleGuardrails(args.inventory)
    
    try:
        if args.analyze_operation:
            # Analyze specific operation
            parts = args.analyze_operation.split(":", 1)
            if len(parts) == 2:
                operation_type = parts[0]
                operation_details = {"action": parts[1]}
                
                analysis = guardrails.analyze_operation(operation_type, operation_details)
                
                print("🔍 Operation Analysis:")
                print(f"  Type: {analysis['operation_type']}")
                print(f"  Ansible-Native: {'✓' if analysis['ansible_native'] else '✗'}")
                
                if analysis["recommended_modules"]:
                    print(f"  Recommended Modules: {', '.join(analysis['recommended_modules'])}")
                
                if analysis["guardrails_violations"]:
                    print(f"  ⚠️  Guardrails Violations:")
                    for violation in analysis["guardrails_violations"]:
                        print(f"    • {violation}")
                
                if analysis["suggested_tasks"]:
                    print(f"  📋 Suggested Tasks:")
                    for task in analysis["suggested_tasks"]:
                        print(f"    - {task.get('name', 'Task')}")
            
        elif args.discover_var:
            # Discover variable truth
            discovery = guardrails.discover_variable_truth(args.discover_var, args.host, args.group)
            
            if discovery.get("error"):
                print(f"❌ Error: {discovery['error']}")
            else:
                print("🔍 Variable Discovery Results:")
                print(f"  Variable: {discovery['variable_name']}")
                print(f"  Inventory: {discovery['inventory_path']}")
                
                if discovery.get("variable_values"):
                    print("  Values Found:")
                    for scope, values in discovery["variable_values"].items():
                        print(f"    {scope}: {values}")
        
        elif args.generate_debug_playbook:
            # Generate debugging playbook
            output_path = f"{args.output_dir}/debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yml"
            os.makedirs(args.output_dir, exist_ok=True)
            
            result = guardrails.generate_debugging_playbook(args.generate_debug_playbook, args.inventory, output_path)
            
            if result["success"]:
                print(f"📄 Debugging playbook generated: {result['playbook_path']}")
                print(f"  Tasks: {result['tasks_count']}")
                print(f"  Tags: {', '.join(result['debug_tags'])}")
                print(f"\n🚀 Run with: ansible-playbook -i {args.inventory} {result['playbook_path']} --tags debug")
            else:
                print(f"❌ Failed to generate playbook: {result['error']}")
        
        elif args.check_compliance:
            # Check compliance
            compliance = guardrails.check_ansible_compliance(args.check_compliance)
            
            print("🔍 Compliance Check:")
            print(f"  Compliant: {'✓' if compliance['compliant'] else '✗'}")
            
            if compliance["violations"]:
                print("  Violations:")
                for violation in compliance["violations"]:
                    print(f"    • {violation}")
            
            if compliance["ansible_alternatives"]:
                print("  Ansible Alternatives:")
                for alt in compliance["ansible_alternatives"]:
                    print(f"    • {alt}")
        
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()