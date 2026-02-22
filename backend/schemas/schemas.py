from pydantic import BaseModel
from typing import List, Optional


class AnalyzeInput(BaseModel):
    raw_code: str
    ast_json: dict


class AnalyzeOutput(BaseModel):
    auditor_findings: List[str]
    red_team_findings: List[str]
    severity_score: str
    attack_surface_summary: str


class GeneratePOEInput(BaseModel):
    vulnerability_description: str
    vulnerable_code: str


class GeneratePOEOutput(BaseModel):
    exploit_script: str
    execution_instructions: str


class GeneratePatchInput(BaseModel):
    vulnerability: str
    failure_logs: str


class GeneratePatchOutput(BaseModel):
    patched_code: str
    security_principle: str
    explanation: str


class VerifyInput(BaseModel):
    original_vulnerability: str
    patch_result: str
    execution_logs: str


class VerifyOutput(BaseModel):
    exploit_success: bool
    confidence_level: str
    final_verdict: str


class WebhookPayload(BaseModel):
    repository_url: str
    branch: str
    commit_hash: str


class OrchestratorInput(BaseModel):
    action: Optional[str] = 'run'  # e.g., 'run' or 'scan'
    target: Optional[str] = None
