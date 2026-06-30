import subprocess
import os

class ScannerService:

    @staticmethod
    def run_command(
        cmd,
        cwd
    ):
        import sys
        # Resolve Windows executable issues for batch files like npm
        if os.name == "nt" and cmd and cmd[0] == "npm":
            cmd[0] = "npm.cmd"
            
        shell_mode = (os.name == "nt")

        # Inject current virtualenv's Scripts directory into PATH so that ruff, mypy, bandit are resolved correctly
        env = os.environ.copy()
        scripts_dir = os.path.dirname(sys.executable)
        env["PATH"] = scripts_dir + os.pathsep + env.get("PATH", "")

        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=shell_mode,
            env=env
        )

        return {
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }



class PythonScanner:

    @staticmethod
    def scan(path):

        results = {}

        results["ruff"] = ScannerService.run_command(
            ["ruff", "check", "."],
            path
        )

        results["mypy"] = ScannerService.run_command(
            ["mypy", "."],
            path
        )

        results["bandit"] = ScannerService.run_command(
            ["bandit", "-r", "."],
            path
        )

        return results


class NodeScanner:

    @staticmethod
    def scan(path):

        results = {}

        results["eslint"] = (
            ScannerService.run_command(
                ["npm", "run", "lint"],
                path
            )
        )

        results["test"] = (
            ScannerService.run_command(
                ["npm", "test"],
                path
            )
        )

        return results