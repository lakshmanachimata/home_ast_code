# Get Device Details from Config Entry ID - API Documentation

## Overview

This document provides comprehensive information about retrieving device details associated with a specific config entry ID in Home Assistant. Config entries represent integration instances, and each entry can be associated with one or more devices.

## API Availability

### WebSocket API
- **Available:** Yes
- **Primary Method:** WebSocket commands
- **Filtering:** Client-side filtering required

### REST API
- **Available:** No
- **Note:** Home Assistant does not provide REST API endpoints for device registry operations. All device registry access is through the WebSocket API.

## Approach

Since there is no direct API endpoint that accepts an `entry_id` and returns devices, you must:

1. **Get all devices** using `config/device_registry/list`
2. **Filter client-side** by checking if the `entry_id` is in each device's `config_entries` array
3. **Optionally get entities** associated with those devices using `config/entity_registry/list`

## Step 1: Get Config Entry Details

### WebSocket Command

**Command Type:** `config_entries/get_single`

**Purpose:** Get the config entry details (optional, but useful for validation)

**Request:**
```json
{
  "id": 1,
  "type": "config_entries/get_single",
  "entry_id": "abc123def456"
}
```

**Response:**
```json
{
  "id": 1,
  "type": "result",
  "success": true,
  "result": {
    "config_entry": {
      "entry_id": "abc123def456",
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
    }
  }
}
```

**Authorization:** Requires admin privileges

## Step 2: Get All Devices

### WebSocket Command

**Command Type:** `config/device_registry/list`

**Purpose:** Retrieve all devices in the system

**Request:**
```json
{
  "id": 2,
  "type": "config/device_registry/list"
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
      "id": "device_1",
      "config_entries": ["abc123def456", "xyz789"],
      "connections": [],
      "identifiers": [["zha", "00:11:22:33:44:55:66:77"]],
      "manufacturer": "Texas Instruments",
      "model": "CC2531",
      "name": "Zigbee Coordinator",
      "name_by_user": null,
      "sw_version": "2.1.0",
      "area_id": "living_room",
      "entry_type": null,
      "disabled_by": null,
      "via_device_id": null,
      "labels": []
    },
    {
      "id": "device_2",
      "config_entries": ["abc123def456"],
      "connections": [],
      "identifiers": [["zha", "aa:bb:cc:dd:ee:ff"]],
      "manufacturer": "Philips",
      "model": "Hue Bulb",
      "name": "Living Room Light",
      "name_by_user": null,
      "sw_version": "1.0.0",
      "area_id": "living_room",
      "entry_type": null,
      "disabled_by": null,
      "via_device_id": "device_1",
      "labels": []
    }
  ]
}
```

**Authorization:** No special privileges required (read-only operation)

## Step 3: Filter Devices by Entry ID

### Client-Side Filtering

After receiving all devices, filter them to find devices associated with your config entry ID:

**JavaScript Example:**
```javascript
const entryId = "abc123def456";
const allDevices = response.result; // From config/device_registry/list

const devicesForEntry = allDevices.filter(device => 
  device.config_entries && device.config_entries.includes(entryId)
);
```

**Python Example:**
```python
entry_id = "abc123def456"
all_devices = response["result"]  # From config/device_registry/list

devices_for_entry = [
    device for device in all_devices
    if device.get("config_entries") and entry_id in device.get("config_entries", [])
]
```

## Step 4: Get Entities for Devices (Optional)

### WebSocket Command

**Command Type:** `config/entity_registry/list`

**Purpose:** Retrieve all entities, then filter by device IDs

**Request:**
```json
{
  "id": 3,
  "type": "config/entity_registry/list"
}
```

**Response:**
```json
{
  "id": 3,
  "type": "result",
  "success": true,
  "result": [
    {
      "entity_id": "sensor.living_room_temperature",
      "device_id": "device_2",
      "config_entry_id": "abc123def456",
      "name": "Temperature",
      "original_name": "Temperature",
      "platform": "zha",
      "domain": "sensor",
      "device_class": "temperature",
      "unit_of_measurement": "°C",
      "disabled_by": null,
      "hidden_by": null,
      "entity_category": null,
      "has_entity_name": true,
      "unique_id": "aa:bb:cc:dd:ee:ff:temperature"
    }
  ]
}
```

