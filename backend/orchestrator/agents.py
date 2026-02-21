"""
Agent API Connectors

This module contains all the API connectors for the security agents:
- Auditor (Checkpoint 1)
- Red Team (Checkpoint 2)
- Blue Team (Checkpoint 3/4)
"""

import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


def call_auditor_api(raw_code, ast_json):
    """
    Hits the Checkpoint 1 FastAPI endpoint for vulnerability analysis.

    Args:
        raw_code: The source code to analyze
        ast_json: The AST context extracted from the code

    Returns:
        dict: Auditor findings including severity score and vulnerabilities
    """
    url = f"{API_URL}/analyze"
    payload = {
        "raw_code": raw_code,
        "ast_json": ast_json
    }
    response = requests.post(url, json=payload)

    if response.status_code != 200:
        print(f"\n❌ [FATAL] Auditor API crashed with status {response.status_code}!")
        print(f"Server Logs: {response.text}")
        exit(1)

    return response.json()


def call_red_team_api(vulnerability_description, vulnerable_code):
    """
    Hits the Checkpoint 2 FastAPI endpoint for exploit generation.

    Args:
        vulnerability_description: Description of the vulnerability found
        vulnerable_code: The vulnerable code to exploit

    Returns:
        dict: Generated exploit script and execution instructions
    """
    url = f"{API_URL}/generate_poe"
    payload = {
        "vulnerability_description": vulnerability_description,
        "vulnerable_code": vulnerable_code
    }
    response = requests.post(url, json=payload)

    if response.status_code != 200:
        print(f"\n❌ [FATAL] Red Team API crashed with status {response.status_code}!")
        print(f"Server Logs: {response.text}")
        exit(1)

    return response.json()


def call_blue_team_api(vulnerable_code, vulnerability_description, failure_logs):
    """
    Hits the Checkpoint 3/4 FastAPI endpoint for patch generation.

    Args:
        vulnerable_code: The original vulnerable code
        vulnerability_description: Description of the vulnerability
        failure_logs: Logs from the exploit execution

    Returns:
        dict: Generated patch code and security explanation
    """
    url = f"{API_URL}/generate_patch"
    payload = {
        "vulnerable_code": vulnerable_code,
        "vulnerability": vulnerability_description,
        "failure_logs": failure_logs
    }
    response = requests.post(url, json=payload)

    if response.status_code != 200:
        print(f"\n❌ [FATAL] Blue Team API crashed with status {response.status_code}!")
        print(f"Server Logs: {response.text}")
        exit(1)

    return response.json()


def call_verifier(poe_script, target_file_path):
    """
    Executes the exploit script in a sandboxed environment to verify vulnerabilities.

    Args:
        poe_script: The exploit script to execute
        target_file_path: Path to the target vulnerable file

    Returns:
        dict: Execution results with success status and logs
    """
    from sandbox_runner import run_exploit_in_sandbox
    return run_exploit_in_sandbox(poe_script, target_file_path)
