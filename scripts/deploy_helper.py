#!/usr/bin/env python3
"""
Ansible Deploy Helper
Progressive deployment with staging and recovery capabilities
"""

import os
import sys
import json
import time
import subprocess
import yaml
import asyncio
import threading
import psutil
import platform
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_deployment_state(state_file="deployment_state.json"):
    """Load previous deployment state"""
    try:
        if Path(state_file).exists():
            with open(state_file) as f:
                return json.load(f)
        return {}
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_deployment_state(state, state_file="deployment_state.json"):
    """Save deployment state for recovery"""
    try:
        # Add timestamp to state
        state['last_updated'] = datetime.now().isoformat()
        
        # Create backup of previous state
        if Path(state_file).exists():
            backup_file = f"{state_file}.backup"
            Path(state_file).rename(backup_file)
        
        with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        return True
    except Exception as e:
        print(f"Warning: Could not save state: {e}")
        return False

def get_deployment_status(state_file="deployment_state.json"):
    """Get current deployment status"""
    state = load_deployment_state(state_file)
    
    if not state:
        return {
            'status': 'not_started',
            'stages': {},
            'summary': 'No deployment state found'
        }
    
    stages = state.get('stages', {})
    completed = sum(1 for s in stages.values() if s.get('status') == 'completed')
    failed = sum(1 for s in stages.values() if s.get('status') == 'failed')
    in_progress = sum(1 for s in stages.values() if s.get('status') == 'in_progress')
    total = len(stages)
    
    if completed == total and total > 0:
        status = 'completed'
    elif failed > 0:
        status = 'failed'
    elif in_progress > 0:
        status = 'in_progress'
    elif completed > 0:
        status = 'partial'
    else:
        status = 'not_started'
    
    return {
        'status': status,
        'stages': stages,
        'summary': f'{completed}/{total} stages completed, {failed} failed, {in_progress} in progress',
        'last_updated': state.get('last_updated'),
        'total_stages': total,
        'completed_stages': completed,
        'failed_stages': failed,
        'in_progress_stages': in_progress
    }

def reset_deployment_state(state_file="deployment_state.json"):
    """Reset deployment state"""
    try:
        if Path(state_file).exists():
            backup_file = f"{state_file}.reset_backup"
            Path(state_file).rename(backup_file)
            print(f"📦 State backed up to: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ Could not reset state: {e}")
        return False

def detect_hardware_profile():
    """Detect hardware profile for optimization"""
    try:
        # CPU info
        cpu_count = os.cpu_count()
        cpu_freq = psutil.cpu_freq()
        cpu_freq_mhz = cpu_freq.current if cpu_freq else 0
        
        # Memory info
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        
        # Disk info
        disk = psutil.disk_usage('/')
        disk_gb = disk.total / (1024**3)
        
        # Network interfaces
        interfaces = psutil.net_if_addrs()
        
        # System load
        load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        
        profile = {
            'cpu_count': cpu_count,
            'cpu_freq_mhz': cpu_freq_mhz,
            'memory_gb': round(memory_gb, 2),
            'disk_gb': round(disk_gb, 2),
            'load_avg': load_avg,
            'interfaces': list(interfaces.keys()),
            'platform': platform.system(),
            'architecture': platform.machine(),
            'python_version': platform.python_version()
        }
        
        # Determine profile type
        if (cpu_count and cpu_count >= 16) and (memory_gb and memory_gb >= 32):
            profile_type = 'high_performance'
        elif (cpu_count and cpu_count >= 8) and (memory_gb and memory_gb >= 16):
            profile_type = 'standard'
        elif (cpu_count and cpu_count >= 4) and (memory_gb and memory_gb >= 8):
            profile_type = 'minimal'
        else:
            profile_type = 'resource_constrained'
        
        profile['type'] = profile_type
        
        return profile
        
    except Exception as e:
        print(f"⚠️  Could not detect hardware profile: {e}")
        return {
            'type': 'unknown',
            'cpu_count': os.cpu_count() or 1,
            'memory_gb': 4.0,
            'platform': platform.system()
        }

