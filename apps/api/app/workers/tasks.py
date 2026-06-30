import os
import time
from app.services.llm_service import LLMService

from app.workers.celery_app import (
    celery_app
)

from app.services.github_service import (
    GithubService
)

from app.agents.stack_detector_agent import (
    StackDetectorAgent
)

from app.agents.scan_agent import (
    ScanAgent
)

from app.agents.analysis_agent import (
    AnalysisAgent
)

from app.agents.fixing_agent import (
    FixingAgent
)

from app.agents.validation_agent import (
    ValidationAgent
)

from app.core.database import SessionLocal, Base, engine
from app.models.repository import Repository
from app.models.scan import Scan
from app.models.fix import Fix
from app.models.memory import FixPatternMemory

# Ensure tables are created when the Celery worker initializes
Base.metadata.create_all(bind=engine)


@celery_app.task
def scan_repository_task(
    repository_url
):
    db = SessionLocal()
    LLMService.reset_tokens()
    start_time = time.time()
    
    try:
        # Find or create repository record
        normalized_url = repository_url.replace("\\", "/").rstrip("/")
        repo_name = normalized_url.split("/")[-1]
        repo = db.query(Repository).filter(Repository.github_url == repository_url).first()
        if not repo:
            repo = Repository(
                github_url=repository_url,
                repo_name=repo_name,
                status="scanning"
            )
            db.add(repo)
            db.commit()
            db.refresh(repo)
        else:
            repo.status = "scanning"
            db.commit()

        # Create scan record
        scan = Scan(
            repository_id=repo.id,
            status="running",
            findings={}
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)

        # 1. Clone repository
        repository_path = GithubService.clone_repository(
            repository_url
        )

        # 2. Stack Detection
        stack = (
            StackDetectorAgent()
            .run(repository_path)
        )

        # 3. Running Scanners
        findings = (
            ScanAgent()
            .run(
                stack,
                repository_path
            )
        )

        # Update findings in database
        scan.findings = findings
        db.commit()

        # 4. Issue Parsing
        parser = AnalysisAgent()
        issues = parser.parse(findings)

        # 5. Automated Fixing
        fixer = FixingAgent()
        applied_fixes = []
        for issue in issues:
            original_rel_path = issue.file_path
            
            # Join target file paths with the cloned repository directory path for execution
            issue.file_path = os.path.join(repository_path, issue.file_path)
            
            best_candidate = fixer.fix_issue(
                issue,
                repository_path=repository_path,
                stack=stack,
                db=db,
                scan_id=scan.id
            )
            
            if best_candidate:
                # Add to DB Fix table
                fix_rec = Fix(
                    scan_id=scan.id,
                    file_path=original_rel_path,
                    patch=best_candidate["patch"],
                    status="applied"
                )
                db.add(fix_rec)
                db.commit()
                
                # Keep track for the Pull Request
                applied_fixes.append(best_candidate)

        # 6. Validation
        validation = (
            ValidationAgent.run_tests(
                repository_path,
                stack=stack
            )
        )

        if validation["success"]:
            print("Accepted")
        else:
            print("Rejected")

        # 7. Open Pull Request if changes succeeded and validated
        pr_info = None
        if validation["success"] and applied_fixes:
            from app.agents.pr_agent import PRAgent
            try:
                pr_info = PRAgent.create_pr_for_fixes(
                    repository_path=repository_path,
                    repository_url=repository_url,
                    fixes=applied_fixes
                )
            except Exception as pr_err:
                print(f"Error opening Pull Request on GitHub: {pr_err}")

        # Update Scan and Repo Status
        scan.token_usage = LLMService.total_tokens_used
        scan.execution_time = time.time() - start_time
        scan.status = "completed"
        repo.status = "completed"
        db.commit()

        return {
            "scan_id": scan.id,
            "stack": stack,
            "findings": findings,
            "validation": validation,
            "pull_request": pr_info
        }

    except Exception as e:
        # Rollback status on failure
        if 'scan' in locals():
            scan.status = "failed"
        if 'repo' in locals():
            repo.status = "failed"
        db.commit()
        print(f"Error executing scan repository task: {e}")
        raise e
    finally:
        db.close()