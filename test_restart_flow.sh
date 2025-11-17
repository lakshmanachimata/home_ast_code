#!/bin/bash
# Complete test flow for restart functionality

echo "=========================================="
echo "Home Assistant Restart Test Flow"
echo "=========================================="
echo ""

cd "$(dirname "$0")"
source .venv/bin/activate

echo "Step 1: Starting Home Assistant..."
echo "  - Keep this terminal open"
echo "  - Wait for Home Assistant to fully start"
echo "  - You'll see 'Home Assistant process exited' when it stops"
echo ""
echo "Step 2: In ANOTHER terminal, run:"
echo "  curl -X POST http://localhost:8123/api/services/homeassistant/restart \\"
echo "    -H 'Authorization: Bearer YOUR_TOKEN' \\"
echo "    -H 'Content-Type: application/json'"
echo ""
echo "Step 3: Watch this terminal for exit code 100"
echo ""
echo "=========================================="
echo ""

# Run the restart wrapper
exec ./homeassistant/run_with_restart.sh

