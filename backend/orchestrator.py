import os
import time
from sandbox_runner import run_exploit_in_sandbox
import requests
import json
import glob

# ==========================================
# 🛑 MOCKS (Blue Team is next to be replaced!)
# ==========================================
def mock_ast_analyzer(code):
    return {"functions": ["login"], "sinks": ["execute_sql"]}

def mock_blue_team(code, failure_logs):
    return "# PATCHED CODE\n# Added parameterized queries to prevent SQLi\nprint('Secure App Running')"

def apply_patch(target_file, patched_code):
    with open(target_file, "w") as f:
        f.write(patched_code)
    print(f"[*] Patch applied to {target_file}")

# ==========================================
# 🌐 API CONNECTORS
# ==========================================
def call_auditor_api(raw_code, ast_json):
    """Hits the Checkpoint 1 FastAPI endpoint."""
    url = "http://127.0.0.1:8000/analyze"
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
    """Hits the Checkpoint 2 FastAPI endpoint."""
    url = "http://127.0.0.1:8000/generate_poe"
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


# ==========================================
# 🚀 THE MASTER SECURITY LOOP
# ==========================================
def run_autonomous_pipeline(target_file_path, existing_auditor_results=None):
    print("\n" + "="*50)
    print(f"🛡️ VEXSTORM AUTONOMOUS ENGINE STARTED")
    print(f"🎯 Target: {target_file_path}")
    print("="*50)

    with open(target_file_path, "r", encoding="utf-8") as f:
        original_code = f.read()

    # If we already scanned it in the directory loop, skip the scan. Otherwise, scan it.
    if existing_auditor_results:
        auditor_results = existing_auditor_results
    else:
        print("\n[⚙️ MEMBER 1] Extracting AST Context...")
        ast_context = mock_ast_analyzer(original_code)
        time.sleep(1)

        print("[🔍 AUDITOR] Scanning for surface vulnerabilities...")
        auditor_results = call_auditor_api(original_code, ast_context)
        print(f"\n[🚨 AUDITOR REPORT]\n{json.dumps(auditor_results, indent=2)}")
        time.sleep(1)

    # 4. RED TEAM (Live AI Checkpoint 2)
    # 4. RED TEAM (Live AI Checkpoint 2)
    print("\n[💀 RED TEAM] Analyzing logic & generating custom PoE script...")
    
    # Grab the top finding to feed to the Red Team
    vuln_desc = "Unknown vulnerability"
    if auditor_results.get("red_team_findings"):
        vuln_desc = auditor_results["red_team_findings"][0]

    # The AI writes the exploit script dynamically!
    red_team_results = call_red_team_api(
        vulnerability_description=vuln_desc,
        vulnerable_code=original_code
    )
    poe_script = red_team_results.get("exploit_script", "")
    print(f"[*] AI generated a {len(poe_script)} character Python exploit script.")
    
    # 👇 ADD THESE TWO LINES RIGHT HERE 👇
    print("\n[🔍 EXPLOIT PAYLOAD REVEALED]")
    print(poe_script)
    time.sleep(1)

    # 5. SANDBOX EXECUTION
    print("\n[🐳 ORCHESTRATOR] Sending generated exploit to Docker Sandbox...")
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

        result_run_2 = run_exploit_in_sandbox(poe_script, target_file_path)

        if not result_run_2['success'] or "Bypass successful" not in result_run_2['logs']:
            print("\n✅ [VERDICT] Patch Verified! Exploit neutralized.")
        else:
            print("\n❌ [VERDICT] Patch Failed. Exploit still works.")

        apply_patch(target_file_path, original_code)
    else:
        print("\n✅ [VERDICT] Code is secure against this attack vector.")

    print("\n🏁 PIPELINE COMPLETE.\n")


# ==========================================
# 📂 DIRECTORY SCANNER
# ==========================================
def scan_entire_repository(repo_path):
    print("\n" + "="*50)
    print(f"📂 INITIATING FULL REPOSITORY SCAN: {repo_path}")
    print("="*50)
    
    target_extensions = ['*.py', '*.js', '.env*', '*.json']
    files_to_scan = []
    
    for ext in target_extensions:
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
        
        if ".env" in file_path:
            ast_context = {"type": "configuration_file", "warning": "Contains environment variables"}
        else:
            ast_context = mock_ast_analyzer(file_content) 

        auditor_results = call_auditor_api(file_content, ast_context)
        
        if auditor_results.get("severity_score", "").upper() in ["HIGH", "CRITICAL"]:
            print(f"🚨 [ALERT] High/Critical vulnerabilities found in {os.path.basename(file_path)}!")
            print(json.dumps(auditor_results, indent=2))
            
            # If it is a Python file with a high severity flaw, send it to the Sandbox!
            if file_path.endswith('.py'):
                print(f"\n[🚀] Triggering Autonomous Sandbox Pipeline for {os.path.basename(file_path)}...")
                run_autonomous_pipeline(file_path, existing_auditor_results=auditor_results)
        else:
            print(f"✅ Clean: No major surface threats found.")

if __name__ == "__main__":
    target_folder = os.path.abspath(os.path.join("..", "target_code"))
    scan_entire_repository(target_folder)