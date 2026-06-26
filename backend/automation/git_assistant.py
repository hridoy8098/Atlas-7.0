import os
import subprocess
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from backend.core.ai_engine import ai_engine


class GitAssistant:
    def __init__(self):
        self.repos = {}

    def _run_git(self, args: List[str], repo_path: Optional[str] = None) -> Dict[str, Any]:
        cmd = ["git"]
        if repo_path:
            cmd.extend(["-C", repo_path])
        cmd.extend(args)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Git command timed out"}
        except FileNotFoundError:
            return {"success": False, "error": "Git not found. Install git first."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def status(self, repo_path: str = ".") -> Dict[str, Any]:
        result = self._run_git(["status", "--porcelain"], repo_path)
        if result["success"]:
            lines = [l for l in result["stdout"].split("\n") if l]
            staged = [l[3:] for l in lines if l[0] != "?" and l[0] != " "]
            unstaged = [l[3:] for l in lines if l[0] == " "]
            untracked = [l[3:] for l in lines if l[0] == "?"]
            branch_result = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_path)
            branch = branch_result["stdout"] if branch_result["success"] else "unknown"
            return {"success": True, "branch": branch, "staged": staged, "unstaged": unstaged, "untracked": untracked, "total": len(lines)}
        return result

    def commit(self, message: str, repo_path: str = ".", auto_add: bool = True) -> Dict[str, Any]:
        if auto_add:
            self._run_git(["add", "-A"], repo_path)
        result = self._run_git(["commit", "-m", message], repo_path)
        if result["success"]:
            return {"success": True, "message": "Commit successful", "hash": self._get_latest_hash(repo_path)}
        return {"success": False, "error": result.get("stderr", "Commit failed")}

    def smart_commit(self, repo_path: str = ".") -> Dict[str, Any]:
        status = self.status(repo_path)
        if not status["success"]:
            return status
        changes = status.get("staged", []) + status.get("unstaged", []) + status.get("untracked", [])
        if not changes:
            return {"success": True, "message": "Nothing to commit"}
        try:
            prompt = f"""Generate a concise git commit message based on these changed files:
{json.dumps(changes[:20], indent=2)}
Return ONLY the commit message, no explanation."""
            message = ai_engine.chat(prompt)
            if not message or len(message) < 3:
                message = f"Update {', '.join(changes[:3])}"
        except Exception:
            message = f"Update {', '.join(changes[:3])}"
        return self.commit(message.strip(), repo_path)

    def log(self, repo_path: str = ".", count: int = 10) -> Dict[str, Any]:
        result = self._run_git(["log", f"--max-count={count}", "--oneline", "--pretty=format:%h|%an|%ar|%s"], repo_path)
        if result["success"]:
            commits = []
            for line in result["stdout"].split("\n"):
                if "|" in line:
                    parts = line.split("|", 3)
                    commits.append({"hash": parts[0], "author": parts[1], "date": parts[2], "message": parts[3] if len(parts) > 3 else ""})
            return {"success": True, "commits": commits, "count": len(commits)}
        return result

    def push(self, repo_path: str = ".", remote: str = "origin", branch: Optional[str] = None) -> Dict[str, Any]:
        if not branch:
            br = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_path)
            branch = br["stdout"] if br["success"] else "main"
        return self._run_git(["push", remote, branch], repo_path)

    def pull(self, repo_path: str = ".", remote: str = "origin", branch: Optional[str] = None) -> Dict[str, Any]:
        if not branch:
            br = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_path)
            branch = br["stdout"] if br["success"] else "main"
        return self._run_git(["pull", remote, branch], repo_path)

    def branch(self, repo_path: str = ".") -> Dict[str, Any]:
        result = self._run_git(["branch", "-a"], repo_path)
        if result["success"]:
            branches = [{"name": b.strip().replace("* ", ""), "current": b.strip().startswith("*")} for b in result["stdout"].split("\n") if b.strip()]
            return {"success": True, "branches": branches, "current": next((b["name"] for b in branches if b["current"]), None)}
        return result

    def diff(self, repo_path: str = ".") -> Dict[str, Any]:
        result = self._run_git(["diff", "--stat"], repo_path)
        return {"success": result["success"], "diff": result.get("stdout", "")}

    def _get_latest_hash(self, repo_path: str) -> str:
        r = self._run_git(["rev-parse", "--short", "HEAD"], repo_path)
        return r.get("stdout", "") if r["success"] else ""


git_assistant = GitAssistant()
