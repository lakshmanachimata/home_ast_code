# Config Entry Creation API Documentation

## Overview

When a config flow reaches the `create_entry` step, it means the flow is ready to create a config entry (which represents a device or integration instance). The config entry is **automatically created** when you submit the final step of the flow - there is no separate API call needed to "add the device to the system."

## REST API Endpoint

### Submit Config Flow Step

**Endpoint:** `POST /api/config/config_entries/flow/{flow_id}`

**Authentication:** Requires admin privileges (`CAT_CONFIG_ENTRIES` permission with "add" permission)

**Purpose:** Submit user input for the current step of a config flow. When the flow completes and returns `type: "create_entry"`, the config entry is automatically created.

**URL Parameters:**
- `flow_id` (string, required): The unique identifier of the config flow

**Request Body:**
```json
{
  "user_input_field_1": "value1",
  "user_input_field_2": "value2",
  // ... other fields as required by the current step's schema
}
```

**Request Body Schema:**
- The request body must match the `data_schema` returned in the previous flow step response
- Fields are validated against the schema defined by the integration's config flow
- Empty body `{}` is allowed if the current step doesn't require user input

**Response (Success - Flow Continues):**
```json
{
  "flow_id": "abc123...",
  "handler": "integration_domain",
  "type": "form",
  "step_id": "next_step",
  "data_schema": [
    {
      "name": "field_name",
      "required": true,
      "type": "string"
    }
  ],
  "errors": {},
  "description": "Step description",
  "description_placeholders": {}
}
```

**Response (Success - Config Entry Created):**
```json
{
  "flow_id": "abc123...",
  "handler": "integration_domain",
  "type": "create_entry",
  "title": "Device Name",
  "version": 1,
  "minor_version": 1,
  "result": {
    "entry_id": "config_entry_id",
    "domain": "integration_domain",
    "title": "Device Name",
    "source": "user",
    "state": "loaded",
    "created_at": 1234567890.123,
    "modified_at": 1234567890.123,
    "disabled_by": null,
    "pref_disable_new_entities": false,
    "pref_disable_polling": false,
    "supports_options": false,
    "supports_reconfigure": false,
    "supports_unload": false,
    "supports_remove_device": false,
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

**Response (Error - Validation Failed):**
```json
{
  "errors": {
    "field_name": ["Error message"],
    "base": ["General error message"]
  }
}
```

**Response (Error - Flow Not Found):**
```json
{
  "message": "Invalid flow specified"
}
```

**HTTP Status Codes:**
- `200 OK`: Flow step processed successfully
- `400 Bad Request`: Invalid data or validation errors
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Flow not found

## Flow Process

### Step 1: Initialize Config Flow

**Endpoint:** `POST /api/config/config_entries/flow`

**Request Body:**
```json
{
  "handler": "integration_domain",
  "show_advanced_options": false
}
```

**Response:**
```json
{
  "flow_id": "abc123...",
  "handler": "integration_domain",
  "type": "form",
  "step_id": "user",
  "data_schema": [...],
  "errors": {}
}
```

### Step 2-N: Continue Flow Steps

**Endpoint:** `POST /api/config/config_entries/flow/{flow_id}`

Submit user input for each step until the flow completes.

### Final Step: Create Entry

When you POST to `/api/config/config_entries/flow/{flow_id}` with the final step's user input:

1. **The system automatically:**
   - Validates the user input
   - Creates the config entry
   - Calls the integration's `async_setup_entry()` method
   - Registers devices and entities
   - Returns the created config entry in the response

2. **Response includes:**
   - `type: "create_entry"` - Indicates entry was created
   - `result` - Contains the full config entry object
   - `entry_id` - Unique identifier for the created entry

3. **No additional API call is needed** - The device/integration is now added to the system.

## Example: Complete Flow

### 1. Start Flow
```bash
POST /api/config/config_entries/flow
{
  "handler": "met"
}
```

**Response:**
```json
{
  "flow_id": "flow_123",
  "handler": "met",
  "type": "form",
  "step_id": "user",
  "data_schema": [
    {
      "name": "name",
      "required": true,
      "type": "string"
    },
    {
      "name": "latitude",
      "required": true,
      "type": "float"
    },
    {
      "name": "longitude",
      "required": true,
      "type": "float"
    }
  ]
}
```

### 2. Submit User Input
```bash
POST /api/config/config_entries/flow/flow_123
{
  "name": "Home",
  "latitude": 59.9139,
  "longitude": 10.7522
}
```

**Response (Config Entry Created):**
```json
{
  "flow_id": "flow_123",
  "handler": "met",
  "type": "create_entry",
  "title": "Home",
  "version": 1,
  "minor_version": 1,
  "result": {
    "entry_id": "abc123def456",
    "domain": "met",
    "title": "Home",
    "source": "user",
    "state": "loaded",
    "created_at": 1234567890.123,
    "modified_at": 1234567890.123,
    ...
  }
}
```

**At this point, the config entry is created and the integration is set up. No additional API call is needed.**

## WebSocket API

Home Assistant does **not** provide a WebSocket API for submitting config flow steps. The WebSocket APIs available are:

### 1. Subscribe to Config Entry Changes

**Command:** `config_entries/subscribe`

**Purpose:** Receive notifications when config entries are created, updated, or removed

**Request:**
```json
{
  "id": 1,
  "type": "config_entries/subscribe",
  "type_filter": ["device", "hub", "service"]
}
```

**Response:**
```json
{
  "id": 1,
  "type": "result",
  "success": true,
  "result": null
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
        "domain": "met",
        "title": "Home",
        ...
      }
    }
  ]
}
```

### 2. Get Config Flow Progress

**Command:** `config_entries/flow/progress`

**Purpose:** List flows that are in progress but not started by a user (e.g., discovered devices)

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
      "handler": "met",
      "step_id": "user",
      "context": {
        "source": "zeroconf"
      }
    }
  ]
}
```

