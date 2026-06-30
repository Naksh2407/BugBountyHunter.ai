
class ReportService:

    @staticmethod
    def generate_markdown_report(findings: dict, validation_results: dict, applied_fixes: list, attempts: list | None = None) -> str:
        report = "# 🎯 BugBountyHunter Scan & Auto-Repair Report\n\n"
        
        # 1. Summary Section
        report += "## 📋 Executive Summary\n"
        if applied_fixes:
            report += f"✅ **Status**: Scanning completed. BugBountyHunter successfully applied **{len(applied_fixes)}** code repairs.\n\n"
        else:
            report += "✅ **Status**: Scanning completed. No issues were found or successfully patched.\n\n"

        # 2. Tech Stack and Scanner Tools Section
        report += "### 🔍 Tools Executed\n"
        for tool, details in findings.items():
            return_code = details.get("return_code", 0)
            status_icon = "⚠️" if return_code != 0 else "✅"
            report += f"- {status_icon} **{tool.upper()}**: return code `{return_code}`\n"
        report += "\n"

        # 3. Applied Fixes Section
        if applied_fixes:
            report += "## 🛠️ Applied Code Repairs\n"
            report += "The following issues were detected and repaired:\n\n"
            for idx, fix in enumerate(applied_fixes, 1):
                file_path = fix.get("file_path", "unknown")
                score = fix.get("score", 0.0)
                report += f"### {idx}. {file_path}\n"
                report += f"- **Linter/Scanner validation score**: `{score}`\n"
                if fix.get("patch"):
                    report += "<details><summary><b>Unified Patch Code</b></summary>\n\n"
                    report += f"```diff\n{fix.get('patch')}\n```\n\n"
                    report += "</details>\n\n"
        
        # 4. Complex Refinement Trace Log Section
        if attempts:
            report += "## 🔄 Complex Refinement Trace Log\n"
            report += "Below is the history of code repair attempts and linter/validation feedback:\n\n"
            for idx, att in enumerate(attempts, 1):
                file_path = att.get("file_path", "unknown")
                line_number = att.get("line_number", "unknown")
                status = att.get("status", "unknown")
                score = att.get("score", 0.0)
                
                status_icon = "✅" if score >= 1.0 else "❌" if score == 0.0 else "⏳"
                report += f"### Attempt {idx}: {file_path} (Line {line_number})\n"
                report += f"- **Outcome**: {status_icon} `{status}` (Validation Score: `{score}`)\n"
                if att.get("patch"):
                    report += "<details><summary><b>Attempt Patch Diff</b></summary>\n\n"
                    report += f"```diff\n{att.get('patch')}\n```\n\n"
                    report += "</details>\n\n"

        # 5. Final Validation Results Section
        report += "## 🛡️ Sandbox Validation\n"
        if validation_results:
            success = validation_results.get("success", False)
            sandboxed = validation_results.get("sandboxed", False)
            status_str = "✅ PASSED" if success else "❌ REJECTED"
            sandbox_str = "Docker Sandbox" if sandboxed else "Local Environment"
            report += f"- **Validation Outcome**: **{status_str}**\n"
            report += f"- **Execution Environment**: `{sandbox_str}`\n\n"
            
            stdout = validation_results.get("stdout", "")
            stderr = validation_results.get("stderr", "")
            if stdout or stderr:
                report += "<details><summary><b>Validation Output Log</b></summary>\n\n"
                if stdout:
                    report += f"```text\n{stdout[:1000]}\n```\n"
                if stderr:
                    report += f"```text\n{stderr[:1000]}\n```\n"
                report += "</details>\n"
        else:
            report += "No sandbox validation run was captured.\n"

        return report
