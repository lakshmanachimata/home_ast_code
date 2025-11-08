# Get Devices by Area API Documentation

## Overview

This document provides comprehensive information about retrieving devices assigned to one or more areas in Home Assistant. The device registry API allows you to query devices and filter them by area assignment.

## API Availability

### WebSocket API
- **Available:** Yes
- **Primary Method:** WebSocket commands
- **Filtering:** Client-side filtering required

### REST API
- **Available:** No
- **Note:** Home Assistant does not provide REST API endpoints for device registry operations. All device registry access is through the WebSocket API.

## WebSocket API

### Endpoint

**Command Type:** `config/device_registry/list`

**Protocol:** WebSocket

**Authentication:** Required (via WebSocket authentication)

**Authorization:** No special privileges required (read-only operation)

### Request Format

#### Message Structure

The request is sent as a JSON object through the WebSocket connection:

**Required Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique message identifier for correlating request and response |
| `type` | string | Must be `"config/device_registry/list"` |

**Request Example:**
```json
{
  "id": 1,
  "type": "config/device_registry/list"
}
```

### Response Format

#### Success Response

The server responds with a JSON object containing an array of all devices:

**Response Structure:**
```json
{
  "id": <request_id>,
  "type": "result",
  "success": true,
  "result": [
    {
      "id": "device_id_1",
      "area_id": "area_kitchen",
      "name": "Kitchen Temperature Sensor",
      "name_by_user": null,
      "manufacturer": "Sensor Corp",
      "model": "TempSensor Pro",
      "identifiers": [["domain", "unique_id"]],
      "connections": [],
      "config_entries": ["config_entry_id"],
      "disabled_by": null,
      "entry_type": null,
      "labels": [],
      "created_at": 1234567890.123,
      "modified_at": 1234567890.123,
      "sw_version": "1.0.0",
      "hw_version": null,
      "serial_number": null,
      "configuration_url": null,
      "via_device_id": null
    },
    {
      "id": "device_id_2",
      "area_id": "area_living_room",
      "name": "Living Room Light",
      ...
    }
  ]
}
```

#### Device Entry Fields

Each device in the response array contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique device identifier |
| `area_id` | string \| null | Area identifier if device is assigned to an area, `null` otherwise |
| `name` | string | Device name (set by integration) |
| `name_by_user` | string \| null | User-customizable name, `null` if not set |
| `manufacturer` | string \| null | Device manufacturer |
| `model` | string \| null | Device model |
| `identifiers` | array of arrays | List of identifier tuples `[["domain", "unique_id"], ...]` |
| `connections` | array of arrays | List of connection tuples `[["connection_type", "value"], ...]` |
| `config_entries` | array of strings | List of configuration entry IDs associated with this device |
| `disabled_by` | string \| null | Disabler type if device is disabled, `null` if enabled |
| `entry_type` | string \| null | Device entry type (e.g., `"service"`) |
| `labels` | array of strings | List of label identifiers assigned to the device |
| `created_at` | number | Timestamp when device was created (Unix timestamp with decimals) |
| `modified_at` | number | Timestamp when device was last modified (Unix timestamp with decimals) |
| `sw_version` | string \| null | Software version |
| `hw_version` | string \| null | Hardware version |
| `serial_number` | string \| null | Serial number |
| `configuration_url` | string \| null | URL to device configuration page |
| `via_device_id` | string \| null | Device ID of parent device if this device is connected via another device |

### Filtering by Area

Since the WebSocket API returns all devices, filtering by area must be performed client-side. The `area_id` field in each device entry is used for filtering.

#### Single Area Filtering

To get devices for a single area:

1. Send `config/device_registry/list` request
2. Receive all devices
3. Filter devices where `area_id` matches the target area ID

**Filtering Logic:**
- Include devices where `device.area_id === "target_area_id"`
- Exclude devices where `device.area_id === null`
- Exclude devices where `device.area_id !== "target_area_id"`

#### Multiple Areas Filtering

To get devices for multiple areas in a single request:

1. Send `config/device_registry/list` request
2. Receive all devices
3. Filter devices where `area_id` is in the list of target area IDs

**Filtering Logic:**
- Include devices where `device.area_id` is in the array of target area IDs
- Exclude devices where `device.area_id === null`
- Exclude devices where `device.area_id` is not in the target list

**Example Filter Array:**
```javascript
const targetAreas = ["area_kitchen", "area_living_room", "area_bedroom"];
const filteredDevices = allDevices.filter(device => 
  device.area_id !== null && targetAreas.includes(device.area_id)
);
```

### Getting Area IDs

To obtain valid area IDs for filtering, use the area registry list command:

**Command:** `config/area_registry/list`

**Request:**
```json
{
  "id": 2,
  "type": "config/area_registry/list"
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
      "area_id": "area_kitchen",
      "name": "Kitchen",
      "aliases": [],
      "picture": null,
      "icon": null,
      "floor_id": null,
      "labels": [],
      "temperature_entity_id": null,
      "humidity_entity_id": null
    },
    {
      "area_id": "area_living_room",
      "name": "Living Room",
      ...
    }
  ]
}
```

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
5. **Send Commands:** After authentication, you can send device list commands

### Authorization Requirements

- **Read Access:** No special privileges required for listing devices
- **Token Permissions:** Standard access token with read permissions is sufficient

## Usage Patterns

### Pattern 1: Get Devices for Single Area

**Steps:**
1. Authenticate via WebSocket
2. Send `config/device_registry/list` command
3. Filter response by `area_id === "target_area_id"`

**Result:** Array of devices assigned to the specified area

### Pattern 2: Get Devices for Multiple Areas