def optimize_for_hardware(profile):
    """Get optimization settings based on hardware profile"""
    profile_type = profile.get('type', 'unknown')
    cpu_count = profile.get('cpu_count', 1)
    memory_gb = profile.get('memory_gb', 4)
    
    optimizations = {
        'ansible_forks': min(cpu_count, 10),  # Cap at 10 forks
        'timeout_multiplier': 1.0,
        'retry_count': 3,
        'async_enabled': False,
        'parallel_stages': 1
    }
    
    if profile_type == 'high_performance':
        optimizations.update({
            'ansible_forks': min(cpu_count, 20),
            'timeout_multiplier': 0.8,  # Faster timeouts
            'retry_count': 2,
            'async_enabled': True,
            'parallel_stages': 2
        })
    elif profile_type == 'standard':
        optimizations.update({
            'ansible_forks': min(cpu_count, 10),
            'timeout_multiplier': 1.0,
            'retry_count': 3,
            'async_enabled': True,
            'parallel_stages': 1
        })
    elif profile_type == 'minimal':
        optimizations.update({
            'ansible_forks': min(cpu_count, 5),
            'timeout_multiplier': 1.5,  # Longer timeouts
            'retry_count': 4,
            'async_enabled': False,
            'parallel_stages': 1
        })
    elif profile_type == 'resource_constrained':
        optimizations.update({
            'ansible_forks': 2,  # Very conservative
            'timeout_multiplier': 2.0,  # Much longer timeouts
            'retry_count': 5,
            'async_enabled': False,
            'parallel_stages': 1
        })
    
    return optimizations

def check_transient_locks(timeout=300, retries=3):
    """Check for transient locks that might cause deployment failures"""
    lock_files = [
        '/var/lib/dpkg/lock',
        '/var/lib/apt/lists/lock',
        '/var/cache/apt/archives.lock'
    ]
    
    for attempt in range(retries):
        locked = []
        for lock_file in lock_files:
            if Path(lock_file).exists():
                    locked.append(lock_file)
        
        if not locked:
            print(f"✅ No transient locks detected (attempt {attempt + 1})")
            return True
        else:
            print(f"⚠️  Transient locks detected: {locked}")
            print("  💡 Waiting 30 seconds for locks to clear...")
            time.sleep(30)
            return False
    
    print(f"❌ Persistent locks detected after {retries} attempts")
    return False

def run_ansible_async(playbook, inventory, timeout=300, callback=None):
    """Run ansible-playbook asynchronously with callback support"""
    def run_process():
        try:
            process = subprocess.Popen(
                ['ansible-playbook', '-i', inventory, '--timeout', str(timeout), playbook],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            output_lines = []
            error_lines = []
            
            # Read output in real-time
            while True:
                output = process.stdout.readline() if process.stdout else ''
                if output == '' and process.poll() is not None:
                    break
                if output:
                    output_lines.append(output.strip())
                    if callback:
                        callback('stdout', output.strip())
                
                error = process.stderr.readline() if process.stderr else ''
                if error:
                    error_lines.append(error.strip())
                    if callback:
                        callback('stderr', error.strip())
            
            return {
                'returncode': process.returncode,
                'stdout': '\n'.join(output_lines),
                'stderr': '\n'.join(error_lines),
                'success': process.returncode == 0
            }
        except Exception as e:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False,
                'exception': e
            }
    
    # Run in thread pool for async execution
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_process)
        return future

def run_ansible_with_retry(playbook, inventory, max_retries=3, base_timeout=300, scaling_factor=2, async_mode=False):
    """Run ansible-playbook with intelligent retry logic and async support"""
    def deployment_callback(stream_type, line):
        if stream_type == 'stdout':
            print(f"📤 {line}")
        else:
            print(f"⚠️  {line}")
    
    for attempt in range(max_retries):
        timeout = base_timeout * (scaling_factor ** attempt)
        
        print(f"🚀 Attempt {attempt + 1}/{max_retries}: Timeout={timeout}s")
        
        if async_mode:
            print("🔄 Running in async mode...")
            future = run_ansible_async(playbook, inventory, timeout, deployment_callback)
            
            try:
                result = future.result(timeout=timeout + 60)
                
                if result['success']:
                    print(f"✅ Deployment successful on attempt {attempt + 1}")
                    return True
                else:
                    print(f"❌ Deployment failed on attempt {attempt + 1}")
                    if result.get('stderr'):
                        print(f"Stderr: {result['stderr']}")
                    
                    # Check if failure is due to timeout
                    if result.get('stderr') and any(keyword in result['stderr'].lower() for keyword in ['timeout', 'timed out']):
                        print(f"⏱️  Timeout detected - increasing timeout for next attempt")
                        continue
                    
                    return False
                    
            except Exception as e:
                print(f"💥 Async execution error: {e}")
                return False
        else:
            # Synchronous execution
            try:
                result = subprocess.run(
                    ['ansible-playbook', '-i', inventory, '--timeout', str(timeout), playbook],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=timeout + 60  # Extra buffer for subprocess
                )
                
                if result.returncode == 0:
                    print(f"✅ Deployment successful on attempt {attempt + 1}")
                    return True
                else:
                    print(f"❌ Deployment failed on attempt {attempt + 1}")
                    print(f"Stdout: {result.stdout}")
                    if result.stderr:
                        print(f"Stderr: {result.stderr}")
                    
                    # Check if failure is due to timeout
                    if "timeout" in result.stderr.lower() or "timed out" in result.stderr.lower():
                        print(f"⏱️  Timeout detected - increasing timeout for next attempt")
                        continue
                    
                    return False
                    
            except subprocess.TimeoutExpired:
                print(f"⏱️  Ansible timeout after {timeout}s")
                continue
            except Exception as e:
                print(f"💥 Unexpected error: {e}")
                return False
    
    print(f"❌ All {max_retries} attempts failed")
    return False

