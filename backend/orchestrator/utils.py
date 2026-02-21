"""
Utility Functions

This module contains utility functions used across the orchestrator.
"""

import os


def apply_patch(target_file, patched_code):
    """
    Apply a security patch to a target file.

    Args:
        target_file: Path to the file to patch
        patched_code: The patched code content
    """
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(patched_code)
    print(f"[*] Patch applied to {target_file}")


def extract_ast_context(code):
    """
    Extract AST context from source code using the AST analyzer.

    Args:
        code: The source code to analyze

    Returns:
        dict: AST context with functions, sinks, imports, etc.
    """
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ast_engine'))
    from analyzer import analyze_code
    return analyze_code(code)


def get_vulnerability_description(auditor_results):
    """
    Extract the primary vulnerability description from auditor results.

    Args:
        auditor_results: Results from the auditor API

    Returns:
        str: Primary vulnerability description
    """
    vuln_desc = "Unknown vulnerability"
    if auditor_results.get("red_team_findings"):
        vuln_desc = auditor_results["red_team_findings"][0]
    return vuln_desc


def is_exploitable(auditor_results):
    """
    Check if the auditor found exploitable vulnerabilities.

    Args:
        auditor_results: Results from the auditor API

    Returns:
        bool: True if exploitable logic was found
    """
    return bool(auditor_results.get("red_team_findings"))


def is_critical_finding(auditor_results):
    """
    Check if the auditor found critical or high severity issues.

    Args:
        auditor_results: Results from the auditor API

    Returns:
        bool: True if severity is HIGH or CRITICAL
    """
    return auditor_results.get("severity_score", "").upper() in ["HIGH", "CRITICAL"]
