"""
Sentinel Agents Orchestrator Package

This package contains the autonomous security pipeline that coordinates
all security agents: Auditor, Red Team, Blue Team, and Verifier.
"""

from .pipeline import run_autonomous_pipeline
from .scanner import scan_entire_repository

__all__ = [
    'run_autonomous_pipeline',
    'scan_entire_repository'
]
