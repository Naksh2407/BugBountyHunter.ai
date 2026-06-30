import re
from app.models.issue import Issue

class AnalysisAgent:

    @staticmethod
    def parse(findings: dict) -> list[Issue]:
        issues = []

        # 1. Parse Ruff
        if "ruff" in findings and findings["ruff"].get("stdout"):
            stdout = findings["ruff"]["stdout"]
            lines = stdout.splitlines()
            for idx, line in enumerate(lines):
                line_str = line.strip()
                if not line_str:
                    continue
                # Classic format: path:line:col: MSG or path:line: MSG
                match = re.match(r"^([^:]+):(\d+):(?:\d+:)?\s+(.*)$", line_str)
                if match:
                    file_path = match.group(1)
                    line_number = int(match.group(2))
                    message = match.group(3)
                    issues.append(Issue(
                        file_path=file_path,
                        line_number=line_number,
                        tool="ruff",
                        severity="error",
                        message=message
                    ))
                # New multi-line format: "--> path:line:col"
                elif line_str.startswith("-->") or " --> " in line:
                    match = re.search(r"-->\s+([^:]+):(\d+)", line_str)
                    if match:
                        file_path = match.group(1).strip()
                        line_number = int(match.group(2))
                        # Find the message on the preceding lines
                        message = "Ruff violation"
                        for k in range(idx - 1, -1, -1):
                            prev = lines[k].strip()
                            if prev and not prev.startswith("-->") and not prev.startswith("|") and not prev.isdigit():
                                message = prev
                                break
                        issues.append(Issue(
                            file_path=file_path,
                            line_number=line_number,
                            tool="ruff",
                            severity="error",
                            message=message
                        ))

        # 2. Parse Mypy
        if "mypy" in findings and findings["mypy"].get("stdout"):
            stdout = findings["mypy"]["stdout"]
            for line in stdout.splitlines():
                # mypy output format: path:line: error/warning/note: MSG
                match = re.match(r"^([^:]+):(\d+):\s+(error|warning|note):\s+(.*)$", line.strip())
                if match:
                    file_path = match.group(1)
                    line_number = int(match.group(2))
                    severity = match.group(3)
                    message = match.group(4)
                    issues.append(Issue(
                        file_path=file_path,
                        line_number=line_number, 
                        tool="mypy",
                        severity=severity,
                        message=message
                    ))

        # 3. Parse Bandit
        if "bandit" in findings and findings["bandit"].get("stdout"):
            stdout = findings["bandit"]["stdout"]
            blocks = stdout.split(">> Issue:")[1:]
            for block in blocks:
                lines = block.splitlines()
                if not lines:
                    continue
                # First line contains issue name/message, e.g., [B101:assert_used] Use of assert detected.
                msg_match = re.match(r"^\[([^\]]+)\]\s+(.*)$", lines[0].strip())
                code = msg_match.group(1) if msg_match else "bandit-error"
                desc = msg_match.group(2) if msg_match else lines[0].strip()

                # Look for Location line in the block
                location_match = re.search(r"Location:\s+([^:]+):(\d+)", block)
                if location_match:
                    file_path = location_match.group(1)
                    line_number = int(location_match.group(2))
                    issues.append(Issue(
                        file_path=file_path,
                        line_number=line_number,
                        tool="bandit",
                        severity="warning",
                        message=f"{code}: {desc}"
                    ))

        # 4. Parse ESLint
        if "eslint" in findings and findings["eslint"].get("stdout"):
            stdout = findings["eslint"]["stdout"]
            current_file = None
            for line in stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                if line.endswith((".js", ".ts", ".tsx", ".jsx")) or ("src\\" in line or "src/" in line):
                    current_file = line
                    continue
                match = re.match(r"^(\d+):(\d+)\s+(error|warning)\s+(.*)$", line)
                if match and current_file:
                    line_number = int(match.group(1))
                    severity = match.group(3)
                    message = match.group(4)
                    issues.append(Issue(
                        file_path=current_file,
                        line_number=line_number,
                        tool="eslint",
                        severity=severity,
                        message=message
                    ))

        return issues
