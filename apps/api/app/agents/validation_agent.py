import subprocess
import os
import ast
import re
from app.sandbox.docker_manager import DockerManager
from app.sandbox.sandbox_runner import SandboxRunner

class ValidationAgent:

    @staticmethod
    def verify_patch_safety(
        fixed_code: str,
        file_path: str
    ) -> tuple[bool, str]:
        """
        Kaggle Day 4 Security Guardrail:
        Statically analyzes the proposed patch to check for prompt injections,
        malicious code patterns, backdoors, or critical security vulnerabilities
        before executing the code.
        """
        ext = os.path.splitext(file_path)[-1].lower()
        
        # 1. Python specific AST-based defensive analysis
        if ext == ".py":
            try:
                tree = ast.parse(fixed_code)
                for node in ast.walk(tree):
                    # Check for eval() and exec()
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            if node.func.id in ("eval", "exec"):
                                return False, f"Defensive check triggered: use of forbidden function '{node.func.id}' detected."
                        
                        # Check for unsafe imports using __import__
                        elif isinstance(node.func, ast.Attribute):
                            if node.func.attr == "__import__":
                                return False, "Defensive check triggered: dynamic import '__import__' detected."

                    # Check for risky import statements
                    elif isinstance(node, ast.Import):
                        for name in node.names:
                            if name.name in ("pty", "socket", "ctypes"):
                                return False, f"Defensive check triggered: importation of unsafe module '{name.name}' is blocked."
                                
                    elif isinstance(node, ast.ImportFrom):
                        if node.module in ("pty", "socket", "ctypes"):
                            return False, f"Defensive check triggered: importation from unsafe module '{node.module}' is blocked."
            except Exception as e:
                # If it's syntactically invalid Python, that's caught by linter/compilers anyway,
                # but we shouldn't execute it.
                return False, f"Defensive check triggered: proposed patch contains syntax errors: {e}"

        # 2. JS/TS Lexical matching safety rules
        elif ext in (".js", ".ts", ".tsx", ".jsx"):
            # Check for eval, exec, child_process, process.env exfiltrations
            unsafe_patterns = [
                (r"\beval\s*\(", "eval() execution"),
                (r"\bexec\s*\(", "exec() execution"),
                (r"child_process", "child_process system access"),
                (r"fs\.writeFile", "unauthorized filesystem modifications"),
                (r"process\.env", "environment variables exfiltration risk")
            ]
            for pattern, reason in unsafe_patterns:
                if re.search(pattern, fixed_code):
                    return False, f"Defensive check triggered: potential unsafe pattern '{reason}' found in JavaScript code."

        return True, "Code patch passed defensive security check."

    @staticmethod
    def run_tests(
        repository_path,
        stack="python"
    ):
        # 1. Determine command based on stack
        if stack == "node":
            cmd = ["npm", "test"]
            docker_image = "node:18-slim"
        else:  # default to python
            cmd = ["pytest"]
            docker_image = "python:3.10-slim"

        # 2. Try Docker validation first
        try:
            manager = DockerManager()
            container = manager.create_container(docker_image, repository_path)
            try:
                if stack == "node":
                    exec_cmd = ["sh", "-c", "npm install && npm test"]
                else:
                    exec_cmd = ["sh", "-c", "pip install pytest && pytest"]

                result = SandboxRunner.execute(container, exec_cmd)
                
                success = result.get("exit_code") == 0
                stdout = result.get("output", "")
                stderr = ""
                
                return {
                    "success": success,
                    "stdout": stdout,
                    "stderr": stderr,
                    "sandboxed": True
                }
            finally:
                try:
                    container.stop(timeout=2)
                    container.remove()
                except Exception:
                    pass
        except Exception as e:
            # Fallback to local subprocess execution if Docker is unavailable
            print(f"Docker validation failed/unavailable ({e}). Falling back to local execution.")
            
            try:
                if stack == "node":
                    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
                    subprocess.run([npm_cmd, "install"], cwd=repository_path, capture_output=True)
                    result = subprocess.run(
                        [npm_cmd, "test"],
                        cwd=repository_path,
                        capture_output=True,
                        text=True
                    )
                else:
                    import sys
                    result = subprocess.run(
                        [sys.executable, "-m", "pytest"],
                        cwd=repository_path,
                        capture_output=True,
                        text=True
                    )

                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "sandboxed": False
                }
            except Exception as inner_e:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Local execution failed: {str(inner_e)}",
                    "sandboxed": False
                }