# How to Test Home Assistant Restart

## Important: You Need TWO Terminals

The restart API must be called from a **different terminal** while Home Assistant is running.

## Step-by-Step Instructions

### Terminal 1: Start Home Assistant

```bash
cd /Users/lakshmana/projects/hm_ast/home_ast_code
./homeassistant/run_with_restart.sh
```

**Keep this terminal open and watch it.** You should see:
```
==========================================
Starting Home Assistant...
  To test restart, call the API:
    POST /api/services/homeassistant/restart
==========================================
```

Then Home Assistant will start loading. **Wait for it to fully start** (you'll see it's ready).

### Terminal 2: Call the Restart API

**Open a NEW terminal** and run:

```bash
# First, get your access token from Home Assistant UI:
# 1. Go to http://localhost:8123
# 2. Profile → Long-Lived Access Tokens → Create Token
# 3. Copy the token

# Then call the restart API:
curl -X POST http://localhost:8123/api/services/homeassistant/restart \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

### What You Should See

**In Terminal 1** (where Home Assistant is running), you should see:

```
==========================================
Home Assistant process exited
  Exit code: 100
==========================================

✓ RESTART DETECTED (exit code 100)
  The restart API was called successfully!
  Restarting Home Assistant in 2 seconds...

==========================================
Starting Home Assistant...
```

Then Home Assistant will restart automatically.

## Common Mistakes

### ❌ Wrong: Killing the Process Manually

If you press **Ctrl+C** or close the terminal, you'll see:
- Exit code: **137** (process killed)
- This is **NOT** a restart

### ❌ Wrong: Not Calling the API

Just starting Home Assistant and waiting won't trigger a restart. You **must** call the restart API from another terminal.

### ✅ Correct: Call the API While It's Running

1. Start Home Assistant in Terminal 1
2. Wait for it to fully start
3. Call the restart API from Terminal 2
4. Watch Terminal 1 for exit code 100

## Troubleshooting

### If You See Exit Code 137

This means the process was killed, not restarted. Check:
- Did you press Ctrl+C? (Don't do that)
- Did you close the terminal? (Don't do that)
- Is Activity Monitor force-quitting it?
- Check system logs for what killed it

### If You See Exit Code 0

This means normal shutdown (not restart). This happens if:
- You called the **stop** API (not restart)
- The process exited normally for some other reason

### If You See Exit Code 100

**SUCCESS!** This means:
- The restart API was called
- Home Assistant exited with restart code
- The script will automatically restart it

## Quick Test Script

You can also use the test script:

```bash
# Terminal 1
./test_restart_flow.sh

# Terminal 2 (after HA starts)
python test_restart_api.py YOUR_ACCESS_TOKEN
```

