import os
import shutil
import time
import stat
from sqlalchemy.orm import Session
from app.workers.tasks import scan_repository_task
from app.core.database import SessionLocal
from app.models.scan import Scan
from app.models.fix import Fix
from app.models.fix_attempt import FixAttempt

def force_remove_tree(path):
    if not os.path.exists(path):
        return
    def onerror(func, p, excinfo):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except Exception:
            pass
    shutil.rmtree(path, onerror=onerror)

class BugBountyEvaluator:

    @staticmethod
    def setup_mock_repo(target_path: str):
        """
        Creates a temporary test repository with intentional bugs for evaluation.
        """
        force_remove_tree(target_path)
        os.makedirs(target_path, exist_ok=True)
        
        # 1. Math Ops Python file with F821 Undefined Name error
        math_ops_content = """def divide(a, b):
    if b == 0:
        # Intentional bug: division_by_zero_error is undefined
        return division_by_zero_error
    return a / b

def multiply(a: int, b: int) -> int:
    # Intentional bug: missing return statement (will fail test)
    res = a * b
"""
        with open(os.path.join(target_path, "math_ops.py"), "w", encoding="utf-8") as f:
            f.write(math_ops_content)

        # 1b. Write requirements.txt so that StackDetector detects python
        with open(os.path.join(target_path, "requirements.txt"), "w", encoding="utf-8") as f:
            f.write("pytest\n")

        # 2. Pytest test cases
        test_math_content = """from math_ops import divide, multiply

def test_divide():
    assert divide(4, 2) == 2.0

def test_multiply():
    assert multiply(3, 4) == 12
"""
        with open(os.path.join(target_path, "test_math_ops.py"), "w", encoding="utf-8") as f:
            f.write(test_math_content)

        # 3. Create basic git structure so GitService doesn't fail
        try:
            import subprocess
            subprocess.run(["git", "init"], cwd=target_path, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Evaluator"], cwd=target_path, capture_output=True)
            subprocess.run(["git", "config", "user.email", "eval@agent.ai"], cwd=target_path, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=target_path, capture_output=True)
            subprocess.run(["git", "commit", "-m", "initial commit"], cwd=target_path, capture_output=True)
        except Exception as git_err:
            print(f"Git init warning in mock repo: {git_err}")

    @staticmethod
    def run_evaluation() -> dict:
        """
        Runs the evaluation suite and benchmarks BugBountyHunter.
        """
        db: Session = SessionLocal()
        scratch_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scratch"))
        eval_repo_path = os.path.join(scratch_dir, "evaluation-repo")
        
        try:
            print("Setting up evaluation benchmark repository...")
            BugBountyEvaluator.setup_mock_repo(eval_repo_path)
            
            # Start timer
            start_time = time.time()
            
            # Run scan repository task synchronously
            print("Triggering BugBountyHunter scan and auto-repair sequence on benchmark...")
            task_res = scan_repository_task(eval_repo_path)
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # Fetch the exact scan record that was executed
            scan_id = task_res.get("scan_id") if isinstance(task_res, dict) else None
            latest_scan = db.query(Scan).filter(Scan.id == scan_id).first() if scan_id else None
            if not latest_scan:
                return {"error": "No scan recorded."}
                
            fixes = db.query(Fix).filter(Fix.scan_id == latest_scan.id).all()
            attempts = db.query(FixAttempt).filter(FixAttempt.scan_id == latest_scan.id).all()
            
            # Calculate metrics
            total_bugs = 2  # Undefined variable and Missing return
            bugs_detected = 0
            if latest_scan.findings:
                # Ruff finding count
                ruff_out = latest_scan.findings.get("ruff", {}).get("stdout", "")
                if "F821" in ruff_out or "undefined" in ruff_out:
                    bugs_detected += 1
                
                # Mypy/test finding count
                if "multiply" in ruff_out or "multiply" in latest_scan.findings.get("mypy", {}).get("stdout", ""):
                    bugs_detected += 1
                    
            bugs_fixed = len(fixes)
            success_rate = (bugs_fixed / total_bugs) * 100.0 if total_bugs > 0 else 0.0
            
            # Extract self-refinement loops count
            refinement_cycles = 0
            for att in attempts:
                if "refined_attempt_" in att.status:
                    refinement_cycles += 1
            
            avg_refinement_cycles = refinement_cycles / len(attempts) if attempts else 0
            
            eval_metrics = {
                "scan_id": latest_scan.id,
                "benchmark_name": "AI Agents Course Benchmark V1",
                "execution_time_seconds": round(elapsed_time, 2),
                "total_bugs_preset": total_bugs,
                "bugs_detected": bugs_detected,
                "bugs_successfully_fixed": bugs_fixed,
                "success_rate_percentage": round(success_rate, 2),
                "total_attempts_generated": len(attempts),
                "self_refinement_cycles_executed": refinement_cycles,
                "avg_refinement_cycles_per_bug": round(avg_refinement_cycles, 2),
                "status": "passed" if success_rate >= 50.0 else "failed"
            }
            
            print(f"Evaluation completed successfully! Metrics: {eval_metrics}")
            return eval_metrics
            
        except Exception as e:
            print(f"Error executing evaluation suite: {e}")
            return {"error": str(e)}
        finally:
            db.close()
            # Clean up repo directory
            try:
                force_remove_tree(eval_repo_path)
            except Exception:
                pass
