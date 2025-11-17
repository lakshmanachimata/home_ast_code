# Home Assistant Restart and Shutdown API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Restart API](#restart-api)
4. [Shutdown API](#shutdown-api)
5. [Error Handling](#error-handling)
6. [Code Examples](#code-examples)
7. [Best Practices](#best-practices)
8. [Limitations and Considerations](#limitations-and-considerations)

---

## Overview

Home Assistant provides REST API endpoints to restart and shutdown the application. These are administrative operations that require proper authentication and permissions.

**Base URL:** `http://localhost:8123` (or your Home Assistant instance URL)

**API Version:** Uses the standard Home Assistant REST API

---

## Authentication

All API requests require authentication using one of the following methods:

### 1. Long-Lived Access Token (Recommended)
- Generate from: **Profile → Long-Lived Access Tokens**
- Include in header: `Authorization: Bearer YOUR_ACCESS_TOKEN`

### 2. Bearer Token
- Use your authentication token in the Authorization header

**Example Header:**
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json
```

---

## Restart API

Restarts Home Assistant with optional safe mode support.

### Endpoint

```
POST /api/services/homeassistant/restart
```

### Description

Restarts the Home Assistant application. Before restarting, the system:
- Validates the configuration file for errors
- Checks if a database migration is in progress
- Optionally enables safe mode (disables custom integrations and custom cards)

### Request Parameters

#### Path Parameters
None

#### Query Parameters
None

#### Request Body (JSON)

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `safe_mode` | boolean | No | `false` | If `true`, restarts in safe mode which disables custom integrations and custom cards. Useful for troubleshooting. |

### Request Examples

#### Basic Restart
```bash
curl -X POST http://localhost:8123/api/services/homeassistant/restart \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

#### Restart with Safe Mode
```bash
curl -X POST http://localhost:8123/api/services/homeassistant/restart \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"safe_mode": true}'
```

#### Explicit Normal Restart
```bash
curl -X POST http://localhost:8123/api/services/homeassistant/restart \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"safe_mode": false}'
```

### Response

#### Success Response

**Status Code:** `200 OK`

**Response Body:**
```json
[]
```

The response is an empty array, indicating the service call was successful. The restart process begins immediately after the response is sent.

#### Error Responses

**Status Code:** `400 Bad Request`

**Possible Error Messages:**

1. **Configuration Validation Failed:**
```json
{
  "message": "The system cannot restart because the configuration is not valid: [error details]"
}
```

2. **Database Migration in Progress:**
```json
{
  "message": "The system cannot restart while a database upgrade is in progress."
}
```

3. **Invalid JSON:**
```json
{
  "message": "Data should be valid JSON."
}
```

**Status Code:** `401 Unauthorized**
```json
{
  "message": "Unauthorized"
}
```

**Status Code:** `403 Forbidden**
```json
{
  "message": "Forbidden"
}
```

### Behavior

1. **Configuration Validation:** The system validates `configuration.yaml` and related files before restarting. If errors are found:
   - An error is logged
   - A persistent notification is created
   - The restart is aborted
   - An error response is returned

2. **Safe Mode:** When `safe_mode: true`:
   - Safe mode is enabled before restart
   - Custom integrations are disabled
   - Custom cards are disabled
   - Useful for troubleshooting configuration issues

3. **Restart Process:**
   - The API call returns immediately
   - Home Assistant begins shutdown sequence
   - Exit code `100` is used to signal restart (not shutdown)
   - The application restarts automatically

---

## Shutdown API

Shuts down Home Assistant completely.

### Endpoint

```
POST /api/services/homeassistant/stop
```

### Description

Stops the Home Assistant application completely. The system will:
- Execute shutdown jobs
- Stop all integrations
- Save persistent states
- Exit the application

**⚠️ Warning:** This will stop Home Assistant. It will not restart automatically unless managed by a process manager (systemd, Docker, etc.).

### Request Parameters

#### Path Parameters
None

#### Query Parameters
None

#### Request Body

Optional. Can be empty `{}` or omitted entirely.

### Request Examples

#### Basic Shutdown
```bash
curl -X POST http://localhost:8123/api/services/homeassistant/stop \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

#### Shutdown with Empty Body
```bash
curl -X POST http://localhost:8123/api/services/homeassistant/stop \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Response

#### Success Response

**Status Code:** `200 OK`

**Response Body:**
```json
[]
```

The response is an empty array, indicating the service call was successful. The shutdown process begins immediately.

#### Error Responses

**Status Code:** `400 Bad Request`

**Possible Error Messages:**

1. **Database Migration in Progress:**
```json
{
  "message": "The system cannot stop while a database upgrade is in progress."
}
```

2. **Invalid JSON:**
```json
{
  "message": "Data should be valid JSON."
}
```

**Status Code:** `401 Unauthorized**
```json
{
  "message": "Unauthorized"
}
```

**Status Code:** `403 Forbidden**
```json
{
  "message": "Forbidden"
}
```

### Behavior

1. **Shutdown Sequence:**
   - Stage 1: Execute all registered shutdown jobs
   - Stage 2: Stop all integrations gracefully
   - Stage 3: Save persistent states
   - Stage 4: Exit with code `0` (normal shutdown)

2. **No Configuration Validation:** Unlike restart, shutdown does not validate configuration files.

3. **Exit Code:** Uses exit code `0` (normal termination), not `100` (restart).

---

## Error Handling

### Common Error Scenarios

#### 1. Database Migration in Progress

Both restart and shutdown will fail if a database migration is in progress:

```json
{
  "message": "The system cannot [restart|stop] while a database upgrade is in progress."
}
```

**Solution:** Wait for the migration to complete before attempting restart/shutdown.

#### 2. Configuration Errors (Restart Only)

Restart validates configuration before proceeding:

```json
{
  "message": "The system cannot restart because the configuration is not valid: [error details]"
}
```

**Solution:** Fix configuration errors shown in the logs before restarting.

#### 3. Authentication Errors

```json
{
  "message": "Unauthorized"
}
```

**Solution:** Ensure you're using a valid access token with admin permissions.

#### 4. Permission Errors

```json
{
  "message": "Forbidden"
}
```

**Solution:** Ensure your user account has administrative privileges.

#### 5. Bluetooth/Event Loop Shutdown Error (Non-Critical)

**⚠️ Important:** This is a known issue that does NOT affect the API call itself.

During shutdown, you may see errors in the Home Assistant logs (not in the API response) related to Bluetooth:

```
RuntimeError: Event loop is closed
```

**What's happening:**
- This occurs when Home Assistant shuts down
- The Bluetooth component (using `bleak` with CoreBluetooth on macOS) tries to deliver callbacks from a background thread
- The event loop has already been closed, causing a race condition
- This is a cleanup issue, not an API failure

**Why it's safe to ignore:**
- The API call returns successfully (HTTP 200)
- The restart/shutdown operation completes normally
- This is a known issue with `bleak` and asyncio during shutdown
- It doesn't prevent Home Assistant from restarting or shutting down

**When you see this:**
- The API call succeeded
- Home Assistant is shutting down/restarting as expected
- You can safely ignore these errors in the logs
- The error appears in the Home Assistant process logs, not in the API response

**Example log output (safe to ignore):**
```
PyObjC: Converting exception to Objective-C:2025-11-16 21:55:02.638 ERROR (Dummy-9) [root] Uncaught exception
Traceback (most recent call last):
  File ".../bleak/backends/corebluetooth/CentralManagerDelegate.py", line 277
    self.event_loop.call_soon_threadsafe(...)
RuntimeError: Event loop is closed
```

**Note:** This is expected behavior during shutdown and does not indicate a problem with your API call or Home Assistant's functionality.

### Error Response Format

All errors follow this structure:

```json
{
  "message": "Error description here"
}
```

**Important:** The Bluetooth/event loop error mentioned above does NOT appear in the API response. It only appears in the Home Assistant process logs and can be safely ignored.

---

## Code Examples

### Python (aiohttp)

```python
import aiohttp
import asyncio

async def restart_home_assistant(access_token: str, safe_mode: bool = False):
    """Restart Home Assistant.
    
    Note: You may see Bluetooth/event loop errors in Home Assistant logs
    during shutdown. These are non-critical and can be safely ignored.
    The API call succeeds if HTTP 200 is returned.
    """
    url = "http://localhost:8123/api/services/homeassistant/restart"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {"safe_mode": safe_mode}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"Restart initiated: {result}")
                    # Note: Bluetooth errors may appear in HA logs but don't affect this call
                    return True
                else:
                    error = await response.json()
                    print(f"Error: {error.get('message', 'Unknown error')}")
                    return False
        except aiohttp.ClientError as e:
            print(f"Connection error: {e}")
            return False

async def stop_home_assistant(access_token: str):
    """Stop Home Assistant.
    
    Note: You may see Bluetooth/event loop errors in Home Assistant logs
    during shutdown. These are non-critical and can be safely ignored.
    The API call succeeds if HTTP 200 is returned.
    """
    url = "http://localhost:8123/api/services/homeassistant/stop"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"Shutdown initiated: {result}")
                    # Note: Bluetooth errors may appear in HA logs but don't affect this call
                    return True
                else:
                    error = await response.json()
                    print(f"Error: {error.get('message', 'Unknown error')}")
                    return False
        except aiohttp.ClientError as e:
            print(f"Connection error: {e}")
            return False

# Usage
async def main():
    token = "YOUR_ACCESS_TOKEN"
    
    # Restart normally
    await restart_home_assistant(token)
    
    # Restart in safe mode
    await restart_home_assistant(token, safe_mode=True)
    
    # Shutdown
    await stop_home_assistant(token)

if __name__ == "__main__":
    asyncio.run(main())
```

### Python (requests)

```python
import requests

def restart_home_assistant(access_token: str, safe_mode: bool = False):
    """Restart Home Assistant."""
    url = "http://localhost:8123/api/services/homeassistant/restart"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {"safe_mode": safe_mode}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        print(f"Restart initiated: {response.json()}")
        return True
    except requests.exceptions.HTTPError as e:
        error = e.response.json() if e.response else {}
        print(f"Error: {error.get('message', str(e))}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return False

def stop_home_assistant(access_token: str):
    """Stop Home Assistant."""
    url = "http://localhost:8123/api/services/homeassistant/stop"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, timeout=30)
        response.raise_for_status()
        print(f"Shutdown initiated: {response.json()}")
        return True
    except requests.exceptions.HTTPError as e:
        error = e.response.json() if e.response else {}
        print(f"Error: {error.get('message', str(e))}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return False

# Usage
token = "YOUR_ACCESS_TOKEN"
restart_home_assistant(token)
stop_home_assistant(token)
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

async function restartHomeAssistant(accessToken, safeMode = false) {
    const url = 'http://localhost:8123/api/services/homeassistant/restart';
    const headers = {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
    };
    const data = { safe_mode: safeMode };
    
    try {
        const response = await axios.post(url, data, { headers });
        console.log('Restart initiated:', response.data);
        return true;
    } catch (error) {
        if (error.response) {
            console.error('Error:', error.response.data.message || 'Unknown error');
        } else {
            console.error('Connection error:', error.message);
        }
        return false;
    }
}

async function stopHomeAssistant(accessToken) {
    const url = 'http://localhost:8123/api/services/homeassistant/stop';
    const headers = {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
    };
    
    try {
        const response = await axios.post(url, {}, { headers });
        console.log('Shutdown initiated:', response.data);
        return true;
    } catch (error) {
        if (error.response) {
            console.error('Error:', error.response.data.message || 'Unknown error');
        } else {
            console.error('Connection error:', error.message);
        }
        return false;
    }
}

// Usage
const token = 'YOUR_ACCESS_TOKEN';
restartHomeAssistant(token);
stopHomeAssistant(token);
```

### JavaScript (Browser/Fetch API)

```javascript
async function restartHomeAssistant(accessToken, safeMode = false) {
    const url = 'http://localhost:8123/api/services/homeassistant/restart';
    const headers = {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
    };
    const body = JSON.stringify({ safe_mode: safeMode });
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: body
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('Restart initiated:', data);
            return true;
        } else {
            const error = await response.json();
            console.error('Error:', error.message || 'Unknown error');
            return false;
        }
    } catch (error) {
        console.error('Connection error:', error.message);
        return false;
    }
}

async function stopHomeAssistant(accessToken) {
    const url = 'http://localhost:8123/api/services/homeassistant/stop';
    const headers = {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
    };
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: headers
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('Shutdown initiated:', data);
            return true;
        } else {
            const error = await response.json();
            console.error('Error:', error.message || 'Unknown error');
            return false;
        }
    } catch (error) {
        console.error('Connection error:', error.message);
        return false;
    }
}

// Usage
const token = 'YOUR_ACCESS_TOKEN';
restartHomeAssistant(token);
stopHomeAssistant(token);
```

### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
)

type RestartRequest struct {
    SafeMode bool `json:"safe_mode"`
}

func restartHomeAssistant(accessToken string, safeMode bool) error {
    url := "http://localhost:8123/api/services/homeassistant/restart"
    
    reqBody := RestartRequest{SafeMode: safeMode}
    jsonData, err := json.Marshal(reqBody)
    if err != nil {
        return fmt.Errorf("failed to marshal request: %w", err)
    }
    
    req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
    if err != nil {
        return fmt.Errorf("failed to create request: %w", err)
    }
    
    req.Header.Set("Authorization", "Bearer "+accessToken)
    req.Header.Set("Content-Type", "application/json")
    
    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        return fmt.Errorf("request failed: %w", err)
    }
    defer resp.Body.Close()
    
    if resp.StatusCode != http.StatusOK {
        body, _ := io.ReadAll(resp.Body)
        return fmt.Errorf("error: %s", string(body))
    }
    
    fmt.Println("Restart initiated successfully")
    return nil
}

func stopHomeAssistant(accessToken string) error {
    url := "http://localhost:8123/api/services/homeassistant/stop"
    
    req, err := http.NewRequest("POST", url, nil)
    if err != nil {
        return fmt.Errorf("failed to create request: %w", err)
    }
    
    req.Header.Set("Authorization", "Bearer "+accessToken)
    req.Header.Set("Content-Type", "application/json")
    
    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        return fmt.Errorf("request failed: %w", err)
    }
    defer resp.Body.Close()
    
    if resp.StatusCode != http.StatusOK {
        body, _ := io.ReadAll(resp.Body)
        return fmt.Errorf("error: %s", string(body))
    }
    
    fmt.Println("Shutdown initiated successfully")
    return nil
}

func main() {
    token := "YOUR_ACCESS_TOKEN"
    
    if err := restartHomeAssistant(token, false); err != nil {
        fmt.Printf("Restart failed: %v\n", err)
    }
    
    if err := stopHomeAssistant(token); err != nil {
        fmt.Printf("Shutdown failed: %v\n", err)
    }
}
```

### PowerShell

```powershell
function Restart-HomeAssistant {
    param(
        [string]$AccessToken,
        [bool]$SafeMode = $false
    )
    
    $url = "http://localhost:8123/api/services/homeassistant/restart"
    $headers = @{
        "Authorization" = "Bearer $AccessToken"
        "Content-Type" = "application/json"
    }
    $body = @{
        safe_mode = $SafeMode
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $body
        Write-Host "Restart initiated: $response"
        return $true
    }
    catch {
        Write-Host "Error: $($_.Exception.Message)"
        return $false
    }
}

function Stop-HomeAssistant {
    param(
        [string]$AccessToken
    )
    
    $url = "http://localhost:8123/api/services/homeassistant/stop"
    $headers = @{
        "Authorization" = "Bearer $AccessToken"
        "Content-Type" = "application/json"
    }
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers
        Write-Host "Shutdown initiated: $response"
        return $true
    }
    catch {
        Write-Host "Error: $($_.Exception.Message)"
        return $false
    }
}

# Usage
$token = "YOUR_ACCESS_TOKEN"
Restart-HomeAssistant -AccessToken $token
Stop-HomeAssistant -AccessToken $token
```

---

## Best Practices

### 1. **Use Long-Lived Access Tokens**
- Generate tokens from the Home Assistant UI
- Store tokens securely (environment variables, secrets management)
- Never commit tokens to version control

### 2. **Error Handling**
- Always check HTTP status codes
- Parse and display error messages to users
- Implement retry logic for transient failures (but not for restart/shutdown)

### 3. **Timeout Configuration**
- Set appropriate timeouts (30-60 seconds recommended)
- The API returns immediately, but the operation may take time to complete

### 4. **Safe Mode Usage**
- Use safe mode when troubleshooting configuration issues
- Safe mode helps identify if custom integrations are causing problems

### 5. **Monitoring**
- Monitor Home Assistant status after restart/shutdown
- Use health check endpoints to verify the system is running
- Log all restart/shutdown operations for audit purposes

### 6. **Security**
- Use HTTPS in production environments
- Restrict API access to trusted networks when possible
- Regularly rotate access tokens

### 7. **Graceful Shutdown**
- Avoid calling shutdown during active operations
- Wait for critical processes to complete before shutting down
- Consider using restart instead of stop when possible

---

## Limitations and Considerations

### 1. **Database Migrations**
- Both restart and shutdown will fail if a database migration is in progress
- Wait for migrations to complete before attempting these operations

### 2. **Configuration Validation (Restart Only)**
- Restart validates configuration files before proceeding
- Invalid configurations will prevent restart
- Check logs for specific configuration errors

### 3. **No Automatic Restart (Shutdown)**
- Shutdown stops Home Assistant completely
- It will not restart automatically unless managed by:
  - systemd
  - Docker restart policies
  - Supervisor (Home Assistant OS)
  - Other process managers

### 4. **Response Timing**
- API calls return immediately
- The actual restart/shutdown process happens asynchronously
- The response does not wait for the operation to complete

### 5. **Admin Permissions Required**
- Both services require administrative privileges
- Regular users cannot restart or shutdown Home Assistant

### 6. **Connection Loss**
- After shutdown, the API will be unavailable
- After restart, wait for Home Assistant to fully start before making new API calls

### 7. **Safe Mode Limitations**
- Safe mode disables custom integrations and cards
- Some functionality may be unavailable in safe mode
- Remember to disable safe mode after troubleshooting

### 8. **Process Management**
- In containerized environments, ensure proper restart policies
- In systemd environments, use `systemctl restart home-assistant` when appropriate
- Supervisor-managed instances handle restarts automatically

### 9. **State Persistence**
- Persistent states are saved during shutdown
- States are preserved during restart
- Ensure sufficient time for state saving operations

### 10. **Integration Cleanup**
- Integrations are stopped gracefully during shutdown
- Some integrations may take time to clean up resources
- Restart may be faster than shutdown + manual start

### 11. **Bluetooth/Event Loop Shutdown Errors (Non-Critical)**
- On macOS, you may see `RuntimeError: Event loop is closed` errors in logs during shutdown
- This is a known race condition with the `bleak` Bluetooth library and asyncio
- **These errors do NOT affect the API call or shutdown/restart operation**
- The API returns HTTP 200 successfully even if these errors appear in logs
- This is a cleanup issue, not a functional problem
- Safe to ignore - Home Assistant restarts/shuts down normally despite these log errors

### 12. **Restart Not Working in Debug Mode**
- **Issue:** Restart may not work when running Home Assistant with a debugger attached (VS Code, PyCharm, etc.)
- **Cause:** Restart uses exit code 100, requiring the process to exit and be restarted by the parent. Debuggers intercept exits and keep the process alive.
- **Solutions:**
  1. **Test restart without debugger:** Run Home Assistant normally (not in debug mode) to test restart functionality
  2. **Use shutdown instead:** In debug mode, use the shutdown API and manually restart
  3. **Create a restart wrapper script:** See example below

**Restart Wrapper Script Example (for debug mode):**

```python
#!/usr/bin/env python3
"""Wrapper script to handle restart in debug mode."""
import subprocess
import sys
import os

RESTART_EXIT_CODE = 100

def main():
    """Run Home Assistant with restart support."""
    config_dir = sys.argv[1] if len(sys.argv) > 1 else "config"
    
    while True:
        # Run Home Assistant
        result = subprocess.run(
            [sys.executable, "-m", "homeassistant", "--debug", "-c", config_dir],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        # Check exit code
        if result.returncode == RESTART_EXIT_CODE:
            print("Restart requested, restarting Home Assistant...")
            continue  # Loop to restart
        else:
            # Normal exit or error
            sys.exit(result.returncode)

if __name__ == "__main__":
    main()
```

**Usage:**
```bash
python restart_wrapper.py config
```

**Note:** In production (non-debug) environments, restart works automatically because the process manager (systemd, Docker, Supervisor) handles the exit code 100 and restarts the service.

---

## Additional Resources

- [Home Assistant REST API Documentation](https://developers.home-assistant.io/docs/api/rest/)
- [Home Assistant Authentication](https://developers.home-assistant.io/docs/auth_api/)
- [Home Assistant Services](https://www.home-assistant.io/integrations/homeassistant/#services)
- [Safe Mode Documentation](https://www.home-assistant.io/docs/configuration/troubleshooting/)

---

## Version Information

- **Documentation Version:** 1.0
- **Home Assistant API Version:** Current
- **Last Updated:** Based on Home Assistant core codebase

---

## Support

For issues or questions:
1. Check Home Assistant logs: `/config/logs` or `journalctl -u home-assistant`
2. Review [Home Assistant Community Forum](https://community.home-assistant.io/)
3. Check [GitHub Issues](https://github.com/home-assistant/core/issues)

---

**Note:** This documentation is based on the Home Assistant core codebase. API behavior may vary slightly between versions. Always test in a development environment before using in production.

