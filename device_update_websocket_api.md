# Device Registry Update WebSocket API Documentation

## Overview

The Device Registry Update WebSocket API allows you to update device properties in Home Assistant, including the device area assignment and user-friendly name. This API is part of the Home Assistant WebSocket API and requires administrative privileges.

## Endpoint

**Command Type:** `config/device_registry/update`

**Protocol:** WebSocket

**Authentication:** Required (via WebSocket authentication)

**Authorization:** Admin privileges required

## Request Format

### Message Structure

The request must be sent as a JSON object through the WebSocket connection with the following structure:

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique message identifier for correlating request and response |
| `type` | string | Must be `"config/device_registry/update"` |
| `device_id` | string | Unique identifier of the device to update (required) |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `area_id` | string \| null | Area identifier to assign the device to. Set to `null` to remove area assignment |
| `name_by_user` | string \| null | User-friendly custom name for the device. Set to `null` to remove custom name |
| `labels` | array of strings | List of label identifiers to assign to the device |
| `disabled_by` | string \| null | Device disabler value. Only `"user"` is allowed via API, or `null` to enable the device |

## Field Details

### device_id

- **Type:** string
- **Required:** Yes
- **Description:** The unique device identifier in the device registry. This can be obtained from the device registry list command or from device entries.
- **Example:** `"abc123def456..."`

### area_id

- **Type:** string or null
- **Required:** No
- **Description:** The unique identifier of an area to assign the device to. The area must exist in the area registry. Setting this to `null` removes the device's area assignment.
- **Behavior:**
  - If provided as a string, assigns the device to that area
  - If provided as `null`, removes the area assignment
  - If omitted, the area assignment remains unchanged
- **Example:** `"area_kitchen"` or `null`

### name_by_user

- **Type:** string or null
- **Required:** No
- **Description:** A user-friendly custom name for the device. This is separate from the device's default name (which is set by the integration). Setting this to `null` removes the custom name.
- **Behavior:**
  - If provided as a string, sets the custom user name
  - If provided as `null`, removes the custom name
  - If omitted, the custom name remains unchanged
- **Note:** This is different from the device's `name` property, which is managed by the integration and cannot be changed via this API
- **Example:** `"Kitchen Temperature Sensor"` or `null`

### labels

- **Type:** array of strings
- **Required:** No
- **Description:** A list of label identifiers to assign to the device. Labels must exist in the label registry.
- **Behavior:**
  - If provided, replaces all existing labels with the provided list
  - If omitted, labels remain unchanged
- **Example:** `["label_bedroom", "label_sensor"]`

### disabled_by

- **Type:** string or null
- **Required:** No
- **Description:** Controls whether the device is disabled. Only the value `"user"` is allowed via the API to disable a device, or `null` to enable it.
- **Allowed Values:**
  - `"user"` - Disables the device (user-initiated)
  - `null` - Enables the device (removes user disable)
- **Note:** Other disable reasons (such as `"config_entry"`) cannot be set via this API
- **Example:** `"user"` or `null`

## Response Format

### Success Response

When the update is successful, the server responds with:

**Response Type:** `result`

**Structure:**
```json
{
  "id": <request_id>,
  "type": "result",
  "success": true,
  "result": {
    // Device entry dictionary representation
    // Contains all device properties including updated values
  }
}
```

**Response Fields:**
- `id`: Matches the request message ID
- `type`: Always `"result"` for successful operations
- `success`: Always `true` for successful operations
- `result`: Dictionary containing the complete updated device entry with all properties

### Error Response

If an error occurs, the server responds with:

**Response Type:** `result`

**Structure:**
```json
{
  "id": <request_id>,
  "type": "result",
  "success": false,
  "error": {
    "code": "<error_code>",
    "message": "<error_message>"
  }
}
```

**Common Error Codes:**
- `invalid_info`: Invalid parameter value or device not found
- `unauthorized`: Authentication required or insufficient privileges
- `unknown_error`: Unexpected server error

## Authentication

### WebSocket Authentication Flow

1. **Connection:** Establish WebSocket connection to `/api/websocket`
2. **Auth Required:** Server sends `{"type": "auth_required"}`
3. **Authenticate:** Send authentication message:
   ```json
   {
     "type": "auth",
     "access_token": "<your_access_token>"
   }
   ```
4. **Auth Confirmation:** Server responds with `{"type": "auth_ok"}`
5. **Send Commands:** After authentication, you can send device update commands

### Authorization Requirements

- **Admin Access Required:** The user account must have administrative privileges
- **Token Permissions:** The access token must have sufficient permissions for device registry modifications

## Usage Notes

### Partial Updates

- Only include fields you want to update
- Omitted fields remain unchanged
- You can update a single field or multiple fields in one request

### Area Assignment

- The `area_id` must reference an existing area in the area registry
- Use `null` to remove area assignment
- To find available areas, use the `config/area_registry/list` command

### Name Management

- `name_by_user` is the user-customizable name
- The device's `name` property (set by integrations) cannot be changed via this API
- Setting `name_by_user` to `null` removes the custom name, reverting to the integration-set name

### Labels

- Labels are replaced entirely when provided (not merged)
- All labels must exist in the label registry
- To remove all labels, send an empty array: `[]`

### Device Disabling

- Only user-initiated disabling is allowed via this API
- Other disable reasons (like config entry issues) cannot be set or cleared via this API
- Setting `disabled_by` to `null` enables a user-disabled device

### Data Types

- All string values must be valid UTF-8
- Array values (like `labels`) are converted to sets internally
- `null` values are explicitly supported for optional fields to clear values

## Related APIs

### List Devices

**Command:** `config/device_registry/list`

**Description:** Retrieve all devices in the registry to find device IDs and current properties.

### List Areas

**Command:** `config/area_registry/list`

**Description:** Retrieve all areas in the registry to find valid area IDs for assignment.

### List Labels

**Command:** `config/label_registry/list`

**Description:** Retrieve all labels in the registry to find valid label IDs for assignment.

## Implementation Details

### Server-Side Processing

1. **Validation:** The server validates all provided parameters
2. **Authorization Check:** Verifies admin privileges
3. **Registry Update:** Updates the device registry entry
4. **Data Conversion:**
   - `labels` array is converted to a set
   - `disabled_by` string is converted to `DeviceEntryDisabler` enum if provided
5. **Response:** Returns the updated device entry dictionary representation

### Event Broadcasting

When a device is updated, Home Assistant broadcasts a `device_registry_updated` event with:
- `action`: `"update"`
- `device_id`: The updated device identifier
- `changes`: Dictionary of changed fields

This allows other components and integrations to react to device changes.

## Limitations

1. **Read-Only Fields:** Some device properties (like `name`, `manufacturer`, `model`, etc.) are set by integrations and cannot be modified via this API
2. **Admin Only:** Requires administrative privileges
3. **Limited Disable Control:** Only user-initiated disabling is supported
4. **Area Validation:** Area must exist in the area registry
5. **Label Validation:** All labels must exist in the label registry

## Best Practices

1. **Get Device ID First:** Use `config/device_registry/list` to find the correct `device_id`
2. **Validate Areas:** Verify area exists before assigning
3. **Incremental Updates:** Update only the fields that need to change
4. **Error Handling:** Always check the `success` field in responses
5. **Idempotency:** The same update can be sent multiple times safely
6. **Null Values:** Use `null` explicitly to clear optional fields rather than omitting them

## Version Information

- **API Version:** Part of Home Assistant core WebSocket API
- **Minimum Home Assistant Version:** Available in all modern Home Assistant versions
- **Stability:** Stable API, changes are backward compatible

