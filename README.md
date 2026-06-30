# 🎯 BugBountyHunter

> **An Autonomous AI Security Agent that dynamically scans codebases, detects vulnerabilities, and executes containerized self-refining code repairs.**

Built for the next generation of automated software security, **BugBountyHunter** acts as an autonomous agent that not only scans your code for linter errors, styling violations, and security CVEs, but goes further by creating and validating patches in a sandboxed runner, refining them recursively based on compiler logs, and automatically opening GitHub Pull Requests with detailed unified diffs.

---

## 🌟 Premium Features

### 1. Stepped Self-Refinement validation
If a patch candidate initially breaks compile tests, typecheck checks, or syntax rules, **BugBountyHunter** triggers a **reflection loop (up to 3 validation attempts)**. It feeds back the exact compiler error stdout/stderr into the LLM context to dynamically correct its own patches.

### 2. Multi-Scanner Core Abstraction
Support for Python and JavaScript/TypeScript codebases with out-of-the-box linter/scanner tools:
* **Ruff** & **mypy** for Python static linting and type checking.
* **Bandit** for detecting Python security vulnerabilities.
* **ESLint** for JavaScript/TypeScript syntax checks.

### 3. Iridescent Glassmorphic Portal UI
A stunning landing and dashboard UI designed with obsidian glass overlays, real-time scanning tables, slide-in details drawers, and **pure CSS animated floating glass orbs** representing the fluid nature of agentic AI.

### 4. Sandbox Validation Runner
Integrations for isolated execution using Docker container sandboxes or local subprocess testing to ensure generated patches are functional before they are staged.

---

## 📂 Project Architecture

```text
BUG APP/
├── apps/
│   └── api/                  # Python FastAPI Backend & Dashboard
│       ├── app/
│       │   ├── agents/       # Agent configurations (scan, repair, validation, PR)
│       │   ├── api/          # Route handlers & dashboard HTML templates
│       │   ├── core/         # DB engine setup & configurations
│       │   ├── models/       # SQLite / PostgreSQL database schemas
│       │   ├── services/     # GitHub connection, reports compilation, & LLM integrations
│       │   └── workers/      # Celery task schedules & synchronous run engines
│       ├── requirements.txt  # Python package configurations (fastapi, uvicorn, celery, docker)
│       └── .env              # Local environment credentials (DATABASE_URL, GITHUB_TOKEN)
├── docker/
│   └── docker-compose.yml    # Celery Redis broker configuration service
├── scratch/                  # Temporary clone directory for scanning/verifying codebases
└── README.md                 # Project summary & Hackathon presentation documentation
```

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
* Python 3.10+
* Docker (for sandboxed validation)
* Redis (optional, falls back to Celery Eager SQLite if Redis is offline)

### 2. Launching the Backend API & Dashboard

1. Navigate to the `apps/api` directory:
   ```bash
   cd apps/api
   ```
2. Activate your virtual environment and install the required libraries:
   ```bash
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Start the FastAPI dashboard server:
   ```bash
   python -m uvicorn app.main:app --port 8000 --host 127.0.0.1
   ```
4. Open your browser and navigate to the premium dashboard portal:
   ```
   http://127.0.0.1:8000/dashboard
   ```

---

## 🛠️ Testing the Agent Flow

Enter any GitHub URL or test repository directory (e.g. `c:/Users/AGOEL/OneDrive/Desktop/BUG APP/scratch/test-python-repo` which contains an intentional `undefined_variable` bug in `calculator.py`) in the **"Scan & Auto-Repair New Repository"** input, then click **"Initiate Bug Hunt"**.

Observe:
1. The agent detecting the python stack and triggering Ruff.
2. The initial patch failing validation due to the undefined variable.
3. The self-refinement logs running recursively up to 3 times to fix compilation syntax issues.
4. The scan table updating dynamically to status `completed`.
5. Opening the **"View Analysis"** details panel to display collapsible linter logs, attempts, patches, and detailed outcomes.

---

## 🤖 Interoperability & Integration (MCP Server & Gemini)

### 1. Google Gemini Support
To run the agent using Gemini models (e.g., `gemini-2.5-flash`):
1. Set the environment variable:
   ```bash
   # Windows Command Prompt
   set GEMINI_API_KEY=your_gemini_api_key_here
   # Windows PowerShell
   $env:GEMINI_API_KEY="your_gemini_api_key_here"
   ```
2. (Optional) Customize the target model:
   ```bash
   set GEMINI_MODEL=gemini-2.5-flash
   ```
3. If `GEMINI_API_KEY` is not present, the agent automatically falls back to `OPENAI_API_KEY` or Mock local developer fallback mode.

### 2. Stdio-based MCP Server for Claude Desktop/Cursor
In addition to the HTTP endpoints, **BugBountyHunter** acts as a fully compliant, stdio-based Model Context Protocol (MCP) server. You can integrate this agent directly into tools like Claude Desktop or Cursor to allow them to scan, repair, and validate your codebases.

#### Claude Desktop Configuration
Add the following to your `claude_desktop_config.json` (usually located at `%APPDATA%\Claude\claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "bug-bounty-hunter": {
      "command": "python",
      "args": ["-m", "app.mcp_server"],
      "env": {
        "GEMINI_API_KEY": "your_gemini_api_key_here",
        "GITHUB_TOKEN": "your_github_token_here"
      },
      "cwd": "c:/Users/AGOEL/OneDrive/Desktop/BugBountyHunter.ai/apps/api"
    }
  }
}
```
Now, you can interact with `BugBountyHunter` from Claude Desktop, asking it to clone repositories, repair issues, or validate code.

