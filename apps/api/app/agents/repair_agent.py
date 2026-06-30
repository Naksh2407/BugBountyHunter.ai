import os
import json
import time
from app.services.llm_service import LLMService
from app.services.git_service import GitService
from app.agents.context_agent import ContextAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.patch_agent import PatchAgent
from app.models.fix_attempt import FixAttempt
from app.models.scan import Scan as ScanModel
from app.services.memory_store import MemoryStoreService

class RepairAgent:

    def _append_trace(self, db, scan_id, log_line: str):
        if not (db and scan_id):
            print(log_line)
            return
        try:
            print(log_line)
            scan_rec = db.query(ScanModel).filter(ScanModel.id == scan_id).first()
            if scan_rec:
                current_trace = scan_rec.reasoning_trace or ""
                timestamp = time.strftime("%H:%M:%S")
                scan_rec.reasoning_trace = current_trace + f"[{timestamp}] {log_line}\n"
                db.commit()
        except Exception as e:
            print(f"Error appending trace: {e}")

    def repair_issue(
        self,
        issue,
        repository_path=None,
        stack="python",
        db=None,
        scan_id=None
    ):
        rel_path = os.path.relpath(issue.file_path, repository_path) if repository_path else issue.file_path
        self._append_trace(db, scan_id, f"Initiating repair for {issue.tool} issue in '{rel_path}' at line {issue.line_number}")

        # 1. Generate initial candidates using Dynamic AST / Lexical Context
        candidates = self.generate_candidates(issue, db=db)
        if not candidates:
            self._append_trace(db, scan_id, f"Could not generate candidates for '{rel_path}' (file missing or AST unparseable).")
            return None

        best_candidate = None
        best_score = -1

        for idx, candidate in enumerate(candidates):
            candidate_source = "Long-Term Memory cache" if candidate.get("from_memory") else "LLM Generative agent"
            self._append_trace(db, scan_id, f"Evaluating candidate #{idx+1} sourced from {candidate_source}")

            # 2. Defensive Security Guardrail Check (Kaggle Day 4)
            self._append_trace(db, scan_id, "Statically evaluating patch candidate safety...")
            passed_security, sec_msg = ValidationAgent.verify_patch_safety(candidate["fixed_content"], candidate["file_path"])
            if not passed_security:
                self._append_trace(db, scan_id, f"Security Warning: Candidate rejected. Reason: {sec_msg}")
                self.log_attempt(candidate, 0.0, {"success": False, "stderr": sec_msg}, "rejected_security_guardrail", db, scan_id, issue, repository_path)
                continue
            
            self._append_trace(db, scan_id, "Security check passed. Staging patch and running tests...")

            # 3. Run initial validation (Docker sandbox / Local test runner)
            score, val_res = self.validate_candidate(
                candidate,
                repository_path,
                stack
            )

            status = "passed_validation" if score >= 1.0 else "failed_validation"
            if candidate.get("from_memory"):
                status += "_memory"
            self._append_trace(db, scan_id, f"Validation results: status={status}, test_score={score}")
            self.log_attempt(candidate, score, val_res, status, db, scan_id, issue, repository_path)

            # 4. Self-Refinement Loop: If validation failed, try up to 3 times using compiler logs
            refine_attempts = 0
            max_refine_attempts = 3
            header_context = candidate.get("header_context", "")

            while score < 1.0 and val_res and refine_attempts < max_refine_attempts:
                refine_attempts += 1
                try:
                    stdout = val_res.get("stdout", "")
                    stderr = val_res.get("stderr", "")
                    error_message = f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}"
                    
                    self._append_trace(db, scan_id, f"Triggering Self-Refinement Loop (Cycle #{refine_attempts}/{max_refine_attempts}) using compilation/test errors.")

                    # Call LLM to refine the fix
                    raw_refined = LLMService.generate_refined_fix(
                        issue=issue,
                        code_context=candidate["context"],
                        failed_code=candidate["raw_fix"],
                        error_message=error_message,
                        header_context=header_context
                    )
                    refined_context = self._sanitize_code(raw_refined)

                    # Reconstruct file content with refined fix
                    with open(candidate["file_path"], "r", encoding="utf-8") as f:
                        original_lines = f.readlines()
                    
                    new_lines = original_lines[:candidate["start"]] + [refined_context] + original_lines[candidate["end"]:]
                    refined_content = "".join(new_lines)
                    refined_patch = PatchAgent.create_patch(candidate["file_path"], refined_content)

                    # Create refined candidate dict
                    refined_candidate = {
                        "file_path": candidate["file_path"],
                        "original_content": candidate["original_content"],
                        "fixed_content": refined_content,
                        "patch": refined_patch,
                        "raw_fix": raw_refined,
                        "context": candidate["context"],
                        "start": candidate["start"],
                        "end": candidate["end"],
                        "header_context": header_context
                    }

                    # Re-run Security Guardrail Check on refined code
                    passed_security, sec_msg = ValidationAgent.verify_patch_safety(refined_content, candidate["file_path"])
                    if not passed_security:
                        self._append_trace(db, scan_id, f"Refinement Security Warning: Cycle #{refine_attempts} candidate rejected. Reason: {sec_msg}")
                        self.log_attempt(refined_candidate, 0.0, {"success": False, "stderr": sec_msg}, f"refined_attempt_{refine_attempts}_rejected", db, scan_id, issue, repository_path)
                        val_res = {"success": False, "stderr": sec_msg}
                        continue

                    # Validate refined candidate
                    refined_score, refined_val_res = self.validate_candidate(
                        refined_candidate,
                        repository_path,
                        stack
                    )

                    refined_status = f"refined_attempt_{refine_attempts}_" + ("passed" if refined_score >= 1.0 else "failed")
                    self._append_trace(db, scan_id, f"Refinement Cycle #{refine_attempts} validation outcome: score={refined_score}")
                    self.log_attempt(refined_candidate, refined_score, refined_val_res, refined_status, db, scan_id, issue, repository_path)

                    # Keep refined fix if it improved performance
                    if refined_score > score:
                        self._append_trace(db, scan_id, f"Refinement cycle succeeded. Improved score from {score} to {refined_score}.")
                        candidate = refined_candidate
                        score = refined_score
                        val_res = refined_val_res
                    else:
                        candidate = refined_candidate
                        val_res = refined_val_res
                except Exception as refine_err:
                    self._append_trace(db, scan_id, f"Exception in self-refinement cycle: {refine_err}")
                    break

            candidate["score"] = score

            if score > best_score:
                best_score = score
                best_candidate = candidate

        # 5. Long-Term Memory Store (Kaggle Day 3)
        if best_candidate and best_score >= 1.0 and not best_candidate.get("from_memory"):
            self._append_trace(db, scan_id, "Saving successful patch to Long-Term Memory...")
            MemoryStoreService.save_fix_pattern(
                db=db,
                tool=issue.tool,
                message=issue.message,
                file_path=best_candidate["file_path"],
                successful_patch=best_candidate["raw_fix"]
            )

        self._append_trace(db, scan_id, f"Repair agent cycle completed. Best patch validation score: {best_score}")
        return best_candidate

    def log_attempt(
        self,
        candidate,
        score,
        val_res,
        status,
        db=None,
        scan_id=None,
        issue=None,
        repository_path=None
    ):
        if not (db and scan_id):
            return
        try:
            rel_path = os.path.relpath(candidate["file_path"], repository_path) if repository_path else candidate["file_path"]
            val_res_str = json.dumps(val_res) if val_res else None
            
            attempt = FixAttempt(
                scan_id=scan_id,
                file_path=rel_path,
                line_number=issue.line_number if issue else None,
                original_code=candidate["original_content"],
                candidate_code=candidate["fixed_content"],
                patch=candidate["patch"],
                score=score,
                validation_result=val_res_str,
                status=status
            )
            db.add(attempt)
            db.commit()
        except Exception as db_err:
            print(f"Error saving FixAttempt to DB: {db_err}")

    def generate_candidates(self, issue, num_candidates=2, db=None):
        file_path = issue.file_path
        if not os.path.exists(file_path):
            return []

        # Read original file
        with open(file_path, "r", encoding="utf-8") as f:
            original_lines = f.readlines()
        original_content = "".join(original_lines)

        # Extract module header context (first 15 lines of imports/globals)
        header_lines = original_lines[:15]
        header_context = "".join(header_lines)

        # 1. Use Dynamic Context Expansion (AST / Lexical)
        try:
            context, start, end = ContextAgent.extract_context(file_path, issue.line_number)
        except Exception as context_err:
            print(f"Dynamic context extraction failed ({context_err}). Falling back to static radius.")
            radius = 30
            start = max(0, issue.line_number - 1 - radius)
            end = min(len(original_lines), issue.line_number - 1 + radius)
            context = "".join(original_lines[start:end])

        # 2. Check Long-Term Memory first (Kaggle Day 3)
        cached_fix = None
        if db:
            cached_fix = MemoryStoreService.get_relevant_patch(db, issue.tool, issue.message, file_path)

        if cached_fix:
            new_lines = original_lines[:start] + [cached_fix] + original_lines[end:]
            fixed_content = "".join(new_lines)
            patch = PatchAgent.create_patch(file_path, fixed_content)
            
            return [{
                "file_path": file_path,
                "original_content": original_content,
                "fixed_content": fixed_content,
                "patch": patch,
                "raw_fix": cached_fix,
                "context": context,
                "start": start,
                "end": end,
                "header_context": header_context,
                "from_memory": True
            }]

        candidates = []
        for i in range(num_candidates):
            try:
                # Call LLM to generate fix
                raw_fix = LLMService.generate_fix(issue, context, header_context=header_context)
                fixed_context = self._sanitize_code(raw_fix)

                # Reconstruct full file content with the fix applied to context block
                new_lines = original_lines[:start] + [fixed_context] + original_lines[end:]
                fixed_content = "".join(new_lines)

                # Generate unified diff
                patch = PatchAgent.create_patch(file_path, fixed_content)

                candidates.append({
                    "file_path": file_path,
                    "original_content": original_content,
                    "fixed_content": fixed_content,
                    "patch": patch,
                    "raw_fix": raw_fix,
                    "context": context,
                    "start": start,
                    "end": end,
                    "header_context": header_context,
                    "from_memory": False
                })
            except Exception as e:
                print(f"Error generating candidate {i}: {e}")

        return candidates

    def validate_candidate(self, candidate, repository_path, stack):
        file_path = candidate["file_path"]
        original_content = candidate["original_content"]
        fixed_content = candidate["fixed_content"]

        try:
            # Apply fix
            GitService.apply_fix(file_path, fixed_content)

            # Run validation tests
            val_res = ValidationAgent.run_tests(repository_path, stack)
            
            # Revert fix immediately to keep workspace clean
            GitService.apply_fix(file_path, original_content)

            if val_res.get("success"):
                return 1.0, val_res
            return 0.2, val_res  # compiled/applied but tests failed
        except Exception as e:
            print(f"Validation error: {e}")
            try:
                GitService.apply_fix(file_path, original_content)
            except Exception:
                pass
            return 0.0, None

    def _sanitize_code(self, code: str) -> str:
        code = code.strip()
        if code.startswith("```"):
            lines = code.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            code = "\n".join(lines)
        return code