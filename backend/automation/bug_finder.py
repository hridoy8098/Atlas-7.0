import re
import ast
import traceback
from typing import Dict, Any, Optional, List
from backend.core.ai_engine import ai_engine


class BugFinder:
    def __init__(self):
        self.history = []

    def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        issues = []
        if language == "python":
            issues = self._check_python_syntax(code)
        suggestions = self._ai_review(code, language)
        result = {
            "success": True,
            "language": language,
            "issues": issues,
            "issue_count": len(issues),
            "suggestions": suggestions,
        }
        self.history.append({"code_length": len(code), "issues": len(issues), "time": __import__("datetime").datetime.now().isoformat()})
        return result

    def _check_python_syntax(self, code: str) -> List[Dict]:
        issues = []
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append({
                "type": "syntax_error",
                "message": str(e),
                "line": e.lineno or 0,
                "offset": e.offset or 0,
            })
        dangerous = ["eval(", "exec(", "__import__", "os.system", "subprocess.call", "pickle.loads"]
        for i, line in enumerate(code.split("\n"), 1):
            for pattern in dangerous:
                if pattern in line:
                    issues.append({
                        "type": "security_warning",
                        "message": f"Potentially dangerous function '{pattern}' used",
                        "line": i,
                    })
        return issues

    def _ai_review(self, code: str, language: str) -> str:
        try:
            prompt = f"""Review this {language} code for bugs, performance issues, and improvements:
```{language}
{code[:2000]}
```
List specific bugs, security issues, and optimization suggestions."""
            return ai_engine.chat(prompt)
        except Exception:
            return "AI review unavailable."

    def find_logical_errors(self, code: str) -> Dict[str, Any]:
        issues = []
        lines = code.split("\n")
        variables = set()
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//"):
                continue
            assign_match = re.match(r"^(\w+)\s*=", stripped)
            if assign_match:
                variables.add(assign_match.group(1))
            refs = re.findall(r"\b([a-z_][a-z0-9_]*)\b", stripped, re.IGNORECASE)
            for ref in refs:
                if ref not in {"self", "None", "True", "False", "print", "len", "range", "int", "str", "list", "dict", "set", "return", "if", "else", "elif", "for", "while", "in", "not", "and", "or", "is", "def", "class", "import", "from", "as", "try", "except", "finally", "with", "pass", "break", "continue", "raise", "yield", "lambda", "global", "nonlocal"} and ref not in variables and i > 1:
                    if not stripped.startswith("#") and "def " not in stripped and "class " not in stripped:
                        issues.append({"type": "potential_bug", "message": f"Possibly undefined variable '{ref}'", "line": i})
        return {"success": True, "issues": issues, "count": len(issues)}

    def get_history(self) -> Dict[str, Any]:
        return {"success": True, "history": self.history[-50:]}


bug_finder = BugFinder()
