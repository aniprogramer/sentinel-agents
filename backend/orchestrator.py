import os
import time
from sandbox_runner import run_exploit_in_sandbox
import requests
import json


def mock_ast_analyzer(code):
    return {"functions": ["login"], "sinks": ["execute_sql"]}


def call_auditor_api(raw_code, ast_json):
    """Hits the Member 2 FastAPI endpoint."""
    url = "http://127.0.0.1:8000/analyze"
    payload = {
        "raw_code": raw_code,
        "ast_json": ast_json
    }
    response = requests.post(url, json=payload)
    
    # The Senior Engineer check: Did the server actually succeed?
    if response.status_code != 200:
        print(f"\n❌ [FATAL] FastAPI Server crashed with status {response.status_code}!")
        print(f"Server Logs: {response.text}")
        exit(1)
        
    return response.json()



def mock_red_team(code):
    # This is a fake Python exploit the AI *would* generate
    return """
import os
import requests
print('--- RED TEAM EXPLOIT EXECUTING ---')
print('Simulating SQL Injection payload...')
print('Bypass successful. Data extracted.')
"""

def mock_blue_team(code, failure_logs):
    return "# PATCHED CODE\n# Added parameterized queries to prevent SQLi\nprint('Secure App Running')"

def apply_patch(target_file, patched_code):
    with open(target_file, "w") as f:
        f.write(patched_code)
    print(f"[*] Patch applied to {target_file}")

# ==========================================
# 🚀 THE MASTER SECURITY LOOP (YOUR JOB)
# ==========================================
def run_autonomous_pipeline(target_file_path):
    print("\n" + "="*50)
    print(f"🛡️ VEXSTORM AUTONOMOUS ENGINE STARTED")
    print(f"🎯 Target: {target_file_path}")
    print("="*50)

    # 1. READ FILE
    with open(target_file_path, "r") as f:
        original_code = f.read()

    # 2. AST SLICER (Member 1)
    print("\n[⚙️ MEMBER 1] Extracting AST Context...")
    ast_context = mock_ast_analyzer(original_code)
    time.sleep(1) # Simulating processing time

    # 3. AUDITOR (Member 2 - Checkpoint 1)
    print("[🔍 AUDITOR] Scanning for surface vulnerabilities...")
    auditor_results = call_auditor_api(original_code, ast_context)
    print(f"\n[🚨 AUDITOR REPORT]\n{json.dumps(auditor_results, indent=2)}")
    time.sleep(1)

    # 4. RED TEAM (Member 2 - Checkpoint 2)
    print("[💀 RED TEAM] Analyzing logic & generating PoE script...")
    poe_script = mock_red_team(original_code)
    time.sleep(1)

    # 5. SANDBOX EXECUTION (Your Engine)
    print("\n[🐳 ORCHESTRATOR] Sending exploit to Docker Sandbox...")
    result_run_1 = run_exploit_in_sandbox(poe_script, target_file_path)

    print("\n" + "-"*30)
    print(f"🛑 RED TEAM EXPLOIT SUCCESS: {result_run_1['success']}")
    print(f"📜 LOGS:\n{result_run_1['logs'].strip()}")
    print("-"*30)

    # 6. VERIFICATION & PATCHING (Checkpoint 3 & 4)
    if result_run_1['success']:
        print("\n[🛡️ BLUE TEAM] Vulnerability confirmed! Generating patch...")
        patched_code = mock_blue_team(original_code, result_run_1['logs'])
        time.sleep(1)

        print("[⚖️ VERIFIER] Applying patch and re-testing in Sandbox...")
        apply_patch(target_file_path, patched_code)

        # Re-run the EXACT SAME exploit against the patched code
        result_run_2 = run_exploit_in_sandbox(poe_script, target_file_path)

        if not result_run_2['success'] or "Bypass successful" not in result_run_2['logs']:
            print("\n✅ [VERDICT] Patch Verified! Exploit neutralized.")
        else:
            print("\n❌ [VERDICT] Patch Failed. Exploit still works.")

        # Restore original code for the next test run
        apply_patch(target_file_path, original_code)
    else:
        print("\n✅ [VERDICT] Code is secure against this attack vector.")

    print("\n🏁 PIPELINE COMPLETE.\n")

import glob

def scan_entire_repository(repo_path):
    print("\n" + "="*50)
    print(f"📂 INITIATING FULL REPOSITORY SCAN: {repo_path}")
    print("="*50)
    
    # We want to scan Python files, JS files, and especially .env files
    target_extensions = ['*.py', '*.js', '.env*', '*.json']
    files_to_scan = []
    
    for ext in target_extensions:
        # Recursively find all matching files in the directory
        search_pattern = os.path.join(repo_path, '**', ext)
        files_to_scan.extend(glob.glob(search_pattern, recursive=True))

    if not files_to_scan:
        print("❌ No scannable files found in directory.")
        return

    print(f"🔍 Found {len(files_to_scan)} files to analyze. Starting Auditor...\n")

    for file_path in files_to_scan:
        print(f"\n📄 Analyzing: {os.path.basename(file_path)}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        
        # If it's a .env file, we don't need AST, just raw text analysis
        if ".env" in file_path:
            ast_context = {"type": "configuration_file", "warning": "Contains environment variables"}
        else:
            ast_context = mock_ast_analyzer(file_content) 

        # Call your Gemini Checkpoint 1
        auditor_results = call_auditor_api(file_content, ast_context)
        
        # If the AI finds something bad, print it!
        if auditor_results.get("severity_score", "").upper() in ["HIGH", "CRITICAL"]:
            print(f"🚨 [ALERT] High/Critical vulnerabilities found in {file_path}!")
            print(json.dumps(auditor_results, indent=2))
            
            # Here is where you would trigger the Red Team Sandbox loop
            # run_autonomous_pipeline(file_path) 
        else:
            print(f"✅ Clean: No major surface threats found.")

if __name__ == "__main__":
    # Point it at the dummy file you created earlier
    target_folder = os.path.abspath(os.path.join("..", "target_code"))
    scan_entire_repository(target_folder)
