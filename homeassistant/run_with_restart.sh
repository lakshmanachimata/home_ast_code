#!/bin/bash
# Run Home Assistant with automatic restart support
# This script detects exit code 100 (RESTART_EXIT_CODE) and automatically restarts

cd "$(dirname "$0")/.." || cd /Users/lakshmana/projects/hm_ast/home_ast_code
source .venv/bin/activate

RESTART_EXIT_CODE=100

# Function to handle signals
cleanup() {
    echo ""
    echo "=========================================="
    echo "Received interrupt signal (SIGINT/SIGTERM)"
    echo "Waiting for Home Assistant to shutdown gracefully..."
    echo "=========================================="
    # Don't exit immediately - let the process finish
    wait
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

while true; do
    echo ""
    echo "=========================================="
    echo "Starting Home Assistant..."
    echo "  To test restart, call the API:"
    echo "    POST /api/services/homeassistant/restart"
    echo "=========================================="
    echo ""
    
    # Run Home Assistant in FOREGROUND (not background)
    # This ensures proper signal handling and exit code preservation
    # Running in background with & can cause issues with signal handling
    set +e  # Don't exit on non-zero codes
    python -m homeassistant --debug -c config
    exit_code=$?
    set -e
    
    echo ""
    echo "=========================================="
    echo "Home Assistant process exited"
    echo "  Exit code: $exit_code"
    echo "=========================================="
    
    # Decode exit codes
    if [ $exit_code -eq $RESTART_EXIT_CODE ]; then
        echo ""
        echo "✓ RESTART DETECTED (exit code 100)"
        echo "  This means the restart API was called successfully!"
        echo "  Restarting Home Assistant in 2 seconds..."
        echo ""
        sleep 2
        continue
    elif [ $exit_code -eq 0 ]; then
        echo ""
        echo "Home Assistant exited normally (code 0)"
        echo "  This usually means it was stopped via the stop API or Ctrl+C"
        exit 0
    elif [ $exit_code -eq 137 ]; then
        echo ""
        echo "⚠ WARNING: Process was KILLED (SIGKILL - signal 9)"
        echo "  Exit code 137 = 128 + 9 (SIGKILL)"
        echo "  This means the process was forcefully terminated, not restarted."
        echo "  Possible causes:"
        echo "    - Manual kill command (kill -9)"
        echo "    - System out of memory (OOM killer)"
        echo "    - Another process killed it"
        echo ""
        echo "  This is NOT a restart - the restart API was not called."
        echo "  Exiting wrapper script."
        exit $exit_code
    else
        echo ""
        echo "Home Assistant exited with error code: $exit_code"
        echo "  Not restarting automatically."
        exit $exit_code
    fi
done