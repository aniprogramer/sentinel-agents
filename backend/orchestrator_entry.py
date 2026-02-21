"""
Entry script for running orchestrator utilities without shadowing the
`orchestrator` package name used by the application.

This file preserves the previous behavior of running a quick scan when
executed directly, but it avoids naming conflicts with the `orchestrator`
package located in `backend/orchestrator/`.
"""

import os

# Import from the orchestrator package (pipeline/scanner are submodules)
from orchestrator import run_autonomous_pipeline, scan_entire_repository


if __name__ == "__main__":
    target_folder = os.path.abspath(os.path.join("..", "target_code"))
    scan_entire_repository(target_folder)