def deploy_stage(stage_config, playbook, inventory, state, dry_run=False):
    """Deploy a specific stage with retry logic"""
    stage_name = stage_config.get('name', 'unknown')
    stage_timeout = stage_config.get('timeout', 300)
    max_retries = stage_config.get('retries', 3)
    async_mode = stage_config.get('async', False)
    
    print(f"\n🎯 Deploying Stage: {stage_name}")
    
    if dry_run:
        print(f"[DRY RUN] Would deploy stage '{stage_name}'")
        print(f"  📋 Playbook: {playbook}")
        print(f"  ⏱️  Timeout: {stage_timeout}s")
        print(f"  🔄 Async: {async_mode}")
        return True
    
    # Pre-stage checks
    if stage_config.get('check_locks', True):
        if not check_transient_locks(timeout=stage_timeout, retries=2):
            print("❌ Cannot proceed - transient locks detected")
            return False
    
    # Run stage-specific pre-deployment commands
    pre_commands = stage_config.get('pre_commands', [])
    for cmd in pre_commands:
        print(f"🔧 Running pre-command: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True)
        if result.returncode != 0:
            print(f"❌ Pre-command failed: {cmd}")
            return False
    
    success = run_ansible_with_retry(
        playbook=playbook,
        inventory=inventory,
        max_retries=max_retries,
        base_timeout=stage_timeout,
        async_mode=async_mode
    )
    
    if success:
        # Update state
        state['stages'][stage_name] = {
            'status': 'completed',
            'completed_at': datetime.now().isoformat(),
            'duration': stage_config.get('estimated_duration', 60),
            'async': async_mode
        }
        save_deployment_state(state)
        print(f"✅ Stage '{stage_name}' completed successfully")
    else:
        print(f"💥 Deployment failed at stage '{stage_name}'")
        print("  💡 Use --resume to continue from this stage")
        return False

def progressive_deployment(config_file, inventory_file, state_file="deployment_state.json", dry_run=False):
    """Execute progressive deployment stages"""
    if dry_run:
        print(f"[DRY RUN] Would execute progressive deployment")
        print(f"  📋 Config: {config_file}")
        print(f"  📂 Inventory: {inventory_file}")
        print(f"  🗃️ State file: {state_file}")
        
        # Show detailed dry-run of stages
        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)
            
            stages = config.get('stages', [])
            print(f"\n📋 Deployment Stages ({len(stages)}):")
            for i, stage in enumerate(stages, 1):
                stage_name = stage.get('name', f'stage_{i}')
                print(f"  {i}. {stage_name}")
                print(f"     📄 Playbook: {stage.get('playbook', 'N/A')}")
                print(f"     ⏱️  Timeout: {stage.get('timeout', 300)}s")
                print(f"     🔄 Async: {stage.get('async', False)}")
                print(f"     🔁 Retries: {stage.get('retries', 3)}")
        except Exception as e:
            print(f"  ⚠️  Could not parse config: {e}")
        
        return True
    
    # Load configuration and state
    try:
        with open(config_file) as f:
                config = yaml.safe_load(f)
        
        state = load_deployment_state(state_file)
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False
    
    stages = config.get('stages', [])
    total_stages = len(stages)
    
    # Detect hardware and optimize
    hardware_profile = detect_hardware_profile()
    optimizations = optimize_for_hardware(hardware_profile)
    
    print(f"🎯 Starting Progressive Deployment ({total_stages} stages)")
    print(f"💻 Hardware Profile: {hardware_profile['type']}")
    print(f"⚡ Optimizations: {optimizations['ansible_forks']} forks, {optimizations['timeout_multiplier']}x timeout")
    
    for i, stage_config in enumerate(stages, 1):
        stage_name = stage_config.get('name', f'stage_{i}')
        
        print(f"\n{'='*60}")
        
        # Check if stage should be skipped
        if state.get('stages', {}).get(stage_name, {}).get('status') == 'completed':
            print(f"⏭️  Skipping stage '{stage_name}' - already completed")
            continue
        
        # Apply optimizations to stage
        stage_config = stage_config.copy()
        stage_config.setdefault('timeout', 300)
        stage_config['timeout'] = int(stage_config['timeout'] * optimizations['timeout_multiplier'])
        stage_config.setdefault('retries', optimizations['retry_count'])
        stage_config.setdefault('async', optimizations['async_enabled'])
        
        # Deploy stage
        success = deploy_stage(stage_config, stage_config.get('playbook'), inventory_file, state, dry_run)
        
        if not success:
            print(f"💥 Deployment failed at stage '{stage_name}'")
            print("  💡 Use --resume to continue from this stage")
            return False
    
    print(f"\n{'='*60}")
    print(f"🎉 Progressive deployment completed!")
    
    # Final state summary
    final_state = load_deployment_state()
    completed_stages = [name for name, info in final_state.get('stages', {}).items() 
                        if info.get('status') == 'completed']
    
    print(f"\n📊 Deployment Summary:")
    print(f"  ✅ Completed stages: {', '.join(completed_stages)}")
    print(f"  📊 Total stages: {total_stages}")
    print(f"  📈 Success rate: {len(completed_stages)/total_stages*100:.1f}%")
    
    return len(completed_stages) == total_stages

