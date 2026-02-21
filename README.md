# Sentinel Agents Security Engine 🛡️

An autonomous AI-powered security testing and vulnerability remediation platform that combines static analysis, exploit generation, sandboxed execution, and automated patching.

## Overview

Sentinel Agents is a multi-agent security system that automatically:

1. **Analyzes** code using AST (Abstract Syntax Tree) parsing
2. **Audits** for surface-level vulnerabilities
3. **Generates** exploits (Proof of Exploitation scripts)
4. **Executes** exploits in isolated Docker sandboxes
5. **Patches** vulnerabilities automatically
6. **Verifies** patch effectiveness by re-running exploits

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       IMPROVED AUTONOMOUS SECURITY FLOW                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1-2: CONTEXTUAL INGESTION                                              │
│ • Slicer: Breaks file into logical blocks.                                  │
│ • Context Map: Stores global variables & function relations.                │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 3-5: PARALLEL DISCOVERY (Checkpoint 1 & 2)                             │
│ ┌───────────────────────────┐         ┌───────────────────────────────────┐ │
│ │ Auditor (Surface Scan)    │   AND   │ 	Red Team (Deep Logic Scan)      │ │
│ │ Secrets & CI/CD Pipelines │         │ 	Reachability & Taint Analysis   │ │
│ └─────────────┬─────────────┘         └─────────────────┬─────────────────┘ │
└───────────────┼─────────────────────────────────────────┼───────────────────┘
                │                                         │
                ▼                                         ▼
┌──────────────────────────────┐        ┌─────────────────────────────────────┐
│ STEP 4: INSTANT INTIMATION   │        │ STEP 6-7: ADVERSARIAL VERIFICATION  │
│ • Hardcoded fixes for leaks. │        │ • PoE Script Generation (Shell).    │
│                              │        │ • ISOLATED DOCKER EXECUTION.        |
└──────────────────────────────┘        └─────────────────┬───────────────────┘
                                                          │
                                            ┌─────────────┴─────────────┐
                                            ▼                           ▼
                               ┌──────────────────────────┐  ┌───────────────────────┐
                               │ STEP 8: BLUE TEAM        │  │ STEP 9: VERIFIER      │
                               │ (Checkpoint 3)           │  │ (Checkpoint 4)        │
                               │ • Generate Patch based   │  │ • Runs PoE vs Patch.  │
                               │   on Failure Logs.       │  │ • Feedback Critique.  │
                               └────────────┬─────────────┘  └──────────────┬────────┘
                                            │                               │
                                            └─────CRITIQUE LOOP (Max 3)─────┘
                                                          │
                                                          ▼
                                         ┌───────────────────────────────────┐
                                         │ FINAL OUTPUT: Verified "Thinking" │
                                         │ Report + Patch + Verified PoE.    │
                                         └───────────────────────────────────┘
