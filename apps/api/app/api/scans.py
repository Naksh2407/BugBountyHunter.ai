from fastapi import APIRouter, Depends
from celery.result import AsyncResult  # type: ignore
from sqlalchemy.orm import Session

from app.workers.tasks import (
    scan_repository_task
)
from app.workers.celery_app import (
    celery_app
)
from app.core.database import get_db
from app.models.scan import Scan
from app.models.repository import Repository
from app.models.fix import Fix
from app.models.fix_attempt import FixAttempt

router = APIRouter()


@router.post("/scan")
def scan_repository(
    payload: dict
):

    task = scan_repository_task.delay(
        payload["github_url"]
    )

    return {
        "task_id": task.id
    }


@router.get("/scan/status/{task_id}")
def get_scan_status(
    task_id: str
):

    res = AsyncResult(
        task_id,
        app=celery_app
    )

    if res.state == "SUCCESS":
        return {
            "task_id": task_id,
            "status": "completed",
            "result": res.result
        }
    elif res.state == "FAILURE":
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(res.result)
        }
    else:
        return {
            "task_id": task_id,
            "status": res.state.lower()
        }


@router.get("/scans")
def list_scans(db: Session = Depends(get_db)):
    results = db.query(Scan, Repository.github_url, Repository.repo_name).\
        join(Repository, Scan.repository_id == Repository.id).\
        order_by(Scan.id.desc()).all()
    
    scans_list = []
    for scan, github_url, repo_name in results:
        scans_list.append({
            "id": scan.id,
            "repository_id": scan.repository_id,
            "github_url": github_url,
            "repo_name": repo_name,
            "status": scan.status
        })
    return scans_list


@router.get("/scans/{scan_id}")
def get_scan_details(scan_id: str, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        return {"error": "Scan not found"}
        
    repo = db.query(Repository).filter(Repository.id == scan.repository_id).first()
    fixes = db.query(Fix).filter(Fix.scan_id == scan_id).all()
    attempts = db.query(FixAttempt).filter(FixAttempt.scan_id == scan_id).all()
    
    return {
        "scan": {
            "id": scan.id,
            "status": scan.status,
            "findings": scan.findings,
            "token_usage": scan.token_usage or 0,
            "execution_time": scan.execution_time or 0.0,
            "reasoning_trace": scan.reasoning_trace or ""
        },
        "repository": {
            "github_url": repo.github_url if repo else "",
            "repo_name": repo.repo_name if repo else ""
        },
        "fixes": [
            {
                "id": f.id,
                "file_path": f.file_path,
                "patch": f.patch,
                "status": f.status
            } for f in fixes
        ],
        "attempts": [
            {
                "id": a.id,
                "file_path": a.file_path,
                "line_number": a.line_number,
                "patch": a.patch,
                "score": a.score,
                "status": a.status,
                "validation_result": a.validation_result
            } for a in attempts
        ]
    }

@router.post("/evaluate")
def run_evaluation_suite():
    from app.evaluation.evaluator import BugBountyEvaluator
    res = BugBountyEvaluator.run_evaluation()
    return res