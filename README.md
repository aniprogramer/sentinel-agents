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
┌─────────────────┐
│   FastAPI App   │  (main.py - REST API)
└────────┬────────┘
         │
    ┌────▼─────┐
    │ AI Brain │  (Kimi AI Integration)
    └────┬─────┘
         │
┌────────▼──────────────────┐
│    Orchestrator.py         │  (Master Security Loop)
├───────────────────────────┤
│ 1. AST Analyzer           │
│ 2. Auditor Agent          │
│ 3. Red Team Agent         │
│ 4. Sandbox Runner         │
│ 5. Blue Team Agent        │
│ 6. Verifier Agent         │
└───────────────────────────┘
         │
    ┌────▼──────────┐
    │ Docker Sandbox │
    └───────────────┘
```

## Components

### Core Modules

#### `main.py` - FastAPI REST API
- **Endpoints:**
  - `POST /analyze` - Code vulnerability analysis
  - `POST /generate_poe` - Generate Proof of Exploitation
  - `POST /generate_patch` - Generate security patches
  - `POST /verify` - Verify patch effectiveness

#### `orchestrator.py` - Security Pipeline
The master autonomous pipeline that coordinates all security agents:
- **Member 1:** AST Context Extraction via mock function
- **Member 2:** Real API calls to `/analyze` endpoint for vulnerability scanning
- **Red Team:** Exploit generation and logic analysis (mock)
- **Blue Team:** Patch generation (mock)
- **Verifier:** Patch validation and re-testing
- **Repository Scanner:** Full directory scanning with glob pattern matching
- Integrates with FastAPI backend via HTTP requests
- Error handling for API failures with status code checks
- Support for multiple file types (.py, .js, .env, .json)

#### `sandbox_runner.py` - Docker Execution Engine
- Executes exploits in isolated Docker containers
- Network-disabled and resource-limited (128MB)
- 15-second timeout protection
- Execution result caching (prevents redundant runs)
- Automatic cleanup

#### `core/ai_brain.py` - AI Integration
- Kimi AI (Moonshot) API integration
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

### Test Files (`test_files/`)

Sample vulnerable code for testing the security pipeline:

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
   pip install fastapi uvicorn docker python-dotenv requests tree-sitter tree-sitter-python pydantic
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
├── orchestrator.py            # Master security pipeline
├── sandbox_runner.py          # Docker execution engine
├── .env                       # Environment variables (API keys)
├── Dockerfile.sandbox         # Sandbox container definition
├── core/
│   └── ai_brain.py           # Kimi AI integration
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

| Variable | Description | Required |
|----------|-------------|----------|
| `API_KEY` | Kimi AI (Moonshot) API key | Yes |

## Development

### Adding New Vulnerability Detection

1. Update AST extractors in `ast_engine/`
2. Add detection patterns to analysis prompt
3. Update response schemas in `main.py`

### Extending AI Agents

Modify prompt templates in `main.py`:
```python
PROMPTS = {
    "analyze": "...",
    "generate_poe": "...",
    "generate_patch": "...",
    "verify": "..."
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
- [ ] Distributed sandbox execution
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

### Added
- `sinks_extractor.py` - Detects dangerous function calls (eval, exec, os.system, subprocess, pickle, SQL cursors)
- `.env` file - Environment configuration for API keys
- `venv/` folder - Python virtual environment
- `test_files/` directory - Sample vulnerable code for testing
  - `sample_code_v2.py` - Simple test code with variables
  - `sample_vulnerable.py` - Complex vulnerability examples (SQLi, RCE, pickle deserialization)
- **Repository scanning** - `scan_entire_repository()` function with glob pattern matching
- **Error handling** - API failure detection with HTTP status code validation
- **Multi-file support** - Scans .py, .js, .json, and .env files

### Updated
- Orchestrator now makes real HTTP requests to `/analyze` endpoint
- Added JSON pretty-printing for auditor results
- Improved severity-based alerting (HIGH/CRITICAL flagging)
- AST engine components expanded with sinks detection
- Project structure documentation updated
- Removed persistent execution cache file