```

## Components

### Core Modules

#### `main.py` - FastAPI REST API

- **Endpoints:**
  - `POST /analyze` - Code vulnerability analysis
  - `POST /generate_poe` - Generate Proof of Exploitation
  - `POST /generate_patch` - Generate security patches
  - `POST /verify` - Verify patch effectiveness

#### `orchestrator/` - Modular Security Pipeline Package

The orchestrator has been refactored into a clean, modular package structure for better maintainability and readability:

**Package Structure:**
- **`agents.py`** - All agent API connectors (Auditor, Red Team, Blue Team, Verifier)
- **`pipeline.py`** - Main autonomous security pipeline execution logic
- **`scanner.py`** - Repository scanning functionality with multi-file support
- **`utils.py`** - Utility functions (patching, AST extraction, validation helpers)
- **`__init__.py`** - Package initialization and exports

**Key Features:**
- ✅ **Real AST Analysis:** Uses the actual AST analyzer (no mocks!)
- ✅ **Live API Integration:** All agents call real FastAPI endpoints
- ✅ **Modular Design:** Each file has single, clear responsibility
- ✅ **Error Handling:** Comprehensive status code validation
- ✅ **Multi-File Support:** Scans .py, .js, .json, and .env files
- ✅ **Iterative Patching:** 3-attempt loop with AI feedback learning
- ✅ **Repository Scanning:** Recursive directory traversal with glob patterns

#### `sandbox_runner.py` - Docker Execution Engine

- Executes exploits in isolated Docker containers
- Network-disabled and resource-limited (128MB)
- 15-second timeout protection
- Execution result caching (prevents redundant runs)
- Automatic cleanup

#### `core/ai_brain.py` - AI Integration

- Gemini API integration
- Structured JSON responses
- Schema-validated output
- Temperature-controlled generation

### AST Engine (`ast_engine/`)

Static analysis toolkit using Tree-sitter:

- `analyzer.py` - Core AST parser and traversal
- `imports_extractor.py` - Import statement analysis
- `functions_extractor.py` - Function definition extraction
- `classes_extractor.py` - Class structure analysis
- `globals_extractor.py` - Global variable detection
- `inputs_extractor.py` - User input sink identification
- `sinks_extractor.py` - Dangerous function call detection (eval, exec, os.system, etc.)
- `parser_setup.py` - Tree-sitter configuration
- `helpers.py` - Utility functions for AST processing

### Orchestrator Package (`orchestrator/`)

Modular security pipeline package with clean separation of concerns:

**`agents.py`** - Agent API Connectors
- `call_auditor_api()` - Checkpoint 1: Vulnerability analysis
- `call_red_team_api()` - Checkpoint 2: Exploit generation  
- `call_blue_team_api()` - Checkpoint 3/4: Patch generation
- `call_verifier()` - Sandbox execution wrapper
- Comprehensive error handling with HTTP status validation

**`pipeline.py`** - Security Pipeline Logic
- `run_autonomous_pipeline()` - Main pipeline orchestration with 5 phases:
  1. Analysis & Detection (AST + Auditor)
  2. AND Gate Logic (exploitability check)
  3. Exploitation (Red Team PoE generation)
  4. Verification (Sandbox execution)
  5. Patching & Iterative Verification (up to 3 attempts)
- `_run_patch_verification_loop()` - Iterative patch testing with AI feedback

**`scanner.py`** - Repository Scanner
- `scan_entire_repository()` - Multi-file vulnerability scanning
- `_gather_scannable_files()` - Recursive file discovery with glob patterns
- `_scan_single_file()` - Individual file analysis with severity filtering

**`utils.py`** - Utility Functions
- `apply_patch()` - Apply security patches to files
- `extract_ast_context()` - Real AST extraction using analyzer.py
- `get_vulnerability_description()` - Extract primary vulnerability info
- `is_exploitable()` - Check if vulnerabilities are exploitable
- `is_critical_finding()` - Filter HIGH/CRITICAL severity issues

### Test Files (`test_files/`)

Sample vulnerable code for testing the security pipeline:

- `ast_test.py` - AST analyzer validation tests
- `sample_code_v2.py` - Simple Python code with variable assignments for basic testing
- `sample_vulnerable.py` - Comprehensive vulnerability examples including:
  - SQL Injection via string formatting
  - Remote Code Execution (os.system, exec, eval)
  - Command Injection (subprocess.run)
  - Pickle deserialization vulnerabilities
  - User input from multiple sources (request, input(), sys.argv)
  - Dangerous operations in both class methods and standalone functions

## Setup

### Prerequisites

- Python 3.10+
- Docker
- Kimi AI API Key (Moonshot)

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd sentinel-agents/backend
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   Or manually install core packages:
   ```bash
   pip install fastapi uvicorn docker python-dotenv requests tree-sitter tree-sitter-python pydantic openai google-generativeai
   ```

3. **Configure environment:**

   ```bash
   echo "API_KEY=your_kimi_api_key_here" > .env
   ```

4. **Build Docker sandbox:**
   ```bash
   docker build -t sentinel_sandbox:latest -f Dockerfile.sandbox .
   ```

### Running the Application

**Start FastAPI Server:**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Run Autonomous Pipeline:**

```bash
python orchestrator.py
```

**Scan Entire Repository:**
The orchestrator now includes a `scan_entire_repository()` function that:

- Recursively scans directories for Python, JavaScript, JSON, and .env files
- Automatically detects configuration files
- Calls the auditor API for each file
- Flags HIGH/CRITICAL severity findings

**Test Sandbox (standalone):**

```bash
python sandbox_runner.py
```

## API Usage

### Analyze Code

```bash
POST /analyze
{
  "raw_code": "def login(user, pwd): execute_sql(f\"SELECT * FROM users WHERE name='{user}'\"); ",
  "ast_json": {...}
}
```

**Response:**

```json
{
  "auditor_findings": ["SQL Injection detected"],
  "red_team_findings": ["String interpolation in SQL query"],
  "severity_score": "CRITICAL",
  "attack_surface_summary": "Direct user input to database query"
}
```

### Generate Exploit

```bash
POST /generate_poe
{
  "vulnerability_description": "SQL Injection in login function",
  "vulnerable_code": "..."
}
```

### Generate Patch

```bash
POST /generate_patch
{
  "vulnerability": "SQL Injection",
  "failure_logs": "..."
}
```

### Verify Patch

```bash
POST /verify
{
  "original_vulnerability": "SQL Injection",
  "patch_result": "...",
  "execution_logs": "..."
}
```

## Security Features

### Docker Sandbox Isolation

- **Network Disabled:** No external communication
- **Memory Limited:** 128MB max
- **Timeout Protection:** 15-second execution limit
- **Read-Only Mounts:** Target code cannot be modified
- **Auto-Remove:** Containers cleaned up after execution

### Execution Caching

Prevents redundant Docker runs by caching results based on SHA-256 hash of exploit scripts. Cache is stored in memory during runtime and managed by the sandbox runner.

### Attack Surface Analysis

AST engine identifies:

- User input sources (request parameters, sys.argv, input())
- Database query sinks (cursor.execute)
- File I/O operations
- Network calls
- Command execution points (os.system, subprocess)
- Dangerous functions (eval, exec, pickle.loads)

## Project Structure

```
backend/
├── main.py                    # FastAPI application
├── orchestrator.py            # Main entry point (imports from package)
├── sandbox_runner.py          # Docker execution engine
├── requirements.txt           # Python dependencies
├── execution_cache.json       # Execution result cache
├── .env                       # Environment variables (API keys)
├── Dockerfile.sandbox         # Sandbox container definition
├── core/
│   └── ai_brain.py           # Kimi AI integration
├── orchestrator/              # 🆕 Modular orchestrator package
│   ├── __init__.py           # Package initialization
│   ├── agents.py             # Agent API connectors
│   ├── pipeline.py           # Main security pipeline logic
│   ├── scanner.py            # Repository scanner
│   └── utils.py              # Utility functions
├── ast_engine/
│   ├── __init__.py
│   ├── analyzer.py           # Core AST parser
│   ├── imports_extractor.py  # Import statement extraction
│   ├── functions_extractor.py # Function definition extraction
│   ├── classes_extractor.py   # Class structure extraction
│   ├── globals_extractor.py   # Global variable detection
│   ├── inputs_extractor.py    # User input source detection
│   ├── sinks_extractor.py     # Dangerous function detection
│   ├── parser_setup.py        # Tree-sitter setup
│   └── helpers.py             # AST utility functions
├── temp/                      # Temporary exploit scripts
├── test_files/                # Sample vulnerable code for testing
│   ├── ast_test.py           # AST analysis test file
│   ├── sample_code_v2.py     # Simple test code
│   └── sample_vulnerable.py   # Complex vulnerability examples
└── venv/                      # Python virtual environment
```

## Workflow Example

### Single File Analysis

1. **Submit vulnerable code** via `/analyze`
2. **AI analyzes** AST and identifies SQL injection
3. **Red Team generates** Python exploit script
4. **Sandbox executes** exploit → Confirms vulnerability
5. **Blue Team generates** patched code with parameterized queries
6. **Verifier applies patch** and re-runs exploit
7. **Exploit fails** → Patch verified ✅

### Repository Scanning

1. **Orchestrator scans** entire directory recursively
2. **Detects** .py, .js, .json, and .env files
3. **Analyzes each file** via FastAPI auditor endpoint
4. **Flags critical findings** (HIGH/CRITICAL severity)
5. **Optionally triggers** full exploit pipeline for vulnerable files

## Environment Variables

| Variable  | Description                | Required |
| --------- | -------------------------- | -------- |
| `API_KEY` | Kimi AI (Moonshot) API key | Yes      |

## Dependencies

The project uses a comprehensive set of dependencies documented in `requirements.txt`:

### Core Framework

- **FastAPI** (0.129.0) - Web framework for REST API
- **Uvicorn** (0.41.0) - ASGI server
- **Pydantic** (2.12.5) - Data validation using Python type annotations

### AST & Code Analysis

- **Tree-sitter** (0.25.2) - Incremental parsing library
- **Tree-sitter-Python** (0.25.0) - Python language binding

### Container & Orchestration

- **Docker** (7.1.0) - Container runtime integration

### AI Backends

- **OpenAI** (2.21.0) - OpenAI API integration
- **Google Generative AI** (0.8.6) - Google's generative AI models

### HTTP & Networking

- **Requests** (2.32.5) - HTTP library
- **httpx** (0.28.1) - Modern HTTP client
- **httpcore** (1.0.9) - Low-level HTTP client

### Configuration & Utilities

- **python-dotenv** (1.2.1) - Environment variable management
- **cryptography** (46.0.5) - Cryptographic recipes
- **tqdm** (4.67.3) - Progress bars

### Additional Tools
Multi-language Support:** Currently optimized for Python; JS/JSON analysis is basic
- **Timeout:** 15-second max execution per exploit
- **Dangerous Function Detection:** Limited to predefined list in sinks_extractor.py
- **Repository Scanning:** Pattern matching limited to common file extensions (.py, .js, .json, .env)
- **Patch Retry Limit:** Maximum 3 iterative patch attempts before requiring human intervention
- **Single Exploit per Vulnerability:** Generates one PoE script per vulnerability type
```bash
pip install -r requirements.txt
```
Multi-language support (JavaScript, Java, Go, C/C++)
- [ ] Distributed sandbox execution across multiple containers
- [ ] Web UI dashboard for real-time monitoring
- [ ] CI/CD pipeline integration (GitHub Actions, GitLab CI)
- [ ] Vulnerability database integration (CVE mapping)
- [ ] Machine learning-based pattern dete (e.g., add to `sinks_extractor.py`)
2. Add detection patterns to analysis prompt in `main.py`
3. Update response schemas in `main.py`
4. Test with new sample files in `test_files/`

### Extending AI Agents

**Modify API Connectors** (`orchestrator/agents.py`):
```python
def call_new_agent_api(parameters):
    url = "http://127.0.0.1:8000/new_endpoint"
    payload = {...}
    response = requests.post(url, json=payload)
    # Add error handling
    return response.json()
