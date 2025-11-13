# ZHA Form New Network Flow - Complete Guide

## Overview

The `form_new_network` step in the ZHA (Zigbee Home Automation) config flow is a **progress step** that forms a new Zigbee network. This step does **not require user input** - it runs a background task that can take up to a minute to complete (scanning for a clear network channel).

## Important: REST API Only

**Config flow steps cannot be submitted via WebSocket API.** You must use the REST API to:
- Check progress status
- Advance to the next step
- Complete the flow

WebSocket APIs are available only for:
- Subscribing to config entry changes
- Getting flow progress (read-only)
- Receiving notifications

## Step Flow: `form_new_network` → `create_entry`

### Step 1: Enter `form_new_network` Step

When you reach the `form_new_network` step, the flow automatically:
1. Starts a background task to form a new Zigbee network
2. Returns a progress response indicating the task is running

**Initial Response (Progress Started):**
```json
{
  "flow_id": "abc123...",
  "handler": "zha",
  "type": "show_progress",
  "step_id": "form_new_network",
  "progress_action": "form_new_network",
  "description": "Forming a new Zigbee network.\n\nWe scan for a clear network channel as part of this process, this can take a minute.",
  "description_placeholders": {}
}
```

### Step 2: Poll for Progress Completion

Since this is a progress step, you need to **poll** the flow status to check if the background task has completed.

**Method 1: GET Request (Recommended for Polling)**
```http
GET /api/config/config_entries/flow/{flow_id}
Authorization: Bearer {access_token}
```

**Method 2: POST Request with Empty Body**
```http
POST /api/config/config_entries/flow/{flow_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{}
```

**Response While Progress is Running:**
```json
{
  "flow_id": "abc123...",
  "handler": "zha",
  "type": "show_progress",
  "step_id": "form_new_network",
  "progress_action": "form_new_network",
  "description": "Forming a new Zigbee network.\n\nWe scan for a clear network channel as part of this process, this can take a minute.",
  "description_placeholders": {}
}
```

**Response When Progress is Complete:**
```json
{
  "flow_id": "abc123...",
  "handler": "zha",
  "type": "show_progress_done",
  "step_id": "form_new_network",
  "next_step_id": "create_entry"
}
```

### Step 3: Advance to `create_entry` Step

When you receive `type: "show_progress_done"` with `next_step_id: "create_entry"`, you need to advance to the next step.

**Request:**
```http
POST /api/config/config_entries/flow/{flow_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{}
```

**Response (Moves to create_entry):**
```json
{
  "flow_id": "abc123...",
  "handler": "zha",
  "type": "create_entry",
  "title": "Zigbee Home Automation",
  "version": 1,
  "minor_version": 1,
  "result": {
    "entry_id": "config_entry_id",
    "domain": "zha",
    "title": "Zigbee Home Automation",
    "source": "user",
    "state": "loaded",
    "created_at": 1234567890.123,
    "modified_at": 1234567890.123,
    "disabled_by": null,
    "pref_disable_new_entities": false,
    "pref_disable_polling": false,
    "supports_options": true,
    "supports_reconfigure": true,
    "supports_unload": true,
    "supports_remove_device": true,
    "num_subentries": 0,
    "supported_subentry_types": {},
    "error_reason_translation_key": null,
    "error_reason_translation_placeholders": null,
    "reason": null
  },
  "description": null,
  "description_placeholders": null,
  "options": {},
  "subentries": []
}
```

**At this point, the config entry is created and ZHA is set up. No additional API call is needed.**

## Complete Flow Example

### 1. Start ZHA Config Flow

```http
POST /api/config/config_entries/flow
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "handler": "zha"
}
```

**Response:**
```json
{
  "flow_id": "flow_123",
  "handler": "zha",
  "type": "form",
  "step_id": "user",
  "data_schema": [...]
}
```

### 2. Complete Initial Steps

Continue submitting user input for each step until you reach `form_new_network`.

### 3. Enter `form_new_network` Step

When you POST to advance to `form_new_network`, the background task starts automatically.

**Request:**
```http
POST /api/config/config_entries/flow/flow_123
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "formation_strategy": "form_new_network"
}
```

**Response (Progress Started):**
```json
{
  "flow_id": "flow_123",
  "handler": "zha",
  "type": "show_progress",
  "step_id": "form_new_network",
  "progress_action": "form_new_network",
  "description": "Forming a new Zigbee network.\n\nWe scan for a clear network channel as part of this process, this can take a minute."
}
```

### 4. Poll for Progress Completion

Poll the flow status every 1-2 seconds until progress is complete.

**Request (Polling):**
```http
GET /api/config/config_entries/flow/flow_123
Authorization: Bearer {access_token}
```

**Response (Still in Progress):**
```json
{
  "flow_id": "flow_123",
  "handler": "zha",
  "type": "show_progress",
  "step_id": "form_new_network",
  "progress_action": "form_new_network"
}
```

**Response (Progress Complete):**
```json
{
  "flow_id": "flow_123",
  "handler": "zha",
  "type": "show_progress_done",
  "step_id": "form_new_network",
  "next_step_id": "create_entry"
}
```

### 5. Advance to `create_entry`

**Request:**
```http
POST /api/config/config_entries/flow/flow_123
Authorization: Bearer {access_token}
Content-Type: application/json

{}
```

**Response (Config Entry Created):**
```json
{
  "flow_id": "flow_123",
  "handler": "zha",
  "type": "create_entry",
  "title": "Zigbee Home Automation",
  "version": 1,
  "minor_version": 1,
  "result": {
    "entry_id": "abc123def456",
    "domain": "zha",
    "title": "Zigbee Home Automation",
    "source": "user",
    "state": "loaded",
    ...
  }
}
```

## Polling Strategy

