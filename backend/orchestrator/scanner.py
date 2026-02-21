"""
Repository Scanner

This module contains functionality for scanning entire repositories
and detecting vulnerabilities across multiple files.
"""

import os
import glob
import json
from .agents import call_auditor_api
from .pipeline import run_autonomous_pipeline
from .utils import extract_ast_context, is_critical_finding


def scan_entire_repository(repo_path):
    """
    Scan an entire repository for security vulnerabilities.
    
    This function:
    1. Recursively finds all scannable files (.py, .js, .json, .env)
    2. Runs auditor analysis on each file
    3. Triggers full pipeline for critical findings in Python files
    
    Args:
        repo_path: Path to the repository root directory
    """
    print("\n" + "="*50)
    print(f"📂 INITIATING FULL REPOSITORY SCAN: {repo_path}")
    print("="*50)
    
    files_to_scan = _gather_scannable_files(repo_path)

    if not files_to_scan:
        print("❌ No scannable files found in directory.")
        return

    print(f"🔍 Found {len(files_to_scan)} files to analyze. Starting Auditor...\n")

    for file_path in files_to_scan:
        _scan_single_file(file_path)


def _gather_scannable_files(repo_path):
    """
    Gather all scannable files from the repository.
    
    Args:
        repo_path: Path to the repository root
        
    Returns:
        list: List of file paths to scan
    """
    target_extensions = ['*.py', '*.js', '.env*', '*.json']
    files_to_scan = []
    
    for ext in target_extensions:
        search_pattern = os.path.join(repo_path, '**', ext)
        files_to_scan.extend(glob.glob(search_pattern, recursive=True))
    
    return files_to_scan


def _scan_single_file(file_path):
    """
    Scan a single file for vulnerabilities.
    
    Args:
        file_path: Path to the file to scan
    """
    print(f"\n📄 Analyzing: {os.path.basename(file_path)}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()
    
    # Handle different file types
    if ".env" in file_path:
        ast_context = {
            "type": "configuration_file", 
            "warning": "Contains environment variables"
        }
    else:
        ast_context = extract_ast_context(file_content)

    # Run auditor analysis
    auditor_results = call_auditor_api(file_content, ast_context)
    
    # Handle findings
    if is_critical_finding(auditor_results):
        print(f"🚨 [ALERT] High/Critical vulnerabilities found in {os.path.basename(file_path)}!")
        print(json.dumps(auditor_results, indent=2))
        
        # Trigger full pipeline for Python files with critical findings
        if file_path.endswith('.py'):
            print(f"\n[🚀] Triggering Autonomous Sandbox Pipeline for {os.path.basename(file_path)}...")
            run_autonomous_pipeline(file_path, existing_auditor_results=auditor_results)
    else:
        print(f"✅ Clean: No major surface threats found.")
