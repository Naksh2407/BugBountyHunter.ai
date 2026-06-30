import sys
import json
import os
import traceback
import contextlib

# Helper to redirect sys.stdout to sys.stderr so print statements in agents don't corrupt JSON-RPC stdio
@contextlib.contextmanager
def redirect_stdout_to_stderr():
    old_stdout = sys.stdout
    sys.stdout = sys.stderr
    try:
        yield
    finally:
        sys.stdout = old_stdout

def invoke_tool(name, arguments):
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        if name == "scan_repository":
            github_url = arguments.get("github_url")
            if not github_url:
                return {
                    "content": [{"type": "text", "text": "Error: Missing 'github_url' argument"}],
                    "isError": True
                }
            
            # For stdio client execution, run the scan synchronously to return the final status/findings
            from app.workers.tasks import scan_repository_task
            result = scan_repository_task(github_url)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Scan completed successfully.\nResult details:\n{json.dumps(result, indent=2)}"
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
                return {
                    "content": [{"type": "text", "text": f"Error: File path does not exist: {file_path}"}],
                    "isError": True
                }
                
            from app.models.issue import Issue
            from app.agents.fixing_agent import FixingAgent
            
            issue = Issue(
                file_path=file_path,
                line_number=line_number,
                tool=tool,
                severity="error",
                message=message
            )
            
            fixer = FixingAgent()
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
                    ],
                    "isError": True
                }
                
        elif name == "validate_code":
            repository_path = arguments.get("repository_path")
            stack = arguments.get("stack", "python")
            
            if not os.path.exists(repository_path):
                return {
                    "content": [{"type": "text", "text": f"Error: Repository directory does not exist: {repository_path}"}],
                    "isError": True
                }
                
            from app.agents.validation_agent import ValidationAgent
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
            return {
                "content": [{"type": "text", "text": f"Error: Unknown tool {name}"}],
                "isError": True
            }
            
    except Exception as e:
        return {
            "isError": True,
            "content": [
                {
                    "type": "text",
                    "text": f"Exception executing tool '{name}': {str(e)}\n{traceback.format_exc()}"
                }
            ]
        }
    finally:
        db.close()

def handle_request(req):
    msg_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "bugbountyhunter",
                    "version": "1.0.0"
                }
            }
        }
    
    elif method == "tools/list":
        from app.api.mcp_router import MCP_TOOLS
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": MCP_TOOLS
            }
        }
        
    elif method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        # Protect stdout JSON stream
        with redirect_stdout_to_stderr():
            result = invoke_tool(name, arguments)
            
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": result
        }
        
    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {}
        }
        
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {
            "code": -32601,
            "message": f"Method {method} not found"
        }
    }

def main():
    # Make sure we add apps/api directory to sys.path to resolve imports properly if run from root
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    sys.stderr.write("BugBountyHunter MCP Stdio Server Started.\n")
    sys.stderr.flush()
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
                
            request = json.loads(line)
            response = handle_request(request)
            
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                
        except json.JSONDecodeError:
            sys.stderr.write("Error: Failed to parse incoming message as valid JSON.\n")
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"Exception in stdio read loop: {str(e)}\n{traceback.format_exc()}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