### Recommended Approach

1. **Initial Poll Interval:** 1-2 seconds
2. **Maximum Wait Time:** 60-90 seconds (network formation can take up to a minute)
3. **Poll Method:** Use `GET /api/config/config_entries/flow/{flow_id}` for efficiency
4. **Stop Condition:** When `type` is not "show_progress"`

### Polling Implementation Example

```javascript
async function pollProgress(flowId, maxWaitTime = 90000) {
  const startTime = Date.now();
  const pollInterval = 2000; // 2 seconds
  
  while (Date.now() - startTime < maxWaitTime) {
    const response = await fetch(
      `/api/config/config_entries/flow/${flowId}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    const result = await response.json();
    
    // Check if progress is complete
    if (result.type === 'show_progress_done') {
      return result; // Progress complete, ready for next step
    }
    
    if (result.type === 'create_entry') {
      return result; // Flow completed, entry created
    }
    
    // Still in progress, wait before next poll
    if (result.type === 'show_progress') {
      await new Promise(resolve => setTimeout(resolve, pollInterval));
      continue;
    }
    
    // Unexpected response type
    throw new Error(`Unexpected flow type: ${result.type}`);
  }
  
  throw new Error('Progress polling timeout');
}
```

## Response Types

### `show_progress`

Indicates a background task is running. Continue polling.

```json
{
  "type": "show_progress",
  "step_id": "form_new_network",
  "progress_action": "form_new_network",
  "description": "..."
}
```

### `show_progress_done`

Indicates the background task is complete. Advance to the next step.

```json
{
  "type": "show_progress_done",
  "step_id": "form_new_network",
  "next_step_id": "create_entry"
}
```

### `create_entry`

Indicates the config entry has been created. Flow is complete.

```json
{
  "type": "create_entry",
  "title": "Zigbee Home Automation",
  "result": {
    "entry_id": "...",
    ...
  }
}
```

## Error Handling

### Flow Not Found

**Status:** `404 Not Found`

**Response:**
```json
{
  "message": "Invalid flow specified"
}
```

**Action:** Flow may have been aborted or expired. Start a new flow.

### Progress Task Failed

If the background task fails, the flow will abort. Check for:

**Response:**
```json
{
  "type": "abort",
  "reason": "error_reason",
  "description": "Error description"
}
```

**Action:** Handle the error and potentially restart the flow.

### Timeout

If progress takes longer than expected:

**Action:** 
1. Continue polling up to the maximum wait time (90 seconds)
2. If timeout occurs, check if the flow still exists
3. If flow exists, continue polling
4. If flow doesn't exist, the task may have failed - restart the flow

## WebSocket APIs (Read-Only)

While you cannot submit flow steps via WebSocket, you can use WebSocket to receive notifications:

### Subscribe to Config Entry Changes

**Command:** `config_entries/subscribe`

**Request:**
```json
{
  "id": 1,
  "type": "config_entries/subscribe",
  "type_filter": ["hub"]
}
```

**Events:**
```json
{
  "id": 1,
  "type": "event",
  "event": [
    {
      "type": "create",
      "entry": {
        "entry_id": "abc123def456",
        "domain": "zha",
        "title": "Zigbee Home Automation",
        ...
      }
    }
  ]
}
```

### Get Flow Progress (Read-Only)

**Command:** `config_entries/flow/progress`

**Request:**
```json
{
  "id": 2,
  "type": "config_entries/flow/progress"
}
```

**Response:**
```json
{
  "id": 2,
  "type": "result",
  "success": true,
  "result": [
    {
      "flow_id": "flow_123",
      "handler": "zha",
      "step_id": "form_new_network",
      "context": {
        "source": "user"
      }
    }
  ]
}
```

**Note:** This only shows flows not started by a user (e.g., discovered devices). User-initiated flows are not included.

## Key Points

1. **No User Input Required:** The `form_new_network` step does not require any payload - it's a progress step that runs automatically.

2. **Polling Required:** You must poll the flow status using `GET` or `POST` (empty body) to check if progress is complete.

3. **Empty Body for POST:** When advancing from `show_progress_done` to the next step, use an empty JSON object `{}` as the request body.

4. **REST API Only:** Config flow steps cannot be submitted via WebSocket. Use REST API for all flow operations.

5. **Automatic Transition:** When progress completes, the flow automatically transitions to `create_entry` step. You just need to advance it with an empty POST.

6. **Entry Created Automatically:** When you receive `type: "create_entry"`, the config entry is already created - no additional API call needed.

## Code References

**ZHA Config Flow:**
- `homeassistant/components/zha/config_flow.py:665-687` - `async_step_form_new_network()` method

**Progress Step Handling:**
- `homeassistant/data_entry_flow.py:838-875` - `async_show_progress()` method
- `homeassistant/data_entry_flow.py:897-910` - `async_show_progress_done()` method
- `homeassistant/data_entry_flow.py:328-437` - `async_configure()` method (handles progress steps)

**REST API:**
- `homeassistant/helpers/data_entry_flow.py:104-129` - `FlowManagerResourceView` (GET and POST handlers)

**Test Example:**
- `tests/components/zha/test_config_flow.py:191-215` - `consume_progress_flow()` helper function

## Summary

When `step_id` is `form_new_network`:

1. **No Payload Needed:** This is a progress step - no user input required
2. **Poll for Completion:** Use `GET /api/config/config_entries/flow/{flow_id}` to check progress
3. **Advance When Done:** When you receive `show_progress_done`, POST with empty body `{}` to advance
4. **Entry Created:** When you receive `create_entry`, the ZHA config entry is already created
5. **REST API Only:** All flow operations must use REST API, not WebSocket

The complete flow: `form_new_network` (progress) → `create_entry` (automatic) → Config entry created



