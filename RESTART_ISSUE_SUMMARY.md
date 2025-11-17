# Home Assistant Restart Issue Summary

## Current Situation

You're seeing **exit code 137** (process killed with SIGKILL) instead of **exit code 100** (restart).

## What Exit Code 137 Means

- **137 = 128 + 9** (SIGKILL signal)
- The process was **forcefully terminated**
- This is **NOT** a restart - something killed the process

## The Problem

Looking at your terminal output, the process is being killed **during startup**, not during a restart API call. This means:

1. Home Assistant starts loading
2. Something kills it with SIGKILL (signal 9)
3. Exit code 137 is returned
4. The script exits (doesn't restart)

## What You Need to Do

### Step 1: Let Home Assistant Fully Start

**DO NOT** press Ctrl+C or close the terminal. Let Home Assistant fully start. You'll know it's ready when you see it's fully loaded (no more component loading messages).

### Step 2: Call the Restart API from Another Terminal

**Open a NEW terminal** and call the restart API:

```bash
# Get your access token from Home Assistant UI first:
# http://localhost:8123 → Profile → Long-Lived Access Tokens

curl -X POST http://localhost:8123/api/services/homeassistant/restart \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### Step 3: Watch the First Terminal

You should see:
```
Home Assistant process exited
  Exit code: 100
✓ RESTART DETECTED (exit code 100)
```

## Why You're Seeing Exit Code 137

The process is being killed **before** you call the restart API. Possible reasons:

1. **You're manually killing it** (Ctrl+C, closing terminal, etc.)
   - **Solution:** Don't do that - let it run

2. **macOS Activity Monitor** is force-quitting it
   - **Solution:** Check Activity Monitor, don't force-quit Python processes

3. **System is killing it** (memory pressure, etc.)
   - **Solution:** Check system resources

4. **Another process is killing it**
   - **Solution:** Check what's running: `ps aux | grep python`

## How to Verify the Script Works

The script itself is correct. To verify:

1. Start Home Assistant: `./homeassistant/run_with_restart.sh`
2. **Wait** for it to fully start (don't kill it!)
3. **Call the restart API** from another terminal
4. Watch for exit code 100

## If Process Keeps Getting Killed

If the process is being killed during startup (before you even call the API), check:

```bash
# Check system logs
log show --predicate 'process == "python"' --last 10m

# Check for other Python processes
ps aux | grep python

# Check memory
vm_stat

# Check if something is monitoring/killing processes
ps aux | grep -i "monitor\|watch\|kill"
```

## Expected Behavior

**When restart API is called:**
- Exit code: **100** ✓
- Script detects it and restarts automatically
- You see "✓ RESTART DETECTED"

**When process is killed:**
- Exit code: **137** ✗
- Script exits (doesn't restart)
- You see "⚠ WARNING: Process was KILLED"

## Key Point

**You must actually CALL the restart API** - just starting Home Assistant won't restart it. The restart API must be called from another terminal while Home Assistant is running.