### Filter Entities by Device IDs

**JavaScript Example:**
```javascript
const deviceIds = devicesForEntry.map(device => device.id);
const allEntities = entityResponse.result; // From config/entity_registry/list

const entitiesForDevices = allEntities.filter(entity =>
  entity.device_id && deviceIds.includes(entity.device_id)
);
```

**Python Example:**
```python
device_ids = [device["id"] for device in devices_for_entry]
all_entities = entity_response["result"]  # From config/entity_registry/list

entities_for_devices = [
    entity for entity in all_entities
    if entity.get("device_id") and entity["device_id"] in device_ids
]
```

## Complete Example Workflow

### 1. Get Config Entry (Validation)

```json
{
  "id": 1,
  "type": "config_entries/get_single",
  "entry_id": "abc123def456"
}
```

### 2. Get All Devices

```json
{
  "id": 2,
  "type": "config/device_registry/list"
}
```

### 3. Filter Devices

```javascript
const entryId = "abc123def456";
const devices = response.result.filter(device =>
  device.config_entries && device.config_entries.includes(entryId)
);
```

### 4. Get All Entities (Optional)

```json
{
  "id": 3,
  "type": "config/entity_registry/list"
}
```

### 5. Filter Entities by Device IDs

```javascript
const deviceIds = devices.map(d => d.id);
const entities = entityResponse.result.filter(entity =>
  entity.device_id && deviceIds.includes(entity.device_id)
);
```

## Device Entry Fields

Each device entry contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique device identifier |
| `config_entries` | array[string] | Array of config entry IDs associated with this device |
| `connections` | array[array[string]] | Device connections (e.g., MAC address, serial number) |
| `identifiers` | array[array[string]] | Device identifiers (domain, unique_id pairs) |
| `manufacturer` | string \| null | Device manufacturer name |
| `model` | string \| null | Device model name |
| `model_id` | string \| null | Model identifier |
| `name` | string | Device name |
| `name_by_user` | string \| null | User-customizable name |
| `sw_version` | string \| null | Software/firmware version |
| `hw_version` | string \| null | Hardware version |
| `serial_number` | string \| null | Serial number |
| `area_id` | string \| null | Area assignment |
| `entry_type` | string \| null | Device type (`"service"` or `null`) |
| `disabled_by` | string \| null | Disabled reason (`"user"`, `"integration"`, etc.) |
| `via_device_id` | string \| null | Parent device ID (for sub-devices) |
| `configuration_url` | string \| null | URL to device configuration |
| `labels` | array[string] | Device labels |

## Entity Entry Fields

Each entity entry contains:

| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | string | Full entity ID (e.g., `"sensor.temperature"`) |
| `device_id` | string \| null | Associated device ID |
| `config_entry_id` | string \| null | Config entry ID that created this entity |
| `name` | string \| null | Entity name |
| `original_name` | string \| null | Original name set by integration |
| `platform` | string | Integration platform name |
| `domain` | string | Entity domain (sensor, switch, light, etc.) |
| `device_class` | string \| null | Device class (e.g., `"temperature"`, `"battery"`) |
| `unit_of_measurement` | string \| null | Unit of measurement |
| `disabled_by` | string \| null | Disabled reason |
| `hidden_by` | string \| null | Hidden reason |
| `entity_category` | string \| null | Category (`"diagnostic"`, `"config"`, or `null`) |
| `has_entity_name` | boolean | Whether entity has a name |
| `unique_id` | string | Unique identifier for the entity |

## Alternative: Filter Entities by Config Entry ID

You can also filter entities directly by `config_entry_id`:

**JavaScript Example:**
```javascript
const entryId = "abc123def456";
const allEntities = entityResponse.result;

const entitiesForEntry = allEntities.filter(entity =>
  entity.config_entry_id === entryId
);

// Then get unique device IDs from entities
const deviceIds = [...new Set(
  entitiesForEntry
    .map(entity => entity.device_id)
    .filter(id => id !== null)
)];

// Get devices for those device IDs
const devices = allDevices.filter(device =>
  deviceIds.includes(device.id)
);
```

