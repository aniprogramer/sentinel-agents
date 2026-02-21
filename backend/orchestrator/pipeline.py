"""
Autonomous Security Pipeline

This module contains the main security pipeline that orchestrates
the entire vulnerability detection, exploitation, and patching workflow.
"""

import time
import json
from .agents import (
    call_auditor_api,
    call_red_team_api,
    call_blue_team_api,
    call_verifier
)
from .utils import (
    apply_patch,
    extract_ast_context,
    get_vulnerability_description,
    is_exploitable
)


def run_autonomous_pipeline(target_file_path, existing_auditor_results=None):
    """
    Execute the complete autonomous security pipeline.
    
    This pipeline performs:
    1. AST extraction and code analysis
    2. Vulnerability scanning (Auditor)
    3. Exploit generation (Red Team)
    4. Sandbox execution (Verifier)
    5. Patch generation (Blue Team)
    6. Iterative patch verification
    
    Args:
        target_file_path: Path to the file to analyze
        existing_auditor_results: Optional pre-computed auditor results
    """
    print("\n" + "="*50)
    print(f"🛡️ VEXSTORM AUTONOMOUS ENGINE STARTED")
    print(f"🎯 Target: {target_file_path}")
    print("="*50)

    with open(target_file_path, "r", encoding="utf-8") as f:
        original_code = f.read()

    # ==========================================
    # PHASE 1: Analysis & Detection
    # ==========================================
    if existing_auditor_results:
        auditor_results = existing_auditor_results
    else:
        print("\n[⚙️ MEMBER 1] Extracting AST Context...")
        ast_context = extract_ast_context(original_code)
        time.sleep(1)

        print("[🔍 AUDITOR] Scanning for surface vulnerabilities...")
        auditor_results = call_auditor_api(original_code, ast_context)
        print(f"\n[🚨 AUDITOR REPORT]\n{json.dumps(auditor_results, indent=2)}")
        time.sleep(1)

    # ==========================================
    # PHASE 2: AND Gate Logic
    # ==========================================
    print("\n[🔀 AND GATE] Evaluating AST Context + Auditor Findings...")
    
    if not is_exploitable(auditor_results):
        print("❌ [🔀 AND GATE] No dynamically exploitable logic found. Halting Red Team execution.")
        print("\n🏁 PIPELINE COMPLETE.\n")
        return

    print("✅ [🔀 AND GATE] Exploitable logic confirmed. Triggering Red Team!")
    time.sleep(1)

    # ==========================================
    # PHASE 3: Exploitation
    # ==========================================
    print("\n[💀 RED TEAM] Analyzing logic & generating custom PoE script...")
    
    vuln_desc = get_vulnerability_description(auditor_results)
    red_team_results = call_red_team_api(
        vulnerability_description=vuln_desc,
        vulnerable_code=original_code
    )
    poe_script = red_team_results.get("exploit_script", "")
    print(f"[*] AI generated a {len(poe_script)} character Python exploit script.")
    
    print("\n[🔍 EXPLOIT PAYLOAD REVEALED]")
    print(poe_script)
    time.sleep(1)

    # ==========================================
    # PHASE 4: Verification
    # ==========================================
    print("\n[🐳 ORCHESTRATOR] Sending generated exploit to Docker Sandbox...")
    result_run_1 = call_verifier(poe_script, target_file_path)

    print("\n" + "-"*30)
    print(f"🛑 RED TEAM EXPLOIT SUCCESS: {result_run_1['success']}")
    print(f"📜 LOGS:\n{result_run_1['logs'].strip()}")
    print("-"*30)

    # ==========================================
    # PHASE 5: Patching & Iterative Verification
    # ==========================================
    if result_run_1['success']:
        _run_patch_verification_loop(
            original_code=original_code,
            vuln_desc=vuln_desc,
            poe_script=poe_script,
            target_file_path=target_file_path,
            initial_logs=result_run_1['logs']
        )
    else:
        print("\n✅ [VERDICT] Code is secure against this attack vector.")

    print("\n🏁 PIPELINE COMPLETE.\n")


def _run_patch_verification_loop(original_code, vuln_desc, poe_script, 
                                  target_file_path, initial_logs):
    """
    Internal function to run the iterative patch verification loop.
    
    This function attempts to patch the vulnerability multiple times,
    testing each patch against the exploit until successful or max retries.
    
    Args:
        original_code: The original vulnerable code
        vuln_desc: Description of the vulnerability
        poe_script: The exploit script
        target_file_path: Path to the target file
        initial_logs: Initial exploit execution logs
    """
    print("\n[🛡️ BLUE TEAM] Vulnerability confirmed! Initiating iterative patching...")
    
    max_retries = 3
    attempt = 1
    current_logs = initial_logs
    is_patched = False

    while attempt <= max_retries:
        print(f"\n--- 🛠️ Patch Attempt {attempt}/{max_retries} ---")
        
        # Generate patch using Blue Team AI
        blue_team_results = call_blue_team_api(
            vulnerable_code=original_code,
            vulnerability_description=vuln_desc,
            failure_logs=current_logs
        )
        patched_code = blue_team_results.get("patched_code", "")
        print(f"\n[🛠️ BLUE TEAM PATCH REVEALED]")
        print(patched_code)
        
        # Apply and test the patch
        print("[⚖️ VERIFIER] Applying patch and re-testing in Sandbox...")
        apply_patch(target_file_path, patched_code)

        # Re-run the exploit against the patched code
        result_run_verification = call_verifier(poe_script, target_file_path)

        # Check if the patch successfully blocked the exploit
        if not result_run_verification['success'] or "Bypass successful" not in result_run_verification['logs']:
            print(f"\n✅ [VERDICT] Patch Verified on attempt {attempt}! Exploit neutralized.")
            is_patched = True
            break
        else:
            print(f"❌ [VERDICT] Patch Failed. Red Team bypassed the fix.")
            current_logs = result_run_verification['logs']
            attempt += 1
            time.sleep(1)

    if not is_patched:
        print(f"\n🚨 [VERDICT] Blue Team failed to secure the code after {max_retries} attempts. Human intervention required!")

    # Always restore original code after testing
    apply_patch(target_file_path, original_code)
