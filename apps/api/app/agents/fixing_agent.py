from app.agents.repair_agent import RepairAgent
from app.services.git_service import GitService

class FixingAgent:

    def fix_issue(
        self,
        issue,
        repository_path=None,
        stack="python",
        db=None,
        scan_id=None
    ):
        repair_agent = RepairAgent()
        
        best_candidate = repair_agent.repair_issue(
            issue=issue,
            repository_path=repository_path,
            stack=stack,
            db=db,
            scan_id=scan_id
        )

        if best_candidate and best_candidate.get("score", 0) > 0:
            # Permanently apply the best fix content to the file
            GitService.apply_fix(
                best_candidate["file_path"],
                best_candidate["fixed_content"]
            )
            return best_candidate

        return None
