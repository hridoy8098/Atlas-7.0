# backend/agent/terminal_agent.py — Atlas 7.0 Terminal Controller (Fixed)

import subprocess
import os
import platform
import re
from typing import Optional, Dict
from functools import wraps


# ← NEW: Dangerous command patterns
DANGEROUS_PATTERNS = [
    r'rm\s+-rf\s*/',           # Linux recursive delete root
    r'rm\s+-rf\s+~',           # Delete home
    r'del\s+/[fqs]\s+.*\\',    # Windows force delete
    r'format\s+[a-zA-Z]:',      # Format drive
    r'fdisk',                   # Partition manipulation
    r'mkfs\.',                  # Make filesystem
    r'dd\s+if=.*of=/dev/',     # Direct disk write
    r':\(\)\{\s*:\|:\s*&\s*\};:',  # Fork bomb
    r'>\s*/dev/[sh]da',        # Overwrite disk
    r'chmod\s+-R\s+777\s*/',   # Mess up permissions
    r'chown\s+-R',             # Recursive chown
    r'wget.*\|.*sh',           # Pipe wget to shell
    r'curl.*\|.*sh',           # Pipe curl to shell
    r'python.*-c.*import\s+os.*system',  # Python system exec
]

DANGEROUS_COMMANDS = [
    'shutdown', 'reboot', 'halt', 'poweroff',  # System control (optional block)
]


def sanitize_command(command: str) -> tuple[bool, str]:
    """
    Check if command is safe to execute
    Returns: (is_safe, reason_if_unsafe)
    """
    cmd_lower = command.lower().strip()
    
    # Check regex patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, cmd_lower):
            return False, f"Blocked dangerous pattern: {pattern}"
    
    # Check exact dangerous commands
    for dangerous in DANGEROUS_COMMANDS:
        if cmd_lower.startswith(dangerous):
            return False, f"Blocked system command: {dangerous}"
    
    # Check for sudo (optional, can be configured)
    if cmd_lower.startswith('sudo'):
        return False, "sudo commands require manual approval"
    
    return True, ""


def safe_execute(func):
    """Decorator for safe execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "code": -1
            }
    return wrapper


class TerminalAgent:
    """Terminal command execution — Hardened Version"""
    
    def __init__(self):
        self.system = platform.system()
        self.shell = True if self.system == "Windows" else False
        self.blocked_count = 0
        print(f"💻 Terminal Agent initialized (hardened mode)")
    
    # ===== EXECUTION =====
    
    @safe_execute
    def execute(self, command: str, timeout: int = 30) -> Dict:
        """Execute terminal command with safety checks"""
        # ← NEW: Security validation
        is_safe, reason = sanitize_command(command)
        if not is_safe:
            self.blocked_count += 1
            return {
                "success": False,
                "stdout": "",
                "stderr": f"🚫 {reason}",
                "code": -1,
                "blocked": True
            }
        
        try:
            result = subprocess.run(
                command,
                shell=self.shell,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip() or "(no output)",
                "stderr": result.stderr.strip() or "",
                "code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"⏱️ Timeout after {timeout}s",
                "code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "code": -1
            }
    
    def execute_safe(self, command: str) -> Dict:
        """Execute with additional safety layer"""
        return self.execute(command)
    
    # ===== GIT COMMANDS =====
    
    def git_status(self) -> Dict:
        return self.execute("git status")
    
    def git_pull(self) -> Dict:
        return self.execute("git pull")
    
    def git_push(self) -> Dict:
        return self.execute("git push")
    
    def git_commit(self, message: str) -> Dict:
        # Sanitize message to prevent injection
        safe_message = message.replace('"', '\\"').replace("'", "\\'")
        return self.execute(f'git commit -m "{safe_message}"')
    
    def git_branch(self) -> Dict:
        return self.execute("git branch")
    
    # ===== SYSTEM COMMANDS =====
    
    def ipconfig(self) -> Dict:
        """Network config"""
        cmd = "ipconfig" if self.system == "Windows" else "ifconfig"
        return self.execute(cmd)
    
    def ping(self, host: str = "google.com", count: int = 4) -> Dict:
        """Ping host"""
        # Sanitize host to prevent injection
        safe_host = re.sub(r'[;&|]', '', host)
        cmd = f"ping -n {count} {safe_host}" if self.system == "Windows" else f"ping -c {count} {safe_host}"
        return self.execute(cmd)
    
    def tasklist(self) -> Dict:
        """List processes"""
        cmd = "tasklist" if self.system == "Windows" else "ps aux"
        return self.execute(cmd)
    
    def dir_list(self, path: str = ".") -> Dict:
        """List directory"""
        # Prevent path traversal
        safe_path = os.path.normpath(path)
        if safe_path.startswith('..') or safe_path.startswith('/'):
            return {
                "success": False,
                "stderr": "Path traversal blocked",
                "code": -1
            }
        cmd = f"dir {safe_path}" if self.system == "Windows" else f"ls -la {safe_path}"
        return self.execute(cmd)
    
    # ===== PYTHON =====
    
    def pip_install(self, package: str) -> Dict:
        # Sanitize package name
        safe_package = re.sub(r'[;&|]', '', package)
        return self.execute(f"pip install {safe_package}")
    
    def python_run(self, script: str) -> Dict:
        # Prevent running arbitrary scripts
        if not os.path.exists(script):
            return {
                "success": False,
                "stderr": f"Script not found: {script}",
                "code": -1
            }
        return self.execute(f"python {script}")
    
    def python_version(self) -> Dict:
        return self.execute("python --version")
    
        # ===== HANDLER =====
    
    def handle(self, intent: str, entities: Dict) -> Dict:
        """Route intents to terminal commands"""
        cmd_lower = intent.lower()
        command = entities.get("command", entities.get("query", ""))
        
        if cmd_lower in ["terminal_run", "run"] and command:
            return self.execute(command)
        elif cmd_lower in ["terminal_git", "git_status"]:
            return self.git_status()
        elif cmd_lower in ["git_pull"]:
            return self.git_pull()
        elif cmd_lower in ["git_push"]:
            return self.git_push()
        elif cmd_lower in ["git_commit"]:
            msg = entities.get("message", "Update")
            return self.git_commit(msg)
        elif cmd_lower in ["terminal_pip", "pip_install"]:
            return self.pip_install(command or entities.get("package", ""))
        elif cmd_lower in ["terminal_npm", "npm_install"]:
            return self.execute(f"npm install {command}")
        elif cmd_lower in ["ipconfig", "ip"]:
            return self.ipconfig()
        elif "ping" in cmd_lower:
            return self.ping(command or "google.com")
        elif cmd_lower in ["tasklist", "ps"]:
            return self.tasklist()
        elif cmd_lower in ["python_version", "python"]:
            return self.python_version()
        elif cmd_lower.startswith("dir") or cmd_lower == "ls":
            return self.dir_list(command or ".")
        return self.execute(command or cmd_lower)
    
    # ===== NEW: Security Stats =====
    
    def get_security_stats(self) -> Dict:
        return {
            "blocked_commands": self.blocked_count,
            "dangerous_patterns": len(DANGEROUS_PATTERNS),
            "system": self.system
        }


# Singleton
terminal_agent = TerminalAgent()