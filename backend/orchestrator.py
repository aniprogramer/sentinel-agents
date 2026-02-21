import os
import time
from sandbox_runner import run_exploit_in_sandbox

# ==========================================
# 🛑 MOCKS: We use these until Member 1 & 2 finish their code
# ==========================================
def mock_ast_analyzer(code):
    return {"functions": ["login"], "sinks": ["execute_sql"]}

def mock_auditor(code, ast):
    return {"status": "clean", "surface_vulns": []}

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
    auditor_results = mock_auditor(original_code, ast_context)
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

if __name__ == "__main__":
    # Point it at the dummy file you created earlier
    target_path = os.path.abspath(os.path.join("..", "target_code", "sample_vuln.py"))
    run_autonomous_pipeline(target_path)