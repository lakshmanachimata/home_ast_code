#!/usr/bin/env python3
"""Run Home Assistant with automatic restart support.

This script detects exit code 100 (RESTART_EXIT_CODE) and automatically restarts
Home Assistant when the restart API is called.
"""
import subprocess
import sys
import os
from pathlib import Path

RESTART_EXIT_CODE = 100

def main():
    """Run Home Assistant with restart support."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # Get config directory from command line or use default
    config_dir = sys.argv[1] if len(sys.argv) > 1 else "config"
    
    # Activate venv if it exists
    venv_python = script_dir / ".venv" / "bin" / "python"
    if venv_python.exists():
        python_cmd = str(venv_python)
    else:
        python_cmd = sys.executable
    
    while True:
        print("Starting Home Assistant...")
        
        # Run Home Assistant
        result = subprocess.run(
            [python_cmd, "-m", "homeassistant", "--debug", "-c", config_dir],
            cwd=str(script_dir)
        )
        
        # Check exit code
        if result.returncode == RESTART_EXIT_CODE:
            print("\n" + "=" * 50)
            print("Restart requested, restarting Home Assistant...")
            print("=" * 50 + "\n")
            import time
            time.sleep(2)
            continue  # Loop to restart
        else:
            # Normal exit or error
            print(f"\nHome Assistant exited with code {result.returncode}")
            sys.exit(result.returncode)

if __name__ == "__main__":
    main()

