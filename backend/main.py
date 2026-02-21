from fastapi import FastAPI
from core.ai_brain import call_ai
import subprocess

# Schemas moved to backend/schemas
from schemas.schemas import (
    AnalyzeInput,
    AnalyzeOutput,
    GeneratePOEInput,
    GeneratePOEOutput,
    GeneratePatchInput,
    GeneratePatchOutput,
    VerifyInput,
    VerifyOutput,
    WebhookPayload,
    OrchestratorInput,
)

# Orchestrator functions
from orchestrator import run_autonomous_pipeline, scan_entire_repository

app = FastAPI(title="Sentinel Agents Security Engine")


@app.post("/webhook/github")
def github_push_receiver(payload: WebhookPayload):
    """
    This is what GitHub hits when a developer pushes code.
    """
    # 1. Clone the repo to a temporary folder
    repo_name = payload.repository_url.split("/")[-1].replace(".git", "")
    clone_dir = f"../scans/{repo_name}_{payload.commit_hash[:7]}"

    # Run the git clone command (in a real app, use async/background tasks here)
    subprocess.run(["git", "clone", payload.repository_url, clone_dir])

    # 2. Trigger the Orchestrator Directory Scan on the new folder
    # Trigger a repository scan using the orchestrator
    try:
        scan_entire_repository(clone_dir)
    except Exception:
        # if scanning fails immediately, we still return accepted
        pass

    return {"status": "Scan Initiated", "target": clone_dir}


@app.post("/orchestrator")
def orchestrator_controller(input: OrchestratorInput):
    """Manage orchestrator operations: 'run' or 'scan'.

    - action: 'run' (default) will start the autonomous pipeline
    - action: 'scan' requires `target` path to scan
    """
    action = (input.action or "run").lower()
    if action == 'scan':
        if not input.target:
            return {"success": False, "message": "target required for scan"}
        try:
            scan_entire_repository(input.target)
            return {"success": True, "status": "scan_started", "target": input.target}
        except Exception as e:
            return {"success": False, "message": str(e)}

    # default: run the autonomous pipeline
    try:
        run_autonomous_pipeline(input.target)
        return {"success": True, "status": "orchestration_started"}
    except Exception as e:
        return {"success": False, "message": str(e)}

# ---------- Prompt Templates ----------

PROMPTS = {
    "analyze": """You are the Lead Security Auditor (Checkpoint 1).
Your task is to perform a surface-level Static Application Security Testing (SAST) scan on the provided code and AST.

Raw Code:
{raw_code}

AST Context:
{ast_json}

INSTRUCTIONS:
1. Identify immediate surface threats: hardcoded secrets, exposed API keys, dangerous sinks (eval, exec), and missing authentication.
2. Separate basic findings ("auditor_findings") from complex logic flaws that require an exploit ("red_team_findings" like SQLi or IDOR).
3. Do not generate code fixes yet.

Output strictly valid JSON matching the requested schema. Do not include markdown formatting like ```json.""",

    "generate_poe": """Given vulnerability description and vulnerable code:
Description: {vulnerability_description}
Code: {vulnerable_code}
Generate exploit script and execution instructions.""",

    "generate_patch": """Given vulnerability and failure logs:
Vulnerability: {vulnerability}
Logs: {failure_logs}
Generate patched code, explain the security principle, and provide explanation.""",

    "verify": """Verify patch effectiveness:
Original Vulnerability: {original_vulnerability}
Patch Result: {patch_result}
Execution Logs: {execution_logs}
Return exploit success (true/false), confidence level, and final verdict."""
}

# ---------- Routes ----------
@app.get("/")
def root():
	return {"message": "Welcome to Sentinel Agents Security Engine!"}

@app.post("/analyze", response_model=AnalyzeOutput)
def analyze(input: AnalyzeInput):
    prompt = PROMPTS["analyze"].format(**input.model_dump())
    schema = AnalyzeOutput.model_json_schema()
    return call_ai(prompt, schema)

@app.post("/generate_poe", response_model=GeneratePOEOutput)
def generate_poe(input: GeneratePOEInput):
    prompt = PROMPTS["generate_poe"].format(**input.model_dump())
    schema = GeneratePOEOutput.model_json_schema()
    return call_ai(prompt, schema)

@app.post("/generate_patch", response_model=GeneratePatchOutput)
def generate_patch(input: GeneratePatchInput):
    prompt = PROMPTS["generate_patch"].format(**input.model_dump())
    schema = GeneratePatchOutput.model_json_schema()
    return call_ai(prompt, schema)

@app.post("/verify", response_model=VerifyOutput)
def verify(input: VerifyInput):
    prompt = PROMPTS["verify"].format(**input.model_dump())
    schema = VerifyOutput.model_json_schema()
    return call_ai(prompt, schema)
