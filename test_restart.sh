#!/bin/bash
# Test script to verify restart API works

echo "Testing Home Assistant restart..."
echo ""

# Start Home Assistant in background
cd "$(dirname "$0")"
source .venv/bin/activate

echo "Starting Home Assistant in background..."
python -m homeassistant --debug -c config &
HA_PID=$!

echo "Home Assistant PID: $HA_PID"
echo "Waiting for Home Assistant to start..."
sleep 10

# Check if Home Assistant is running
if ! kill -0 $HA_PID 2>/dev/null; then
    echo "ERROR: Home Assistant process died immediately"
    exit 1
fi

echo "Home Assistant is running. Now calling restart API..."
echo ""

# You'll need to replace YOUR_ACCESS_TOKEN with an actual token
# For now, this is just a template
echo "To test restart, call:"
echo "  curl -X POST http://localhost:8123/api/services/homeassistant/restart \\"
echo "    -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \\"
echo "    -H 'Content-Type: application/json'"
echo ""
echo "Waiting for process to exit..."
wait $HA_PID
EXIT_CODE=$?

echo ""
echo "Home Assistant exited with code: $EXIT_CODE"

if [ $EXIT_CODE -eq 100 ]; then
    echo "✓ SUCCESS: Restart worked! Exit code is 100 (RESTART_EXIT_CODE)"
else
    echo "✗ FAILED: Expected exit code 100, got $EXIT_CODE"
    exit 1
fi