**Steps:**
1. Authenticate via WebSocket
2. Send `config/device_registry/list` command
3. Filter response by `area_id` in array of target area IDs

**Result:** Array of devices assigned to any of the specified areas

### Pattern 3: Get Devices Without Area Assignment

**Steps:**
1. Authenticate via WebSocket
2. Send `config/device_registry/list` command
3. Filter response by `area_id === null`

**Result:** Array of devices not assigned to any area

### Pattern 4: Get All Devices (No Filtering)

**Steps:**
1. Authenticate via WebSocket
2. Send `config/device_registry/list` command
3. Use entire response array

**Result:** Array of all devices in the system

## Response Processing

### Handling Empty Results

- If no devices match the area filter, the filtered result will be an empty array `[]`
- This is not an error condition

### Handling Null Area IDs

- Devices with `area_id === null` are not assigned to any area
- These devices should be excluded when filtering by specific areas
- To include unassigned devices, explicitly check for `null` values

### Performance Considerations

1. **Single Request:** The API returns all devices in one request, which is efficient
2. **Client-Side Filtering:** Filtering is performed on the client, which is fast for typical device counts
3. **Caching:** Consider caching the full device list if multiple area queries are needed
4. **Incremental Updates:** Use WebSocket subscriptions to receive device updates instead of polling

## Error Handling

### Error Response Format

If an error occurs, the server responds with:

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

### Common Error Codes

- `invalid_format`: Invalid request format
- `unauthorized`: Authentication required or invalid token
- `unknown_error`: Unexpected server error

## Related APIs

### List Areas

**Command:** `config/area_registry/list`

**Description:** Retrieve all areas in the registry to obtain valid area IDs for filtering.

### List Entities

**Command:** `config/entity_registry/list`

**Description:** Retrieve all entities. Entities also have `area_id` fields and can be filtered similarly.

### Update Device

**Command:** `config/device_registry/update`

**Description:** Update device properties, including area assignment. Requires admin privileges.

## Implementation Details

### Server-Side Processing

1. **Registry Access:** Server accesses the device registry
2. **Serialization:** All device entries are serialized to JSON using cached `json_repr` property
3. **Response Building:** Response is built efficiently using byte concatenation for performance
4. **No Filtering:** Server does not perform area filtering - all devices are returned

### Client-Side Filtering

Since filtering is performed client-side, you have full control over:

1. **Filter Logic:** Implement custom filtering logic beyond simple area matching
2. **Combined Filters:** Combine area filtering with other criteria (manufacturer, model, labels, etc.)
3. **Performance:** Optimize filtering for your specific use case
4. **Caching:** Cache and reuse the full device list for multiple queries

### Device Registry Structure

The device registry maintains an internal index by `area_id` for efficient lookups, but this is not exposed via the API. The API returns all devices, and clients perform filtering.

## Best Practices

### 1. Cache Device List

If you need to query devices for multiple areas:
- Fetch the full device list once
- Cache it locally
- Filter from the cached list for different area queries
- Refresh cache periodically or on device registry update events

### 2. Validate Area IDs

Before filtering:
- Use `config/area_registry/list` to get valid area IDs
- Validate that target area IDs exist
- Handle cases where area IDs might have been deleted

### 3. Handle Null Values

When filtering:
- Explicitly check for `null` area IDs
- Decide whether to include or exclude unassigned devices
- Document your filtering behavior

### 4. Error Handling

Always:
- Check the `success` field in responses
- Handle error responses appropriately
- Implement retry logic for transient errors
- Log errors for debugging

### 5. Performance Optimization

For large installations:
- Consider pagination if implementing custom endpoints
- Use WebSocket subscriptions for real-time updates
- Implement debouncing for rapid successive queries
- Cache area-to-device mappings if frequently accessed

## Limitations

1. **No Server-Side Filtering:** The API does not support filtering parameters - all devices are returned
2. **No REST API:** Device registry operations are WebSocket-only
3. **No Pagination:** All devices are returned in a single response
4. **Client-Side Processing:** Filtering logic must be implemented client-side
5. **No Incremental Queries:** Cannot request only devices that changed since last query

## Alternative Approaches

### WebSocket Subscriptions

For real-time device updates, consider subscribing to device registry events:

**Event Type:** `device_registry_updated`

**Event Data:**
```json
{
  "action": "update",
  "device_id": "device_id",
  "changes": {
    "area_id": ["old_area_id", "new_area_id"]
  }
}
```

This allows you to:
- Maintain a local cache of devices
- Update the cache incrementally
- Filter from the cached data without repeated API calls

### Template Functions

Home Assistant templates provide helper functions:

- `area_devices(hass, area_id_or_name)`: Returns device IDs for an area
- `area_entities(hass, area_id_or_name)`: Returns entity IDs for an area

These are available in templates and automation scripts but not via external APIs.

## Version Information

- **API Version:** Part of Home Assistant core WebSocket API
- **Minimum Home Assistant Version:** Available in all modern Home Assistant versions
- **Stability:** Stable API, changes are backward compatible
- **Response Format:** Device entry format may evolve, but `area_id` field remains consistent

## Summary

To get devices for one or more areas:

1. **Use WebSocket API:** `config/device_registry/list`
2. **Authenticate:** Provide access token via WebSocket authentication
3. **Receive All Devices:** API returns complete device list
4. **Filter Client-Side:** Filter devices by `area_id` field
5. **Handle Nulls:** Decide how to handle devices without area assignment

The API is efficient for typical use cases, returning all devices in a single request. Client-side filtering provides flexibility for custom filtering logic while maintaining API simplicity.