def resume_deployment(config_file, inventory_file, state_file="deployment_state.json", dry_run=False):
    """Resume deployment from last failed stage"""
    if dry_run:
        print(f"[DRY RUN] Would resume deployment")
        
        # Show what would be resumed
        state = load_deployment_state(state_file)
        last_incomplete = None
        
        for stage_name, stage_info in state.get('stages', {}).items():
            if stage_info.get('status') == 'failed':
                last_incomplete = stage_name
                break
        
        if last_incomplete:
            print(f"  🔄 Would resume from stage: {last_incomplete}")
        else:
            print(f"  ℹ️  No failed stage found to resume from")
        
        return True
    
    # Load state and find last incomplete stage
    state = load_deployment_state(state_file)
    last_incomplete = None
    
    for stage_name, stage_info in state.get('stages', {}).items():
        if stage_info.get('status') == 'failed':
            last_incomplete = stage_name
            break
    
    if not last_incomplete:
        print("❌ No failed stage found to resume from")
        return False
    
    print(f"🔄 Resuming from stage: {last_incomplete}")
    
    # Mark stage as in-progress
    state['stages'][last_incomplete]['status'] = 'in_progress'
    state['stages'][last_incomplete]['resumed_at'] = datetime.now().isoformat()
    save_deployment_state(state)
    
    # Find stage config
    try:
        with open(config_file) as f:
                config = yaml.safe_load(f)
        
        stages = config.get('stages', [])
        stage_config = next((s for s in stages if s.get('name') == last_incomplete), None)
        
        if not stage_config:
            print(f"❌ Stage '{last_incomplete}' not found in configuration")
            return False
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False
    
    # Deploy the resumed stage
    success = deploy_stage(stage_config, stage_config.get('playbook'), inventory_file, state, dry_run)
    
    if success:
        print(f"✅ Successfully resumed and completed stage '{last_incomplete}'")
        return True
    else:
        print(f"❌ Failed to resume stage '{last_incomplete}'")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Progressive deployment with staging and recovery')
    parser.add_argument('config', help='Deployment configuration file')
    parser.add_argument('inventory', help='Ansible inventory file')
    parser.add_argument('--state-file', default='deployment_state.json', help='State tracking file (default: deployment_state.json)')
    parser.add_argument('--resume', action='store_true', help='Resume from last failed stage')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--verbose', action='store_true', help='Show detailed deployment information')
    parser.add_argument('--status', action='store_true', help='Show deployment status')
    parser.add_argument('--reset', action='store_true', help='Reset deployment state')
    
    args = parser.parse_args()
    
    if args.status:
        status = get_deployment_status(args.state_file)
        print(f"📊 Deployment Status: {status['status']}")
        print(f"📝 {status['summary']}")
        if status.get('last_updated'):
            print(f"🕐 Last updated: {status['last_updated']}")
        
        if status['stages']:
            print(f"\n🎯 Stage Details:")
            for stage_name, stage_info in status['stages'].items():
                stage_status = stage_info.get('status', 'unknown')
                icon = {'completed': '✅', 'failed': '❌', 'in_progress': '🔄'}.get(stage_status, '⏸️')
                print(f"  {icon} {stage_name}: {stage_status}")
        
        sys.exit(0)
    
    if args.reset:
        success = reset_deployment_state(args.state_file)
        sys.exit(0 if success else 1)
    
    if args.resume:
        success = resume_deployment(args.config, args.inventory, args.state_file, args.dry_run)
    else:
        success = progressive_deployment(args.config, args.inventory, args.state_file, args.dry_run)
    
    sys.exit(0 if success else 1)