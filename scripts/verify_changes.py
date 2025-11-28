#!/usr/bin/env python3
"""
Change Verification Helper - Detects untracked debugging changes
Uses ansible-playbook --check --diff to find changes not captured in code
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any

def run_check_diff(playbook: str, inventory: str | None = None, extra_vars: Dict[str, str] | None = None, 
                  capture_state: bool = False) -> Dict[str, Any]:
    """Run ansible-playbook in check mode with diff to detect untracked changes"""
    cmd = ["ansible-playbook", "--check", "--diff", playbook]
    
    if inventory:
        cmd.extend(["-i", inventory])
    
    if extra_vars:
        extra_vars_str = ",".join([f"{k}={v}" for k, v in extra_vars.items()])
        cmd.extend(["--extra-vars", extra_vars_str])
    
    # Add state capture hook
    if capture_state:
        cmd.extend(["--extra-vars", "state_capture_enabled=true"])
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=300
        )
        
        # Enhanced diff analysis
        has_diffs = "-- diff" in result.stdout or "+-" in result.stdout
        state_changes = extract_state_changes(result.stdout) if has_diffs else []
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "has_diffs": has_diffs,
            "state_changes": state_changes,
            "change_summary": summarize_changes(result.stdout)
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command timed out after 5 minutes",
            "returncode": 124,
            "has_diffs": False,
            "state_changes": [],
            "change_summary": {}
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": 1,
            "has_diffs": False,
            "state_changes": [],
            "change_summary": {}
        }

def extract_state_changes(output: str) -> List[Dict[str, str]]:
    """Extract structured state changes from ansible output"""
    changes = []
    lines = output.split('\n')
    
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
        
        # Extract state changes
        if 'changed' in line.lower() and '=>' in line:
            changes.append({
                "host": current_host or "unknown",
                "task": current_task or "unknown",
                "change": line.strip(),
                "type": "state_change"
            })
        elif line.startswith('---') or line.startswith('+++'):
            changes.append({
                "host": current_host or "unknown",
                "task": current_task or "unknown",
                "change": line.strip(),
                "type": "file_diff"
            })
    
    return changes

def summarize_changes(output: str) -> Dict[str, Any]:
    """Summarize changes for quick analysis"""
    summary = {
        "total_changes": 0,
        "hosts_affected": set(),
        "tasks_changed": set(),
        "file_changes": 0,
        "service_changes": 0
    }
    
    lines = output.split('\n')
    current_host = None
    current_task = None
    
    for line in lines:
        if 'TASK [' in line:
            current_task = line.split('[')[1].split(']')[0]
        if line.strip() and not line.startswith(' ') and ':' in line:
            if not line.startswith('TASK') and not line.startswith('PLAY'):
                current_host = line.split(':')[0]
        
        if 'changed' in line.lower() and '=>' in line:
            summary["total_changes"] += 1
            if current_host:
                summary["hosts_affected"].add(current_host)
            if current_task:
                summary["tasks_changed"].add(current_task)
            
            # Categorize change type
            change_text = line.lower()
            if 'service' in change_text or 'systemctl' in change_text:
                summary["service_changes"] += 1
            elif 'file' in change_text or 'config' in change_text:
                summary["file_changes"] += 1
        elif line.startswith('---') or line.startswith('+++'):
            summary["file_changes"] += 1
    
    # Convert sets to counts
    summary["hosts_affected"] = len(summary["hosts_affected"])
    summary["tasks_changed"] = len(summary["tasks_changed"])
    
    return summary

def parse_diff_output(output: str) -> List[Dict[str, str]]:
    """Parse diff output to extract change summaries"""
    changes = []
    lines = output.split('\n')
    
    current_file = None
    for line in lines:
        if line.startswith('---') or line.startswith('+++'):
            current_file = line.split('\t')[0] if '\t' in line else line
        elif line.startswith('@@') and current_file:
            changes.append({
                "file": current_file,
                "change_type": "content_diff",
                "summary": line
            })
        elif 'changed' in line.lower() and '=>' in line:
            changes.append({
                "file": "unknown",
                "change_type": "state_change",
                "summary": line.strip()
            })
    
    return changes

def generate_verification_report(result: Dict[str, Any], playbook: str) -> Dict[str, Any]:
    """Generate enhanced verification report"""
    changes = parse_diff_output(result["stdout"]) if result["stdout"] else []
    state_changes = result.get("state_changes", [])
    change_summary = result.get("change_summary", {})
    
    return {
        "playbook": playbook,
        "verification_status": "passed" if result["success"] else "failed",
        "has_untracked_changes": result["has_diffs"],
        "changes_detected": len(changes),
        "state_changes_detected": len(state_changes),
        "change_summary": changes[:5],  # Limit to first 5 changes
        "state_change_details": state_changes[:10],  # Limit to first 10 state changes
        "impact_summary": change_summary,
        "recommendation": (
            "Review detected changes and update Ansible code" 
            if result["has_diffs"] else "No untracked changes detected"
        ),
        "severity": _assess_change_severity(change_summary)
    }

def _assess_change_severity(change_summary: Dict[str, Any]) -> str:
    """Assess severity of detected changes"""
    if change_summary.get("service_changes", 0) > 0:
        return "HIGH"  # Service changes are high impact
    elif change_summary.get("file_changes", 0) > 5:
        return "MEDIUM"  # Multiple file changes
    elif change_summary.get("hosts_affected", 0) > 3:
        return "MEDIUM"  # Changes across many hosts
    elif change_summary.get("total_changes", 0) > 0:
        return "LOW"  # Minor changes
    else:
        return "NONE"

def main():
    parser = argparse.ArgumentParser(
        description="Verify debugging changes are captured in Ansible code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s site.yml                           # Check site.yml for untracked changes
  %(prog)s deploy.yml -i inventory/hosts      # Check with specific inventory
  %(prog)s debug.yml --extra-vars env=dev     # Check with extra variables
  %(prog)s --report site.yml > changes.json   # Save detailed report
        """
    )
    
    parser.add_argument("playbook", help="Playbook to verify")
    parser.add_argument("-i", "--inventory", help="Inventory file")
    parser.add_argument("--extra-vars", help="Extra variables (key=value format)")
    parser.add_argument("--report", action="store_true", 
                       help="Output detailed JSON report")
    parser.add_argument("--quiet", action="store_true",
                       help="Minimal output, exit code only")
    parser.add_argument("--capture-state", action="store_true",
                       help="Enable enhanced state change capture")
    
    args = parser.parse_args()
    
    # Parse extra variables
    extra_vars = {}
    if args.extra_vars:
        for var_pair in args.extra_vars.split(','):
            if '=' in var_pair:
                key, value = var_pair.split('=', 1)
                extra_vars[key.strip()] = value.strip()
    
    # Verify playbook exists
    if not Path(args.playbook).exists():
        print(f"ERROR: Playbook '{args.playbook}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Run verification
    result = run_check_diff(args.playbook, args.inventory, extra_vars, args.capture_state)
    report = generate_verification_report(result, args.playbook)
    
    # Output results
    if args.report:
        print(json.dumps(report, indent=2))
    elif args.quiet:
        # Exit code 1 if untracked changes found
        sys.exit(1 if report["has_untracked_changes"] else 0)
    else:
        print(f"Verification: {report['verification_status'].upper()}")
        print(f"Untracked changes: {'YES' if report['has_untracked_changes'] else 'NO'}")
        print(f"Severity: {report.get('severity', 'UNKNOWN')}")
        
        if report["changes_detected"] > 0:
            print(f"\nDetected changes ({report['changes_detected']}):")
            for change in report["change_summary"]:
                print(f"  • {change['summary']}")
        
        if report.get("state_changes_detected", 0) > 0:
            print(f"\nState changes ({report['state_changes_detected']}):")
            for change in report.get("state_change_details", [])[:5]:
                print(f"  🔄 {change.get('host', 'unknown')}: {change.get('change', 'unknown')}")
        
        impact = report.get("impact_summary", {})
        if impact:
            print(f"\nImpact Summary:")
            print(f"  Hosts affected: {impact.get('hosts_affected', 0)}")
            print(f"  Tasks changed: {impact.get('tasks_changed', 0)}")
            print(f"  File changes: {impact.get('file_changes', 0)}")
            print(f"  Service changes: {impact.get('service_changes', 0)}")
        
        print(f"\nRecommendation: {report['recommendation']}")
        
        if not result["success"] and result["stderr"]:
            print(f"\nErrors: {result['stderr']}", file=sys.stderr)
    
    # Exit code reflects verification status
    sys.exit(0 if result["success"] and not report["has_untracked_changes"] else 1)

if __name__ == "__main__":
    main()