#!/bin/bash
# Run Home Assistant with automatic restart support
# This script detects exit code 100 (RESTART_EXIT_CODE) and automatically restarts

cd "$(dirname "$0")"
source .venv/bin/activate

RESTART_EXIT_CODE=100

# Function to handle signals gracefully
cleanup() {
    echo ""
    echo "=========================================="
    echo "Received interrupt signal"
    echo "Waiting for Home Assistant to shutdown..."
    echo "=========================================="
    # Let the process finish naturally
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
    
    # Run Home Assistant in foreground (not background)
    # This ensures proper signal handling and exit code capture
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
        echo "  The restart API was called successfully!"
        echo "  Restarting Home Assistant in 2 seconds..."
        echo ""
        sleep 2
        continue
    elif [ $exit_code -eq 0 ]; then
        echo ""
        echo "Home Assistant exited normally (code 0)"
        exit 0
    elif [ $exit_code -eq 137 ]; then
        echo ""
        echo "⚠ WARNING: Process was KILLED (SIGKILL - signal 9)"
        echo "  Exit code 137 = 128 + 9 (SIGKILL)"
        echo "  The process was forcefully terminated."
        echo "  This is NOT a restart - something killed the process."
        echo ""
        echo "  Possible causes:"
        echo "    - System out of memory (OOM killer)"
        echo "    - macOS Activity Monitor"
        echo "    - Manual kill command"
        echo ""
        echo "  Check system logs: log show --predicate 'process == \"python\"' --last 5m"
        exit $exit_code
    else
        echo ""
        echo "Home Assistant exited with error code: $exit_code"
        echo "  Not restarting automatically."
        exit $exit_code
    fi
done

