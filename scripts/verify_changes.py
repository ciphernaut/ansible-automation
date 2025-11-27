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

def run_check_diff(playbook: str, inventory: str | None = None, extra_vars: Dict[str, str] | None = None) -> Dict[str, Any]:
    """Run ansible-playbook in check mode with diff to detect untracked changes"""
    cmd = ["ansible-playbook", "--check", "--diff", playbook]
    
    if inventory:
        cmd.extend(["-i", inventory])
    
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
            "returncode": result.returncode,
            "has_diffs": "-- diff" in result.stdout or "+-" in result.stdout
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command timed out after 5 minutes",
            "returncode": 124,
            "has_diffs": False
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": 1,
            "has_diffs": False
        }

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
    """Generate concise verification report"""
    changes = parse_diff_output(result["stdout"]) if result["stdout"] else []
    
    return {
        "playbook": playbook,
        "verification_status": "passed" if result["success"] else "failed",
        "has_untracked_changes": result["has_diffs"],
        "changes_detected": len(changes),
        "change_summary": changes[:5],  # Limit to first 5 changes
        "recommendation": (
            "Review detected changes and update Ansible code" 
            if result["has_diffs"] else "No untracked changes detected"
        )
    }

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
    result = run_check_diff(args.playbook, args.inventory, extra_vars)
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
        
        if report["changes_detected"] > 0:
            print(f"\nDetected changes ({report['changes_detected']}):")
            for change in report["change_summary"]:
                print(f"  • {change['summary']}")
        
        print(f"\nRecommendation: {report['recommendation']}")
        
        if not result["success"] and result["stderr"]:
            print(f"\nErrors: {result['stderr']}", file=sys.stderr)
    
    # Exit code reflects verification status
    sys.exit(0 if result["success"] and not report["has_untracked_changes"] else 1)

if __name__ == "__main__":
    main()