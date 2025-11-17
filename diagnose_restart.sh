#!/bin/bash
# Diagnostic script to understand why restart isn't working

echo "=========================================="
echo "Home Assistant Restart Diagnostic"
echo "=========================================="
echo ""

# Check if Home Assistant is running
if pgrep -f "python.*homeassistant" > /dev/null; then
    echo "✓ Home Assistant is currently running"
    pgrep -f "python.*homeassistant" | while read pid; do
        echo "  PID: $pid"
        ps -p $pid -o command= | head -1
    done
else
    echo "✗ Home Assistant is NOT running"
fi

echo ""
echo "Checking lock file..."
if [ -f "config/.ha_run.lock" ]; then
    echo "  Lock file exists:"
    cat config/.ha_run.lock | python3 -m json.tool 2>/dev/null || cat config/.ha_run.lock
    LOCK_PID=$(cat config/.ha_run.lock | python3 -c "import sys, json; print(json.load(sys.stdin)['pid'])" 2>/dev/null)
    if [ ! -z "$LOCK_PID" ]; then
        if ps -p $LOCK_PID > /dev/null 2>&1; then
            echo "  Lock PID $LOCK_PID is still running"
        else
            echo "  Lock PID $LOCK_PID is NOT running (stale lock)"
            echo "  You may need to remove the lock file: rm config/.ha_run.lock"
        fi
    fi
else
    echo "  No lock file found"
fi

echo ""
echo "To test restart:"
echo "1. Start Home Assistant: ./run_with_restart.sh"
echo "2. Wait for it to fully start"
echo "3. In another terminal, call:"
echo "   curl -X POST http://localhost:8123/api/services/homeassistant/restart \\"
echo "     -H 'Authorization: Bearer YOUR_TOKEN' \\"
echo "     -H 'Content-Type: application/json'"
echo ""
echo "4. Watch the first terminal - you should see exit code 100"
echo ""