## REST API Alternative

While there is no REST API for device registry operations, you can use REST API to get config entry details:

### Get Config Entry

**Endpoint:** `GET /api/config/config_entries/entry/{entry_id}`

**Request:**
```http
GET /api/config/config_entries/entry/abc123def456
Authorization: Bearer {access_token}
```

**Response:**
```json
[
  {
    "entry_id": "abc123def456",
    "domain": "zha",
    "title": "Zigbee Home Automation",
    "source": "user",
    "state": "loaded",
    ...
  }
]
```

**Note:** This only returns the config entry, not the associated devices. You still need WebSocket API to get devices.

## WebSocket Subscriptions

### Subscribe to Device Registry Updates

You can subscribe to device registry changes to maintain a local cache:

**Command:** Subscribe to `device_registry_updated` events via the WebSocket connection

**Event Data:**
```json
{
  "event_type": "device_registry_updated",
  "data": {
    "action": "update",
    "device_id": "device_1",
    "changes": {
      "config_entries": [["old_entries"], ["new_entries"]]
    }
  }
}
```

This allows you to:
- Maintain a local cache of devices
- Update the cache incrementally when devices change
- Filter from cached data without repeated API calls

## Best Practices

### 1. Cache Device and Entity Lists

- Fetch device list once
- Fetch entity list once
- Filter client-side for multiple queries
- Refresh on device/entity registry update events

### 2. Efficient Filtering

- Use `Array.includes()` or `Set.has()` for fast lookups
- Filter devices first, then get entities for those devices
- Consider filtering entities by `config_entry_id` if you only need entities

### 3. Handle Multiple Config Entries

A device can be associated with multiple config entries. If you need devices for a specific entry:

```javascript
// Get devices where entry_id is in config_entries array
const devices = allDevices.filter(device =>
  device.config_entries && device.config_entries.includes(entryId)
);
```

### 4. Primary Config Entry

Some devices have a `primary_config_entry` field (not always in API response). The first entry in `config_entries` is typically the primary one.

## Error Handling

### Config Entry Not Found

**Response:**
```json
{
  "id": 1,
  "type": "result",
  "success": false,
  "error": {
    "code": "not_found",
    "message": "Config entry not found"
  }
}
```

**Action:** Validate the entry ID before querying devices.

### No Devices Found

If filtering returns no devices, it means:
- The config entry exists but has no associated devices
- The config entry may be a service-type integration
- The integration may not create devices (only entities)

## Limitations

1. **No Server-Side Filtering:** The API does not support filtering by `entry_id` - all devices are returned
2. **No REST API:** Device registry operations are WebSocket-only
3. **No Pagination:** All devices are returned in a single response
4. **Client-Side Processing:** Filtering logic must be implemented client-side
5. **No Direct Query:** Cannot query devices directly by entry ID

## Code References

**Device Registry WebSocket:**
- `homeassistant/components/config/device_registry.py:30-57` - `websocket_list_devices()` function

**Config Entry WebSocket:**
- `homeassistant/components/config/config_entries.py:472-491` - `config_entry_get_single()` function

**Entity Registry WebSocket:**
- `homeassistant/components/config/entity_registry.py:42-63` - `websocket_list_entities()` function

**Helper Functions:**
- `homeassistant/helpers/device_registry.py:1724-1728` - `async_entries_for_config_entry()` function (internal use)

## Summary

To get device details from a config entry ID:

1. **Use WebSocket API:** `config/device_registry/list` to get all devices
2. **Filter Client-Side:** Filter devices where `entry_id` is in `config_entries` array
3. **Get Entities (Optional):** Use `config/entity_registry/list` and filter by `device_id` or `config_entry_id`
4. **No REST API:** Device registry operations are WebSocket-only
5. **No Direct Query:** Must filter client-side - no server-side filtering by entry ID

**Key Code Pattern:**
```javascript
const devicesForEntry = allDevices.filter(device =>
  device.config_entries && device.config_entries.includes(entryId)
);
```



