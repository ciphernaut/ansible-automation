#!/usr/bin/env python3
"""
State Reconciliation Testing Framework
Enhanced state comparison and multi-node consistency validation
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

class StateReconciliationTester:
    def __init__(self, inventory: str, output_dir: str = "/tmp/state_reconciliation"):
        self.inventory = inventory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def capture_state_snapshot(self, snapshot_name: str) -> str:
        """Capture comprehensive state snapshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_dir = self.output_dir / f"{snapshot_name}_{timestamp}"
        snapshot_dir.mkdir(exist_ok=True)
        
        print(f"📸 Capturing state snapshot: {snapshot_name}")
        
        # Capture system facts
        facts_dir = snapshot_dir / "facts"
        facts_dir.mkdir(exist_ok=True)
        try:
            subprocess.run([
                "ansible", "all", "-i", self.inventory, "-m", "setup", 
                "--tree", str(facts_dir)
            ], check=True, capture_output=True)
            print(f"  ✓ System facts captured")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed to capture facts: {e}")
            
        # Capture configuration file hashes
        configs_dir = snapshot_dir / "configs"
        configs_dir.mkdir(exist_ok=True)
        try:
            result = subprocess.run([
                "ansible", "all", "-i", self.inventory, "-m", "shell",
                "-a", "find /etc -name '*.conf' -type f -exec md5sum {} \\; 2>/dev/null || true"
            ], capture_output=True, text=True, check=True)
            
            # Save config hashes per host
            self._save_config_hashes(result.stdout, configs_dir)
            print(f"  ✓ Configuration hashes captured")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed to capture configs: {e}")
            
        # Capture running services
        services_dir = snapshot_dir / "services"
        services_dir.mkdir(exist_ok=True)
        try:
            result = subprocess.run([
                "ansible", "all", "-i", self.inventory, "-m", "shell",
                "-a", "systemctl list-units --type=service --state=running --no-pager"
            ], capture_output=True, text=True, check=True)
            
            # Save service status per host
            self._save_service_status(result.stdout, services_dir)
            print(f"  ✓ Service status captured")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Failed to capture services: {e}")
            
        return str(snapshot_dir)
    
    def _save_config_hashes(self, hash_output: str, configs_dir: Path):
        """Parse and save configuration file hashes"""
        current_host = None
        host_hashes = {}
        
        for line in hash_output.split('\n'):
            if line.strip():
                # Ansible output format: hostname | SUCCESS | rc=0 >>
                if ' | SUCCESS | ' in line:
                    current_host = line.split(' | ')[0]
                    host_hashes[current_host] = []
                elif current_host and line.strip():
                    # Parse md5sum output: hash  filename
                    parts = line.strip().split('  ', 1)
                    if len(parts) == 2:
                        host_hashes[current_host].append({
                            'hash': parts[0],
                            'file': parts[1]
                        })
        
        # Save per host
        for host, hashes in host_hashes.items():
            (configs_dir / f"{host}_configs.json").write_text(json.dumps(hashes, indent=2))
    
    def _save_service_status(self, service_output: str, services_dir: Path):
        """Parse and save service status"""
        current_host = None
        host_services = {}
        
        for line in service_output.split('\n'):
            if line.strip():
                if ' | SUCCESS | ' in line:
                    current_host = line.split(' | ')[0]
                    host_services[current_host] = []
                elif current_host and line.strip():
                    # Parse service line: service.service   loaded active running   description
                    if '.service' in line and 'running' in line:
                        service_name = line.split()[0]
                        host_services[current_host].append(service_name)
        
        # Save per host
        for host, services in host_services.items():
            (services_dir / f"{host}_services.json").write_text(json.dumps(services, indent=2))
    
    def compare_snapshots(self, before_dir: str, after_dir: str) -> Dict[str, Any]:
        """Compare two state snapshots"""
        print(f"🔍 Comparing snapshots: {Path(before_dir).name} vs {Path(after_dir).name}")
        
        differences = {
            "facts": {},
            "configs": {},
            "services": {},
            "summary": {"total_changes": 0}
        }
        
        # Compare facts
        facts_diff = self._compare_facts(
            Path(before_dir) / "facts", 
            Path(after_dir) / "facts"
        )
        differences["facts"] = facts_diff
        
        # Compare configurations
        configs_diff = self._compare_configs(
            Path(before_dir) / "configs", 
            Path(after_dir) / "configs"
        )
        differences["configs"] = configs_diff
        
        # Compare services
        services_diff = self._compare_services(
            Path(before_dir) / "services", 
            Path(after_dir) / "services"
        )
        differences["services"] = services_diff
        
        # Calculate summary
        total_changes = (
            len(facts_diff.get("changes", [])) +
            len(configs_diff.get("changes", [])) +
            len(services_diff.get("changes", []))
        )
        differences["summary"]["total_changes"] = total_changes
        
        return differences
    
    def _compare_facts(self, before_dir: Path, after_dir: Path) -> Dict[str, Any]:
        """Compare system facts between snapshots"""
        changes = []
        
        if not before_dir.exists() or not after_dir.exists():
            return {"changes": changes, "error": "Missing fact directories"}
        
        # Get all fact files
        before_files = list(before_dir.glob("*.json"))
        after_files = list(after_dir.glob("*.json"))
        
        for before_file in before_files:
            host = before_file.stem
            after_file = after_dir / f"{host}.json"
            
            if after_file.exists():
                try:
                    before_facts = json.loads(before_file.read_text())
                    after_facts = json.loads(after_file.read_text())
                    
                    # Compare key facts
                    key_fields = [
                        'ansible_distribution', 'ansible_kernel', 
                        'ansible_memtotal_mb', 'ansible_processor_cores'
                    ]
                    
                    for field in key_fields:
                        if field in before_facts.get('ansible_facts', {}) and \
                           field in after_facts.get('ansible_facts', {}):
                            before_val = before_facts['ansible_facts'][field]
                            after_val = after_facts['ansible_facts'][field]
                            
                            if before_val != after_val:
                                changes.append({
                                    "host": host,
                                    "field": field,
                                    "before": before_val,
                                    "after": after_val
                                })
                except (json.JSONDecodeError, KeyError) as e:
                    changes.append({
                        "host": host,
                        "error": f"Failed to parse facts: {e}"
                    })
        
        return {"changes": changes}
    
    def _compare_configs(self, before_dir: Path, after_dir: Path) -> Dict[str, Any]:
        """Compare configuration file hashes"""
        changes = []
        
        if not before_dir.exists() or not after_dir.exists():
            return {"changes": changes, "error": "Missing config directories"}
        
        # Get all config files
        before_files = list(before_dir.glob("*_configs.json"))
        after_files = list(after_dir.glob("*_configs.json"))
        
        for before_file in before_files:
            host = before_file.stem.replace("_configs", "")
            after_file = after_dir / f"{host}_configs.json"
            
            if after_file.exists():
                try:
                    before_configs = json.loads(before_file.read_text())
                    after_configs = json.loads(after_file.read_text())
                    
                    # Create hash lookup
                    before_hashes = {c['file']: c['hash'] for c in before_configs}
                    after_hashes = {c['file']: c['hash'] for c in after_configs}
                    
                    # Find changed files
                    all_files = set(before_hashes.keys()) | set(after_hashes.keys())
                    
                    for file_path in all_files:
                        before_hash = before_hashes.get(file_path)
                        after_hash = after_hashes.get(file_path)
                        
                        if before_hash != after_hash:
                            if before_hash is None:
                                change_type = "added"
                            elif after_hash is None:
                                change_type = "removed"
                            else:
                                change_type = "modified"
                            
                            changes.append({
                                "host": host,
                                "file": file_path,
                                "type": change_type,
                                "before_hash": before_hash,
                                "after_hash": after_hash
                            })
                except (json.JSONDecodeError, KeyError) as e:
                    changes.append({
                        "host": host,
                        "error": f"Failed to parse configs: {e}"
                    })
        
        return {"changes": changes}
    
    def _compare_services(self, before_dir: Path, after_dir: Path) -> Dict[str, Any]:
        """Compare running services"""
        changes = []
        
        if not before_dir.exists() or not after_dir.exists():
            return {"changes": changes, "error": "Missing service directories"}
        
        # Get all service files
        before_files = list(before_dir.glob("*_services.json"))
        after_files = list(after_dir.glob("*_services.json"))
        
        for before_file in before_files:
            host = before_file.stem.replace("_services", "")
            after_file = after_dir / f"{host}_services.json"
            
            if after_file.exists():
                try:
                    before_services = set(json.loads(before_file.read_text()))
                    after_services = set(json.loads(after_file.read_text()))
                    
                    # Find service changes
                    added_services = after_services - before_services
                    removed_services = before_services - after_services
                    
                    for service in added_services:
                        changes.append({
                            "host": host,
                            "service": service,
                            "type": "started"
                        })
                    
                    for service in removed_services:
                        changes.append({
                            "host": host,
                            "service": service,
                            "type": "stopped"
                        })
                        
                except (json.JSONDecodeError, KeyError) as e:
                    changes.append({
                        "host": host,
                        "error": f"Failed to parse services: {e}"
                    })
        
        return {"changes": changes}
    
    def check_multi_node_consistency(self, snapshot_dir: str) -> Dict[str, Any]:
        """Check state consistency across all nodes in inventory"""
        print(f"🔄 Checking multi-node consistency")
        
        consistency_report = {
            "consistent": True,
            "issues": [],
            "summary": {}
        }
        
        # Load facts for consistency check
        facts_dir = Path(snapshot_dir) / "facts"
        if not facts_dir.exists():
            consistency_report["issues"].append("No facts directory found")
            consistency_report["consistent"] = False
            return consistency_report
        
        # Collect all host facts
        all_facts = {}
        for fact_file in facts_dir.glob("*.json"):
            try:
                facts = json.loads(fact_file.read_text())
                all_facts[fact_file.stem] = facts.get('ansible_facts', {})
            except (json.JSONDecodeError, KeyError):
                continue
        
        if len(all_facts) < 2:
            consistency_report["issues"].append("Need at least 2 hosts for consistency check")
            return consistency_report
        
        # Check for inconsistencies in key fields
        key_fields = [
            'ansible_distribution', 'ansible_distribution_version',
            'ansible_kernel', 'ansible_python_version'
        ]
        
        for field in key_fields:
            values = {}
            for host, facts in all_facts.items():
                if field in facts:
                    value = facts[field]
                    if value not in values:
                        values[value] = []
                    values[value].append(host)
            
            if len(values) > 1:
                consistency_report["consistent"] = False
                consistency_report["issues"].append({
                    "field": field,
                    "inconsistent_values": values
                })
        
        # Check service consistency
        services_dir = Path(snapshot_dir) / "services"
        if services_dir.exists():
            all_services = {}
            for service_file in services_dir.glob("*_services.json"):
                try:
                    services = set(json.loads(service_file.read_text()))
                    host = service_file.stem.replace("_services", "")
                    all_services[host] = services
                except (json.JSONDecodeError, KeyError):
                    continue
            
            if len(all_services) > 1:
                # Find services that should be consistent across all nodes
                common_services = None
                for host, services in all_services.items():
                    if common_services is None:
                        common_services = services
                    else:
                        common_services &= services
                
                # Check for missing common services
                for host, services in all_services.items():
                    missing_services = common_services - services
                    if missing_services:
                        consistency_report["issues"].append({
                            "type": "missing_services",
                            "host": host,
                            "missing_services": list(missing_services)
                        })
                        consistency_report["consistent"] = False
        
        consistency_report["summary"] = {
            "hosts_checked": len(all_facts),
            "issues_found": len(consistency_report["issues"])
        }
        
        return consistency_report
    
    def run_reconciliation_test(self, playbook: str, extra_vars: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Run complete reconciliation test"""
        print(f"🚀 Starting reconciliation test for: {playbook}")
        
        # Capture pre-execution state
        pre_snapshot = self.capture_state_snapshot("pre_execution")
        
        # Run playbook
        print(f"🎯 Executing playbook: {playbook}")
        cmd = ["ansible-playbook", "-i", self.inventory, playbook]
        if extra_vars:
            extra_vars_str = ",".join([f"{k}={v}" for k, v in extra_vars.items()])
            cmd.extend(["--extra-vars", extra_vars_str])
        
        try:
            playbook_result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            playbook_success = True
            print(f"  ✓ Playbook executed successfully")
        except subprocess.CalledProcessError as e:
            playbook_success = False
            print(f"  ✗ Playbook failed: {e}")
            playbook_result = e
        
        # Capture post-execution state
        post_snapshot = self.capture_state_snapshot("post_execution")
        
        # Compare snapshots
        differences = self.compare_snapshots(pre_snapshot, post_snapshot)
        
        # Check multi-node consistency
        post_consistency = self.check_multi_node_consistency(post_snapshot)
        
        # Generate report
        report = {
            "playbook": playbook,
            "inventory": self.inventory,
            "pre_snapshot": pre_snapshot,
            "post_snapshot": post_snapshot,
            "playbook_success": playbook_success,
            "playbook_returncode": playbook_result.returncode if hasattr(playbook_result, 'returncode') else 1,
            "state_differences": differences,
            "consistency_check": post_consistency,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_changes": differences["summary"]["total_changes"],
                "consistent": post_consistency["consistent"],
                "overall_success": playbook_success and post_consistency["consistent"]
            }
        }
        
        # Save report
        report_file = self.output_dir / f"reconciliation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.write_text(json.dumps(report, indent=2))
        print(f"📄 Report saved: {report_file}")
        
        return report

def main():
    parser = argparse.ArgumentParser(
        description="State Reconciliation Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i inventory/hosts site.yml                    # Test site.yml
  %(prog)s -i inventory/hosts deploy.yml --compare-only    # Compare existing snapshots
  %(prog)s -i inventory/hosts --check-consistency snapshot_20241201_120000  # Check consistency
        """
    )
    
    parser.add_argument("-i", "--inventory", required=True, help="Inventory file")
    parser.add_argument("playbook", nargs="?", help="Playbook to test")
    parser.add_argument("--compare-only", nargs=2, metavar=("BEFORE", "AFTER"),
                       help="Compare two existing snapshots")
    parser.add_argument("--check-consistency", metavar="SNAPSHOT_DIR",
                       help="Check multi-node consistency in snapshot")
    parser.add_argument("--output-dir", default="/tmp/state_reconciliation",
                       help="Output directory for snapshots and reports")
    parser.add_argument("--extra-vars", help="Extra variables (key=value format)")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = StateReconciliationTester(args.inventory, args.output_dir)
    
    # Parse extra variables
    extra_vars = {}
    if args.extra_vars:
        for var_pair in args.extra_vars.split(','):
            if '=' in var_pair:
                key, value = var_pair.split('=', 1)
                extra_vars[key.strip()] = value.strip()
    
    try:
        if args.compare_only:
            # Compare existing snapshots
            differences = tester.compare_snapshots(args.compare_only[0], args.compare_only[1])
            if not args.quiet:
                print(f"Total changes: {differences['summary']['total_changes']}")
                if differences['summary']['total_changes'] > 0:
                    print("Changes detected:")
                    for category, data in differences.items():
                        if category != 'summary' and data.get('changes'):
                            print(f"  {category}: {len(data['changes'])} changes")
            sys.exit(0 if differences['summary']['total_changes'] == 0 else 1)
            
        elif args.check_consistency:
            # Check consistency of existing snapshot
            consistency = tester.check_multi_node_consistency(args.check_consistency)
            if not args.quiet:
                print(f"Consistency: {'PASS' if consistency['consistent'] else 'FAIL'}")
                if consistency['issues']:
                    print("Issues found:")
                    for issue in consistency['issues']:
                        print(f"  • {issue}")
            sys.exit(0 if consistency['consistent'] else 1)
            
        elif args.playbook:
            # Run full reconciliation test
            report = tester.run_reconciliation_test(args.playbook, extra_vars)
            
            if not args.quiet:
                print(f"\n📊 Reconciliation Test Results:")
                print(f"  Playbook Success: {'✓' if report['playbook_success'] else '✗'}")
                print(f"  State Changes: {report['summary']['total_changes']}")
                print(f"  Consistency: {'✓' if report['consistency_check']['consistent'] else '✗'}")
                print(f"  Overall: {'✓' if report['summary']['overall_success'] else '✗'}")
                
                if report['summary']['total_changes'] > 0:
                    print(f"\n📋 State Changes:")
                    for category, data in report['state_differences'].items():
                        if category != 'summary' and data.get('changes'):
                            print(f"  {category}: {len(data['changes'])} changes")
            
            sys.exit(0 if report['summary']['overall_success'] else 1)
            
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