# Troubleshooting Home Assistant Restart

## Issue: Process Getting Killed (Exit Code 137)

If you're seeing exit code 137 (SIGKILL) instead of exit code 100 (restart), the process is being forcefully terminated before it can exit normally.

### What Exit Code 137 Means

- **137 = 128 + 9** (SIGKILL signal)
- The process was **killed**, not restarted
- This is **NOT** a normal restart

### Common Causes

1. **Manual Kill Command**
   - Someone ran `kill -9 <pid>` or `killall python`
   - Check if you or another process is killing it

2. **macOS Activity Monitor**
   - Activity Monitor might be force-quitting the process
   - Check Activity Monitor for any force-quit actions

3. **System Memory Pressure**
   - macOS might kill processes under memory pressure
   - Check: `vm_stat` and `top` to see memory usage

4. **Terminal/Shell Issues**
   - Closing terminal window kills background processes
   - Terminal app force-quit kills child processes
   - **Solution:** Use `nohup` or `screen`/`tmux` for persistent sessions

5. **Background Process Issues**
   - Running with `&` in background can cause signal handling issues
   - **Solution:** Use the updated script that runs in foreground

### How to Verify Restart is Working

1. **Start Home Assistant:**
   ```bash
   ./homeassistant/run_with_restart.sh
   ```

2. **Wait for it to fully start** (you'll see it's ready)

3. **Call the restart API** (in another terminal or browser):
   ```bash
   curl -X POST http://localhost:8123/api/services/homeassistant/restart \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json"
   ```

4. **Watch the first terminal** - you should see:
   ```
   Home Assistant process exited
     Exit code: 100
   ✓ RESTART DETECTED (exit code 100)
   ```

### If You Still See Exit Code 137

1. **Check what's killing it:**
   ```bash
   # Check system logs
   log show --predicate 'process == "python"' --last 10m
   
   # Check for other Home Assistant processes
   ps aux | grep homeassistant
   
   # Check memory
   vm_stat
   ```

2. **Run in a persistent session:**
   ```bash
   # Using screen
   screen -S ha
   ./homeassistant/run_with_restart.sh
   # Detach: Ctrl+A, then D
   # Reattach: screen -r ha
   
   # Using tmux
   tmux new -s ha
   ./homeassistant/run_with_restart.sh
   # Detach: Ctrl+B, then D
   # Reattach: tmux attach -t ha
   ```

3. **Check for conflicting processes:**
   ```bash
   # Make sure no other Home Assistant is running
   pkill -f "python.*homeassistant"
   
   # Remove stale lock file
   rm config/.ha_run.lock
   ```

### Expected Behavior

When restart API is called successfully:
- Exit code: **100** ✓
- Script detects it and restarts automatically
- You'll see "✓ RESTART DETECTED" message

When process is killed:
- Exit code: **137** ✗
- Script exits (doesn't restart)
- You'll see "⚠ WARNING: Process was KILLED" message

### Testing Without API

To verify the script works, you can manually test exit code handling:

```bash
# Test script with exit code 100
python3 -c "import sys; sys.exit(100)"; echo "Exit code: $?"

# Should show: Exit code: 100
```

If this works, the script is fine - the issue is that Home Assistant is being killed before it can exit with code 100.