```

**Update Pipeline Logic** (`orchestrator/pipeline.py`):
```python
# Add new phase in run_autonomous_pipeline()
new_agent_results = call_new_agent_api(...)
```

**Modify Prompt Templates** (`main.py`):
```python
PROMPTS = {
    "analyze": "...",
    "generate_poe": "...",
    "generate_patch": "...",
    "verify": "...",
    "new_agent": "..."  # Add new prompt
}
```

### Working with the Modular Structure

The orchestrator package is designed for easy maintenance:

```python
# Import the main functions
from orchestrator import run_autonomous_pipeline, scan_entire_repository

# Or import specific components
from orchestrator.agents import call_auditor_api, call_red_team_api
from orchestrator.utils import extract_ast_context, is_critical_finding
from orchestrator.scanner import scan_entire_repository   "verify": "..."
}
```

## Known Limitations

- **Hybrid Mocking:** AST analyzer, Red Team, and Blue Team use mocks; Auditor uses real API
- **Multi-language Support:** Currently optimized for Python; JS/JSON analysis is basic
- **Timeout:** 15-second max execution per exploit
- **Cache Management:** Cache is runtime-only (no persistent storage)
- **Dangerous Function Detection:** Limited to predefined list in sinks_extractor.py
- **Repository Scanning:** Pattern matching limited to common file extensions

## Future Enhancements

- [ ] Real AST-based vulnerability detection (replace mock_ast_analyzer)
- [ ] Full AI agent integration for Red Team and Blue Team
- [ ] Multi-language support (JavaScript, Java, Go)
- [ ] Distributed sandbox ex2, 2026  
**Version:** 2.0 (Modular Architecture)
- [ ] Web UI dashboard
- [ ] CI/CD pipeline integration
- [ ] Vulnerability database integration
- [ ] Machine learning-based pattern detection
- [ ] Extended dangerous function library
- [ ] Configurable sink and source patterns

## Security Considerations

⚠️ **Warning:** This tool executes potentially malicious code. Always:

- Run in isolated environments
- Review generated exploits before execution
- Never execute on production systems
- Keep Docker sandbox images updated

## License

[Add your license here]

## Contributors

Built for hackathon - Sentinel Agents Team

## Support

For issues and questions, please open an issue in the repository.

---

**Last Updated:** February 21, 2026

## Recent Changes
v2.0 - Major Refactoring (February 22, 2026)

**🎉 Orchestrator Modularization**
- **Complete refactoring** of orchestrator.py into modular package structure
- Created `orchestrator/` package with 5 specialized modules:
  - `agents.py` - Agent API connectors (92 lines)
  - `pipeline.py` - Pipeline logic (122 lines)
  - `scanner.py` - Repository scanner (70 lines)
  - `utils.py` - Utility functions (60 lines)
  - `__init__.py` - Package exports (11 lines)
- **Removed all mocks** - All agents now use real API implementations
- **Real AST extraction** - Uses actual analyzer.py instead of mock functions
- **Improved readability** - Reduced from 270+ line monolith to small, focused modules
- Added comprehensive docstrings for all functions

**✨ New Features**
- `test_files/ast_test.py` - AST analyzer validation tests
- Iterative patch verification with AI feedback learning (max 3 attempts)
- Enhanced error messages with context-aware logging
- Better separation of concerns (agents, pipeline, scanner, utilities)

### v1.5 - Core Functionality (February 21, 2026)

**Added**
- `requirements.txt` - Complete Python dependency list (52 packages)
- `execution_cache.json` - Persistent execution result cache
- `sinks_extractor.py` - Dangerous function detection
- `.env` file - Environment configuration
- `venv/` folder - Python virtual environment
- `test_files/` directory with sample vulnerable code
- Repository scanning with glob pattern matching
- Error handling with HTTP status code validation
- Multi-file support (.py, .js, .json, .env)

**Updated**
- Orchestrator now makes real HTTP requests to all endpoints
- JSON pretty-printing for auditor results
- Severity-based alerting (HIGH/CRITICAL flagging)
- AST engine expanded with sinks detection
- Multiple AI backend support (Kimi, OpenAI, Google Generative AI)

### Dependencie
### Dependencies Highlights

- **Web Framework:** FastAPI 0.129.0, Uvicorn 0.41.0
- **Container:** Docker 7.1.0
- **AST Parsing:** Tree-sitter 0.25.2, Tree-sitter-Python 0.25.0
- **AI/ML:** OpenAI 2.21.0, Google Generative AI 0.8.6
- **Utilities:** Pydantic 2.12.5, python-dotenv 1.2.1, requests 2.32.5
