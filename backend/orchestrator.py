"""
Sentinel Agents Security Engine - Main Entry Point

This is the main orchestrator that coordinates the autonomous security pipeline.
All logic has been modularized into the orchestrator package for better maintainability.

Package Structure:
- orchestrator/agents.py: API connectors for Auditor, Red Team, Blue Team, Verifier
- orchestrator/pipeline.py: Main security pipeline execution logic
- orchestrator/scanner.py: Repository scanning functionality
- orchestrator/utils.py: Utility functions (patching, AST extraction, etc.)
"""

import os
from orchestrator import run_autonomous_pipeline, scan_entire_repository


if __name__ == "__main__":
    target_folder = os.path.abspath(os.path.join("..", "target_code"))
    scan_entire_repository(target_folder)