### 3. Subscribe to Config Flow Changes

**Command:** `config_entries/flow/subscribe`

**Purpose:** Receive notifications when non-user flows are initiated or removed

**Request:**
```json
{
  "id": 3,
  "type": "config_entries/flow/subscribe"
}
```

## Key Points

1. **No Separate "Add Device" API:** When `stepId` is `create_entry`, submitting the final step data automatically creates the config entry. There is no separate API endpoint to "add the device."

2. **REST API Only:** Config flow submission is only available via REST API (`POST /api/config/config_entries/flow/{flow_id}`), not WebSocket.

3. **Automatic Setup:** When a config entry is created:
   - The integration's `async_setup_entry()` method is called
   - Devices and entities are automatically registered
   - The entry appears in the device registry

4. **Response Indicates Success:** The response with `type: "create_entry"` confirms the entry was created. The `result` field contains the full config entry object.

5. **WebSocket for Notifications:** Use `config_entries/subscribe` to receive real-time notifications when config entries are created, but you cannot submit flow steps via WebSocket.

## Code References

**REST API Implementation:**
- `homeassistant/components/config/config_entries.py:218-240` - `ConfigManagerFlowResourceView`
- `homeassistant/helpers/data_entry_flow.py:101-139` - `FlowManagerResourceView`

**Config Entry Creation:**
- `homeassistant/config_entries.py:1547-1709` - `async_finish_flow()` method
- `homeassistant/config_entries.py:3204-3235` - `async_create_entry()` method

**Flow Processing:**
- `homeassistant/data_entry_flow.py:328-397` - `async_configure()` method

## Error Handling

### Common Errors

1. **Invalid Flow ID:**
   - Status: `404 Not Found`
   - Message: `"Invalid flow specified"`

2. **Validation Errors:**
   - Status: `400 Bad Request`
   - Response includes `errors` object with field-specific errors

3. **Permission Denied:**
   - Status: `403 Forbidden`
   - Requires admin user with `CAT_CONFIG_ENTRIES` permission

4. **Flow Already Completed:**
   - Status: `404 Not Found`
   - Flow may have been completed or aborted

## Best Practices

1. **Store Flow ID:** Keep track of the `flow_id` returned when initializing the flow
2. **Handle Multi-Step Flows:** Some integrations require multiple steps - continue submitting until `type: "create_entry"` is returned
3. **Validate Input:** Check the `data_schema` in each step response to ensure you're sending the correct fields
4. **Error Recovery:** If validation fails, fix the errors and resubmit to the same `flow_id`
5. **Subscribe to Changes:** Use `config_entries/subscribe` WebSocket command to receive real-time updates about config entry creation

## Summary

When `stepId` is `create_entry`:
- **Use REST API:** `POST /api/config/config_entries/flow/{flow_id}`
- **Submit final step data** in the request body
- **Config entry is automatically created** - no separate API call needed
- **Response confirms creation** with `type: "create_entry"` and the entry in `result`
- **WebSocket is for notifications only** - cannot submit flow steps via WebSocket

