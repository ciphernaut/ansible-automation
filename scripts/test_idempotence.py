#!/usr/bin/env python3
"""
Idempotence Testing Framework
Automated testing to ensure Ansible playbooks produce identical results across multiple executions
"""

import argparse
import json
import subprocess
import sys
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

class IdempotenceTester:
    def __init__(self, inventory: str, output_dir: str = "/tmp/idempotence_tests"):
        self.inventory = inventory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def test_idempotence(self, playbook: str, iterations: int = 3, 
                       extra_vars: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Test playbook idempotence over multiple executions"""
        print(f"🔄 Starting idempotence test for: {playbook}")
        print(f"📊 Running {iterations} iterations to detect non-idempotent behavior")
        
        results = []
        states = []
        
        for i in range(iterations):
            print(f"\n🚀 Iteration {i+1}/{iterations}")
            
            # Capture pre-execution state
            pre_state = self._capture_quick_state(f"iter_{i+1}_pre")
            
            # Run playbook
            playbook_result = self._run_playbook(playbook, extra_vars)
            
            # Capture post-execution state
            post_state = self._capture_quick_state(f"iter_{i+1}_post")
            
            # Analyze changes
            changes = self._analyze_state_changes(pre_state, post_state)
            
            # Extract changed tasks from output
            changed_tasks = self._extract_changed_tasks(playbook_result.get("stdout", ""))
            
            iteration_result = {
                "iteration": i+1,
                "returncode": playbook_result.get("returncode", 1),
                "success": playbook_result.get("returncode", 1) == 0,
                "changes": changes,
                "changed_tasks": changed_tasks,
                "pre_state": pre_state,
                "post_state": post_state
            }
            
            results.append(iteration_result)
            states.append(post_state)
            
            if iteration_result["success"]:
                print(f"  ✓ Iteration {i+1} completed successfully")
                print(f"  📋 Changes detected: {len(changes)}")
                print(f"  🔧 Tasks changed: {len(changed_tasks)}")
            else:
                print(f"  ✗ Iteration {i+1} failed")
                print(f"  ❌ Error: {playbook_result.get('stderr', 'Unknown error')}")
        
        # Analyze idempotence
        idempotence_analysis = self._analyze_idempotence(results, states)
        
        # Generate comprehensive report
        report = {
            "playbook": playbook,
            "inventory": self.inventory,
            "iterations": iterations,
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "idempotence_analysis": idempotence_analysis,
            "summary": {
                "idempotent": idempotence_analysis["idempotent"],
                "total_issues": len(idempotence_analysis["issues"]),
                "consistency_score": idempotence_analysis["consistency_score"],
                "recommendations": idempotence_analysis["recommendations"]
            }
        }
        
        # Save report
        report_file = self.output_dir / f"idempotence_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.write_text(json.dumps(report, indent=2))
        print(f"\n📄 Report saved: {report_file}")
        
        return report
    
    def _capture_quick_state(self, snapshot_name: str) -> Dict[str, Any]:
        """Capture essential state for idempotence testing"""
        snapshot_dir = self.output_dir / f"state_{snapshot_name}"
        snapshot_dir.mkdir(exist_ok=True)
        
        state = {
            "timestamp": datetime.now().isoformat(),
            "configs": {},
            "services": {},
            "files": {}
        }
        
        try:
            # Capture configuration file hashes
            config_result = subprocess.run([
                "ansible", "all", "-i", self.inventory, "-m", "shell",
                "-a", "find /etc -name '*.conf' -type f -exec md5sum {} \\; 2>/dev/null || true"
            ], capture_output=True, text=True, timeout=60)
            
            if config_result.returncode == 0:
                state["configs"] = self._parse_config_hashes(config_result.stdout)
            
            # Capture running services
            service_result = subprocess.run([
                "ansible", "all", "-i", self.inventory, "-m", "shell",
                "-a", "systemctl list-units --type=service --state=running --no-pager"
            ], capture_output=True, text=True, timeout=60)
            
            if service_result.returncode == 0:
                state["services"] = self._parse_service_status(service_result.stdout)
            
            # Capture key file states
            key_files = [
                "/etc/hosts", "/etc/resolv.conf", "/etc/hostname",
                "/etc/passwd", "/etc/group"
            ]
            
            for file_path in key_files:
                file_result = subprocess.run([
                    "ansible", "all", "-i", self.inventory, "-m", "shell",
                    f"-a", "test -f {file_path} && md5sum {file_path} || echo 'MISSING'"
                ], capture_output=True, text=True, timeout=30)
                
                if file_result.returncode == 0:
                    state["files"][file_path] = self._parse_file_hashes(file_result.stdout)
        
        except subprocess.TimeoutExpired:
            print(f"  ⚠️  State capture timeout for {snapshot_name}")
        except Exception as e:
            print(f"  ❌ State capture error for {snapshot_name}: {e}")
        
        return state
    
    def _parse_config_hashes(self, output: str) -> Dict[str, Dict[str, str]]:
        """Parse configuration file hashes from ansible output"""
        configs = defaultdict(dict)
        current_host = None
        
        for line in output.split('\n'):
            if line.strip():
                # Ansible output format: hostname | SUCCESS | rc=0 >>
                if ' | SUCCESS | ' in line:
                    current_host = line.split(' | ')[0]
                elif current_host and line.strip():
                    # Parse md5sum output: hash  filename
                    parts = line.strip().split('  ', 1)
                    if len(parts) == 2:
                        configs[current_host][parts[1]] = parts[0]
        
        return dict(configs)
    
    def _parse_service_status(self, output: str) -> Dict[str, List[str]]:
        """Parse service status from ansible output"""
        services = defaultdict(list)
        current_host = None
        
        for line in output.split('\n'):
            if line.strip():
                if ' | SUCCESS | ' in line:
                    current_host = line.split(' | ')[0]
                elif current_host and line.strip():
                    # Parse service line: service.service   loaded active running   description
                    if '.service' in line and 'running' in line:
                        service_name = line.split()[0]
                        services[current_host].append(service_name)
        
        return dict(services)
    
    def _parse_file_hashes(self, output: str) -> Dict[str, str]:
        """Parse file hashes from ansible output"""
        files = {}
        current_host = None
        
        for line in output.split('\n'):
            if line.strip():
                if ' | SUCCESS | ' in line:
                    current_host = line.split(' | ')[0]
                elif current_host and line.strip() and not line.startswith('MISSING'):
                    # Parse md5sum output: hash  filename
                    parts = line.strip().split('  ', 1)
                    if len(parts) == 2:
                        files[current_host] = parts[0]
        
        return files
    
    def _run_playbook(self, playbook: str, extra_vars: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Run ansible playbook and capture output"""
        cmd = ["ansible-playbook", "-i", self.inventory, playbook]
        
        if extra_vars:
            extra_vars_str = ",".join([f"{k}={v}" for k, v in extra_vars.items()])
            cmd.extend(["--extra-vars", extra_vars_str])
        
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Playbook execution timed out after 5 minutes",
                "returncode": 124
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": 1
            }
    
    def _analyze_state_changes(self, pre_state: Dict[str, Any], post_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze changes between pre and post states"""
        changes = []
        
        # Analyze configuration changes
        pre_configs = pre_state.get("configs", {})
        post_configs = post_state.get("configs", {})
        
        for host in set(pre_configs.keys()) | set(post_configs.keys()):
            pre_host_configs = pre_configs.get(host, {})
            post_host_configs = post_configs.get(host, {})
            
            # Find changed files
            all_files = set(pre_host_configs.keys()) | set(post_host_configs.keys())
            
            for file_path in all_files:
                pre_hash = pre_host_configs.get(file_path)
                post_hash = post_host_configs.get(file_path)
                
                if pre_hash != post_hash:
                    if pre_hash is None:
                        change_type = "added"
                    elif post_hash is None:
                        change_type = "removed"
                    else:
                        change_type = "modified"
                    
                    changes.append({
                        "host": host,
                        "type": "config",
                        "file": file_path,
                        "change_type": change_type,
                        "pre_hash": pre_hash,
                        "post_hash": post_hash
                    })
        
        # Analyze service changes
        pre_services = pre_state.get("services", {})
        post_services = post_state.get("services", {})
        
        for host in set(pre_services.keys()) | set(post_services.keys()):
            pre_host_services = set(pre_services.get(host, []))
            post_host_services = set(post_services.get(host, []))
            
            # Find service changes
            added_services = post_host_services - pre_host_services
            removed_services = pre_host_services - post_host_services
            
            for service in added_services:
                changes.append({
                    "host": host,
                    "type": "service",
                    "service": service,
                    "change_type": "started"
                })
            
            for service in removed_services:
                changes.append({
                    "host": host,
                    "type": "service", 
                    "service": service,
                    "change_type": "stopped"
                })
        
        return changes
    
    def _extract_changed_tasks(self, stdout: str) -> List[Dict[str, str]]:
        """Extract changed tasks from ansible output"""
        changed_tasks = []
        lines = stdout.split('\n')
        
        current_task = None
        current_host = None
        
        for line in lines:
            # Track current task
            if 'TASK [' in line:
                current_task = line.split('[')[1].split(']')[0]
            # Track current host
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                if ':' in line and not line.startswith('TASK') and not line.startswith('PLAY'):
                    current_host = line.split(':')[0]
            
            # Extract changed tasks
            if 'changed' in line.lower() and '=>' in line:
                changed_tasks.append({
                    "host": current_host or "unknown",
                    "task": current_task or "unknown",
                    "change": line.strip()
                })
        
        return changed_tasks
    
    def _analyze_idempotence(self, results: List[Dict[str, Any]], states: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze idempotence across all iterations"""
        issues = []
        
        # Check for failed iterations
        failed_iterations = [r for r in results if not r["success"]]
        if failed_iterations:
            issues.append({
                "type": "execution_failure",
                "description": f"Failed iterations: {[r['iteration'] for r in failed_iterations]}",
                "severity": "HIGH"
            })
        
        # Check for inconsistent changes across iterations
        if len(results) > 1:
            # Compare changes between iterations
            first_iteration_changes = set()
            for change in results[0]["changes"]:
                change_key = f"{change['host']}:{change['type']}:{change.get('file', change.get('service', ''))}"
                first_iteration_changes.add(change_key)
            
            for i, result in enumerate(results[1:], 1):
                iteration_changes = set()
                for change in result["changes"]:
                    change_key = f"{change['host']}:{change['type']}:{change.get('file', change.get('service', ''))}"
                    iteration_changes.add(change_key)
                
                if iteration_changes != first_iteration_changes:
                    issues.append({
                        "type": "inconsistent_changes",
                        "description": f"Iteration {i+1} changes differ from first iteration",
                        "severity": "HIGH",
                        "iteration": i+1,
                        "differences": list(iteration_changes.symmetric_difference(first_iteration_changes))
                    })
            
            # Check for changed tasks across iterations
            first_iteration_tasks = set()
            for task in results[0]["changed_tasks"]:
                task_key = f"{task['host']}:{task['task']}"
                first_iteration_tasks.add(task_key)
            
            for i, result in enumerate(results[1:], 1):
                iteration_tasks = set()
                for task in result["changed_tasks"]:
                    task_key = f"{task['host']}:{task['task']}"
                    iteration_tasks.add(task_key)
                
                if iteration_tasks != first_iteration_tasks:
                    issues.append({
                        "type": "inconsistent_tasks",
                        "description": f"Iteration {i+1} tasks differ from first iteration",
                        "severity": "MEDIUM",
                        "iteration": i+1,
                        "differences": list(iteration_tasks.symmetric_difference(first_iteration_tasks))
                    })
        
        # Calculate consistency score
        total_possible_issues = len(results) * 2  # max 2 issues per iteration
        consistency_score = max(0, 100 - (len(issues) * 10))
        
        # Generate recommendations
        recommendations = []
        if any(issue["type"] == "execution_failure" for issue in issues):
            recommendations.append("Fix playbook execution failures before testing idempotence")
        
        if any(issue["type"] == "inconsistent_changes" for issue in issues):
            recommendations.append("Review playbook for non-idempotent operations (e.g., commands without proper conditionals)")
        
        if any(issue["type"] == "inconsistent_tasks" for issue in issues):
            recommendations.append("Ensure tasks use proper when conditions and check modes")
        
        if not issues:
            recommendations.append("Playbook appears to be idempotent - consider adding to production pipeline")
        
        return {
            "idempotent": len(issues) == 0,
            "issues": issues,
            "consistency_score": consistency_score,
            "recommendations": recommendations
        }
    
    def detect_configuration_drift(self, playbook: str, baseline_snapshot: str, 
                               current_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Detect configuration drift from baseline"""
        print(f"🔍 Detecting configuration drift from baseline: {baseline_snapshot}")
        
        # Load baseline snapshot
        baseline_path = Path(baseline_snapshot)
        if not baseline_path.exists():
            return {
                "error": f"Baseline snapshot not found: {baseline_snapshot}",
                "drift_detected": False
            }
        
        try:
            with open(baseline_path) as f:
                baseline_state = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            return {
                "error": f"Failed to load baseline: {e}",
                "drift_detected": False
            }
        
        # Capture current state if not provided
        if current_state is None:
            current_state = self._capture_quick_state("drift_check")
        
        # Analyze drift
        drift_analysis = self._analyze_configuration_drift(baseline_state, current_state)
        
        return {
            "baseline": baseline_snapshot,
            "current_state": "captured" if current_state else "provided",
            "drift_detected": len(drift_analysis["drift_items"]) > 0,
            "drift_analysis": drift_analysis,
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_configuration_drift(self, baseline: Dict[str, Any], 
                                 current: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze configuration drift between baseline and current states"""
        drift_items = []
        
        # Analyze configuration drift
        baseline_configs = baseline.get("configs", {})
        current_configs = current.get("configs", {})
        
        for host in set(baseline_configs.keys()) | set(current_configs.keys()):
            baseline_host_configs = baseline_configs.get(host, {})
            current_host_configs = current_configs.get(host, {})
            
            # Find drifted configurations
            all_files = set(baseline_host_configs.keys()) | set(current_host_configs.keys())
            
            for file_path in all_files:
                baseline_hash = baseline_host_configs.get(file_path)
                current_hash = current_host_configs.get(file_path)
                
                if baseline_hash != current_hash:
                    if baseline_hash is None:
                        drift_type = "added"
                    elif current_hash is None:
                        drift_type = "removed"
                    else:
                        drift_type = "modified"
                    
                    drift_items.append({
                        "host": host,
                        "type": "config_drift",
                        "file": file_path,
                        "drift_type": drift_type,
                        "baseline_hash": baseline_hash,
                        "current_hash": current_hash,
                        "severity": "HIGH" if drift_type == "modified" else "MEDIUM"
                    })
        
        # Analyze service drift
        baseline_services = baseline.get("services", {})
        current_services = current.get("services", {})
        
        for host in set(baseline_services.keys()) | set(current_services.keys()):
            baseline_host_services = set(baseline_services.get(host, []))
            current_host_services = set(current_services.get(host, []))
            
            # Find service drift
            added_services = current_host_services - baseline_host_services
            removed_services = baseline_host_services - current_host_services
            
            for service in added_services:
                drift_items.append({
                    "host": host,
                    "type": "service_drift",
                    "service": service,
                    "drift_type": "started",
                    "severity": "MEDIUM"
                })
            
            for service in removed_services:
                drift_items.append({
                    "host": host,
                    "type": "service_drift",
                    "service": service,
                    "drift_type": "stopped",
                    "severity": "HIGH"
                })
        
        return {
            "drift_items": drift_items,
            "summary": {
                "total_drift_items": len(drift_items),
                "config_drift": len([d for d in drift_items if d["type"] == "config_drift"]),
                "service_drift": len([d for d in drift_items if d["type"] == "service_drift"]),
                "high_severity": len([d for d in drift_items if d["severity"] == "HIGH"]),
                "medium_severity": len([d for d in drift_items if d["severity"] == "MEDIUM"])
            }
        }

def main():
    parser = argparse.ArgumentParser(
        description="Idempotence Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i inventory/hosts site.yml                    # Test site.yml idempotence
  %(prog)s -i inventory/hosts deploy.yml --iterations 5   # Test with 5 iterations
  %(prog)s -i inventory/hosts --detect-drift baseline.json  # Detect drift from baseline
        """
    )
    
    parser.add_argument("-i", "--inventory", required=True, help="Inventory file")
    parser.add_argument("playbook", nargs="?", help="Playbook to test for idempotence")
    parser.add_argument("--iterations", type=int, default=3,
                       help="Number of iterations to run (default: 3)")
    parser.add_argument("--detect-drift", metavar="BASELINE_SNAPSHOT",
                       help="Detect configuration drift from baseline snapshot")
    parser.add_argument("--extra-vars", help="Extra variables (key=value format)")
    parser.add_argument("--output-dir", default="/tmp/idempotence_tests",
                       help="Output directory for test results")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    parser.add_argument("--verbose", action="store_true", help="Detailed output")
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = IdempotenceTester(args.inventory, args.output_dir)
    
    # Parse extra variables
    extra_vars = {}
    if args.extra_vars:
        for var_pair in args.extra_vars.split(','):
            if '=' in var_pair:
                key, value = var_pair.split('=', 1)
                extra_vars[key.strip()] = value.strip()
    
    try:
        if args.detect_drift:
            # Configuration drift detection
            drift_result = tester.detect_configuration_drift("", args.detect_drift)
            
            if not args.quiet:
                if drift_result.get("error"):
                    print(f"❌ Error: {drift_result['error']}")
                else:
                    print(f"Configuration Drift: {'DETECTED' if drift_result['drift_detected'] else 'NONE'}")
                    
                    if drift_result['drift_detected']:
                        drift_analysis = drift_result['drift_analysis']
                        print(f"\n📊 Drift Summary:")
                        print(f"  Total drift items: {drift_analysis['summary']['total_drift_items']}")
                        print(f"  Config drift: {drift_analysis['summary']['config_drift']}")
                        print(f"  Service drift: {drift_analysis['summary']['service_drift']}")
                        print(f"  High severity: {drift_analysis['summary']['high_severity']}")
                        
                        print(f"\n🔍 Drift Details:")
                        for item in drift_analysis['drift_items'][:10]:
                            print(f"  • {item['host']}: {item['type']} - {item.get('file', item.get('service', 'unknown'))}")
            
            sys.exit(1 if drift_result.get("error") or drift_result.get("drift_detected", False) else 0)
            
        elif args.playbook:
            # Idempotence testing
            report = tester.test_idempotence(args.playbook, args.iterations, extra_vars)
            
            if not args.quiet:
                print(f"\n📊 Idempotence Test Results:")
                print(f"  Playbook: {report['playbook']}")
                print(f"  Iterations: {report['iterations']}")
                print(f"  Idempotent: {'✓' if report['summary']['idempotent'] else '✗'}")
                print(f"  Consistency Score: {report['summary']['consistency_score']}/100")
                print(f"  Issues Found: {report['summary']['total_issues']}")
                
                if report['summary']['total_issues'] > 0:
                    print(f"\n⚠️  Issues:")
                    for issue in report['idempotence_analysis']['issues']:
                        print(f"  • {issue['type']}: {issue['description']}")
                
                print(f"\n💡 Recommendations:")
                for rec in report['summary']['recommendations']:
                    print(f"  • {rec}")
            
            sys.exit(0 if report['summary']['idempotent'] else 1)
            
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()