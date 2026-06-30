from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.workers.tasks import scan_repository_task
from app.agents.fixing_agent import FixingAgent
from app.agents.validation_agent import ValidationAgent
from app.models.issue import Issue
import os

router = APIRouter()

# MCP Tools List
MCP_TOOLS = [
    {
        "name": "scan_repository",
        "description": "Trigger an autonomous scan and repair sequence on a specific GitHub repository.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "github_url": {
                    "type": "string",
                    "description": "The URL of the repository to clone, scan and fix."
                }
            },
            "required": ["github_url"]
        }
    },
    {
        "name": "repair_issue",
        "description": "Generate and apply code repairs dynamically to a specific linter/security issue in a file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the target file."
                },
                "line_number": {
                    "type": "integer",
                    "description": "1-indexed line number where the issue resides."
                },
                "tool": {
                    "type": "string",
                    "description": "Tool that triggered the issue (e.g. 'ruff', 'bandit', 'eslint')."
                },
                "message": {
                    "type": "string",
                    "description": "The compiler/linter error message."
                },
                "repository_path": {
                    "type": "string",
                    "description": "Absolute path to the cloned repository root folder."
                },
                "stack": {
                    "type": "string",
                    "description": "The stack type: 'python' or 'node'.",
                    "default": "python"
                }
            },
            "required": ["file_path", "line_number", "tool", "message", "repository_path"]
        }
    },
    {
        "name": "validate_code",
        "description": "Execute validation tests (pytest/npm test) inside the docker sandboxed container or locally.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repository_path": {
                    "type": "string",
                    "description": "Absolute path to the repository directory."
                },
                "stack": {
                    "type": "string",
                    "description": "The stack to validate ('python' or 'node').",
                    "default": "python"
                }
            },
            "required": ["repository_path"]
        }
    }
]

@router.get("/mcp/tools")
def list_mcp_tools():
    """
    Exposes list of tools available in the BugBountyHunter MCP Server.
    """
    return {
        "tools": MCP_TOOLS
    }

@router.post("/mcp/tools/call")
def call_mcp_tool(
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    Call BugBountyHunter tool.
    Matches Model Context Protocol (MCP) JSON-RPC spec format.
    """
    name = payload.get("name")
    arguments = payload.get("arguments", {})

    if not name:
        raise HTTPException(status_code=400, detail="Missing tool name")

    try:
        if name == "scan_repository":
            github_url = arguments.get("github_url")
            if not github_url:
                return {"error": "Missing 'github_url' argument"}
            # Start background Celery task
            task = scan_repository_task.delay(github_url)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Successfully initiated repository scan background task. Task ID: {task.id}"
                    }
                ]
            }

        elif name == "repair_issue":
            file_path = arguments.get("file_path")
            line_number = arguments.get("line_number")
            tool = arguments.get("tool")
            message = arguments.get("message")
            repository_path = arguments.get("repository_path")
            stack = arguments.get("stack", "python")

            if not os.path.exists(file_path):
                return {"error": f"File path does not exist: {file_path}"}

            issue = Issue(
                file_path=file_path,
                line_number=line_number,
                tool=tool,
                severity="error",
                message=message
            )

            # Initiate repair
            fixer = FixingAgent()
            # Note: We run it synchronously here and pass a None scan_id since it's an ad-hoc MCP call
            best_candidate = fixer.fix_issue(
                issue=issue,
                repository_path=repository_path,
                stack=stack,
                db=db,
                scan_id=None
            )

            if best_candidate:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Successfully generated and applied fix. Validation Score: {best_candidate.get('score')}\nPatch Diff:\n{best_candidate.get('patch')}"
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "Failed to resolve issue. Validation tests did not pass or code did not satisfy security guardrails."
                        }
                    ]
                }

        elif name == "validate_code":
            repository_path = arguments.get("repository_path")
            stack = arguments.get("stack", "python")

            if not os.path.exists(repository_path):
                return {"error": f"Repository directory does not exist: {repository_path}"}

            val_res = ValidationAgent.run_tests(repository_path, stack=stack)
            status_text = "PASSED" if val_res.get("success") else "FAILED"
            exec_mode = "Sandboxed in Docker" if val_res.get("sandboxed") else "Local subprocess fallback"

            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Tests {status_text} (executed {exec_mode}).\nSTDOUT:\n{val_res.get('stdout')}\nSTDERR:\n{val_res.get('stderr')}"
                    }
                ]
            }

        else:
            raise HTTPException(status_code=404, detail=f"MCP Tool '{name}' not found")

    except Exception as e:
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": f"Error executing tool '{name}': {str(e)}"
                }
            ]
        }
