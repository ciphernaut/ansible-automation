#!/usr/bin/env python3
"""
Context Preservation Module
Maintains Ansible best practices and prevents context attrition
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

class ContextPreserver:
    """Preserves and maintains Ansible context across sessions"""
    
    def __init__(self, context_dir: str = "/tmp/ansible_context"):
        self.context_dir = Path(context_dir)
        self.context_dir.mkdir(exist_ok=True)
        self.context_file = self.context_dir / "ansible_context.json"
        self.session_file = self.context_dir / "current_session.json"
        
    def save_context(self, context_data: Dict[str, Any]) -> bool:
        """Save current Ansible context"""
        try:
            context = {
                "timestamp": datetime.now().isoformat(),
                "session_id": self._get_session_id(),
                "ansible_patterns": context_data.get("ansible_patterns", []),
                "best_practices": context_data.get("best_practices", []),
                "common_modules": context_data.get("common_modules", []),
                "anti_patterns": context_data.get("anti_patterns", []),
                "inventory_structure": context_data.get("inventory_structure", {}),
                "recent_operations": context_data.get("recent_operations", [])
            }
            
            with open(self.context_file, 'w') as f:
                json.dump(context, f, indent=2)
            
            # Update current session
            self._update_session(context_data)
            return True
        except Exception as e:
            print(f"Failed to save context: {e}")
            return False
    
    def load_context(self) -> Dict[str, Any]:
        """Load preserved Ansible context"""
        try:
            if self.context_file.exists():
                with open(self.context_file) as f:
                    context = json.load(f)
                
                # Check if context is recent (within 24 hours)
                timestamp = datetime.fromisoformat(context["timestamp"])
                if datetime.now() - timestamp < timedelta(hours=24):
                    return context
        except Exception as e:
            print(f"Failed to load context: {e}")
        
        return self._get_default_context()
    
    def add_operation(self, operation_type: str, details: Dict[str, Any]) -> None:
        """Add operation to context history"""
        context = self.load_context()
        
        operation = {
            "type": operation_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        context["recent_operations"].append(operation)
        
        # Keep only last 20 operations
        context["recent_operations"] = context["recent_operations"][-20:]
        
        self.save_context(context)
    
    def get_ansible_reminders(self) -> List[str]:
        """Get reminders about Ansible best practices"""
        context = self.load_context()
        reminders = []
        
        # Check for common anti-patterns in recent operations
        recent_ops = context.get("recent_operations", [])
        for op in recent_ops[-5:]:  # Last 5 operations
            if "shell" in str(op.get("details", {})).lower():
                reminders.append("📋 Consider using specific Ansible modules instead of shell commands")
            
            if "ssh" in str(op.get("details", {})).lower():
                reminders.append("📋 Use Ansible inventory instead of direct SSH")
            
            if "systemctl" in str(op.get("details", {})).lower():
                reminders.append("📋 Use systemd or service modules for service management")
        
        # Add general reminders
        reminders.extend([
            "🔍 Always use --check --diff before applying changes",
            "📋 Use proper module names instead of generic shell commands",
            "🏷️  Tag tasks for better organization and selective execution",
            "📊 Use ansible_facts for dynamic configuration"
        ])
        
        return list(set(reminders))  # Remove duplicates
    
    def _get_session_id(self) -> str:
        """Generate or retrieve session ID"""
        if self.session_file.exists():
            try:
                with open(self.session_file) as f:
                    session = json.load(f)
                    # Check if session is recent (within 2 hours)
                    timestamp = datetime.fromisoformat(session["timestamp"])
                    if datetime.now() - timestamp < timedelta(hours=2):
                        return session["id"]
            except:
                pass
        
        # Generate new session ID
        session_id = f"ansible_session_{int(time.time())}"
        session_data = {
            "id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return session_id
    
    def _update_session(self, context_data: Dict[str, Any]) -> None:
        """Update current session with context data"""
        session_data = {
            "id": self._get_session_id(),
            "timestamp": datetime.now().isoformat(),
            "last_operation": context_data.get("last_operation"),
            "ansible_patterns_used": context_data.get("ansible_patterns", [])
        }
        
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
    
    def _get_default_context(self) -> Dict[str, Any]:
        """Get default Ansible context"""
        return {
            "timestamp": datetime.now().isoformat(),
            "session_id": self._get_session_id(),
            "ansible_patterns": [
                "Use --check --diff for safe previews",
                "Prefer specific modules over shell commands",
                "Use proper inventory management",
                "Implement idempotence in all tasks"
            ],
            "best_practices": [
                "Always test with --check mode first",
                "Use tags for task organization",
                "Implement proper error handling",
                "Use ansible_facts for dynamic configuration"
            ],
            "common_modules": [
                "apt, yum, dnf for package management",
                "systemd, service for service management", 
                "template, copy for file management",
                "user, group for user management"
            ],
            "anti_patterns": [
                "Direct SSH commands",
                "Manual file editing without state",
                "Shell commands when specific modules exist",
                "Missing inventory consideration"
            ],
            "inventory_structure": {},
            "recent_operations": []
        }

# Global context preserver instance
_context_preserver = None

def get_context_preserver() -> ContextPreserver:
    """Get global context preserver instance"""
    global _context_preserver
    if _context_preserver is None:
        _context_preserver = ContextPreserver()
    return _context_preserver

def preserve_ansible_context(operation_type: str, details: Dict[str, Any]) -> None:
    """Quick function to preserve Ansible context"""
    preserver = get_context_preserver()
    preserver.add_operation(operation_type, details)

def get_ansible_reminders() -> List[str]:
    """Quick function to get Ansible reminders"""
    preserver = get_context_preserver()
    return preserver.get_ansible_reminders()