# Area Registry Create API

## Overview
This API allows you to create a new area in Home Assistant. Areas are used to organize devices and entities by location (e.g., Kitchen, Bedroom, Living Room).

## API Endpoint
**Type**: `config/area_registry/create`

## Authentication
- **Required**: Admin privileges (`@require_admin`)
- The WebSocket connection must be authenticated with an admin user

## Request Format

### Message Structure
```json
{
  "id": <unique_message_id>,
  "type": "config/area_registry/create",
  "name": "<area_name>",
  "aliases": ["alias1", "alias2"],
  "floor_id": "<floor_id>",
  "humidity_entity_id": "<entity_id>" | null,
  "icon": "<icon_identifier>",
  "labels": ["label1", "label2"],
  "picture": "<picture_path>" | null,
  "temperature_entity_id": "<entity_id>" | null
}
```

### Required Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | number | Unique message ID for request/response correlation |
| `type` | string | Must be `"config/area_registry/create"` |
| `name` | string | Display name of the area (e.g., "Kitchen", "Living Room") |

### Optional Parameters
| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `aliases` | array of strings | Alternative names for the area that can be used for matching | None |
| `floor_id` | string | ID of the floor this area belongs to | Must be a valid floor ID if provided |
| `humidity_entity_id` | string \| null | Entity ID of a humidity sensor for this area | Must be a valid sensor entity with `device_class: humidity` |
| `icon` | string | Material Design Icons identifier (e.g., "mdi:home", "mdi:garage") | None |
| `labels` | array of strings | List of label IDs to assign to the area | Must be valid label IDs if provided |
| `picture` | string \| null | Path to a picture file for the area (relative to config directory) | None |
| `temperature_entity_id` | string \| null | Entity ID of a temperature sensor for this area | Must be a valid sensor entity with `device_class: temperature` |

## Response Format

### Success Response
```json
{
  "id": <message_id>,
  "type": "result",
  "success": true,
  "result": {
    "aliases": ["alias1", "alias2"],
    "area_id": "<generated_area_id>",
    "created_at": <unix_timestamp>,
    "floor_id": "<floor_id>" | null,
    "humidity_entity_id": "<entity_id>" | null,
    "icon": "<icon>" | null,
    "labels": ["label1", "label2"],
    "modified_at": <unix_timestamp>,
    "name": "<area_name>",
    "picture": "<picture_path>" | null,
    "temperature_entity_id": "<entity_id>" | null
  }
}
```

### Error Response
```json
{
  "id": <message_id>,
  "type": "result",
  "success": false,
  "error": {
    "code": "invalid_info",
    "message": "<error_message>"
  }
}
```

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `aliases` | array of strings | Alternative names for the area |
| `area_id` | string | Unique identifier for the area (auto-generated from name) |
| `created_at` | number | Unix timestamp (seconds with fractional seconds) when the area was created |
| `floor_id` | string \| null | ID of the floor this area belongs to |
| `humidity_entity_id` | string \| null | Entity ID of the humidity sensor |
| `icon` | string \| null | Icon identifier |
| `labels` | array of strings | List of label IDs assigned to the area |
| `modified_at` | number | Unix timestamp (seconds with fractional seconds) when the area was last modified |
| `name` | string | Display name of the area |
| `picture` | string \| null | Path to area picture |
| `temperature_entity_id` | string \| null | Entity ID of the temperature sensor |

## Validation Rules

### Name Validation
- **Required**: The `name` field is mandatory
- **Uniqueness**: Area names must be unique (case-insensitive)
- **Error**: If a name already exists, returns error: `"The name {name} ({normalized_name}) is already in use"`

### Temperature Entity Validation
If `temperature_entity_id` is provided:
- **Entity Existence**: The entity must exist in Home Assistant
- **Entity Type**: Must be a sensor entity (`domain == "sensor"`)
- **Device Class**: Must have `device_class: temperature`
- **Error Messages**:
  - `"Entity {entity_id} does not exist"` - if entity doesn't exist
  - `"Entity {entity_id} is not a temperature sensor"` - if entity is not a temperature sensor

### Humidity Entity Validation
If `humidity_entity_id` is provided:
- **Entity Existence**: The entity must exist in Home Assistant
- **Entity Type**: Must be a sensor entity (`domain == "sensor"`)
- **Device Class**: Must have `device_class: humidity`
- **Error Messages**:
  - `"Entity {entity_id} does not exist"` - if entity doesn't exist
  - `"Entity {entity_id} is not a humidity sensor"` - if entity is not a humidity sensor

### Floor ID Validation
- **Existence**: If provided, the `floor_id` must exist in the floor registry
- **Type**: Must be a string

### Labels Validation
- **Existence**: All label IDs in the array must exist in the label registry
- **Type**: Must be an array of strings

## Examples

### Example 1: Create Area with Minimum Required Fields
```json
{
  "id": 1,
  "type": "config/area_registry/create",
  "name": "Kitchen"
}
```

**Response**:
```json
{
  "id": 1,
  "type": "result",
  "success": true,
  "result": {
    "aliases": [],
    "area_id": "kitchen",
    "created_at": 1721234567.9,
    "floor_id": null,
    "humidity_entity_id": null,
    "icon": null,
    "labels": [],
    "modified_at": 1721234567.9,
    "name": "Kitchen",
    "picture": null,
    "temperature_entity_id": null
  }
}
```

### Example 2: Create Area with All Optional Fields
```json
{
  "id": 2,
  "type": "config/area_registry/create",
  "name": "Living Room",
  "aliases": ["lounge", "sitting room"],
  "floor_id": "first_floor_id",
  "icon": "mdi:sofa",
  "labels": ["smart_home", "entertainment"],
  "picture": "/config/www/areas/living_room.jpg",
  "temperature_entity_id": "sensor.living_room_temperature",
  "humidity_entity_id": "sensor.living_room_humidity"
}
```

**Response**:
```json
{
  "id": 2,
  "type": "result",
  "success": true,
  "result": {
    "aliases": ["lounge", "sitting room"],
    "area_id": "living_room",
    "created_at": 1721234568.0,
    "floor_id": "first_floor_id",
    "humidity_entity_id": "sensor.living_room_humidity",
    "icon": "mdi:sofa",
    "labels": ["smart_home", "entertainment"],
    "modified_at": 1721234568.0,
    "name": "Living Room",
    "picture": "/config/www/areas/living_room.jpg",
    "temperature_entity_id": "sensor.living_room_temperature"
  }
}
```

### Example 3: Create Area with Floor Assignment
```json
{
  "id": 3,
  "type": "config/area_registry/create",
  "name": "Master Bedroom",
  "floor_id": "second_floor_id",
  "icon": "mdi:bed"
}
```

### Example 4: Create Area with Temperature Sensor Only
```json
{
  "id": 4,
  "type": "config/area_registry/create",
  "name": "Garage",
  "icon": "mdi:garage",
  "temperature_entity_id": "sensor.garage_temperature"
}
```

## Error Examples

### Error 1: Duplicate Name
**Request**:
```json
{
  "id": 5,
  "type": "config/area_registry/create",
  "name": "Kitchen"
}
```
(Assuming "Kitchen" already exists)

**Response**:
```json
{
  "id": 5,
  "type": "result",
  "success": false,
  "error": {
    "code": "invalid_info",
    "message": "The name Kitchen (kitchen) is already in use"
  }
}
```

### Error 2: Invalid Temperature Entity
**Request**:
```json
{
  "id": 6,
  "type": "config/area_registry/create",
  "name": "Office",
  "temperature_entity_id": "light.office_light"
}
```

**Response**:
```json
{
  "id": 6,
  "type": "result",
  "success": false,
  "error": {
    "code": "invalid_info",
    "message": "Entity light.office_light is not a temperature sensor"
  }
}
```

### Error 3: Non-existent Entity
**Request**:
```json
{
  "id": 7,
  "type": "config/area_registry/create",
  "name": "Bathroom",
  "humidity_entity_id": "sensor.non_existent"
}
```

**Response**:
```json
{
  "id": 7,
  "type": "result",
  "success": false,
  "error": {
    "code": "invalid_info",
    "message": "Entity sensor.non_existent does not exist"
  }
}
```

## Notes

1. **Area ID Generation**: The `area_id` is automatically generated from the area name (normalized and lowercased)
2. **Name Normalization**: Area names are normalized (lowercased, spaces removed) for uniqueness checking
3. **Timestamps**: Both `created_at` and `modified_at` are set to the current time when the area is created
4. **Aliases and Labels**: These are stored as sets internally, so duplicate values are automatically removed
5. **Picture Path**: Picture paths are relative to the Home Assistant configuration directory
6. **Icon Format**: Icons should use Material Design Icons format (e.g., "mdi:home", "mdi:garage")
7. **Entity Validation**: Temperature and humidity entities are validated at creation time - they must exist and have the correct device class
8. **Event Firing**: When an area is created, a `area_registry_updated` event is fired with action "create"
9. **Admin Required**: This operation requires admin privileges
10. **Case Sensitivity**: Area name uniqueness is case-insensitive (e.g., "Kitchen" and "kitchen" are considered the same)

## Related APIs

- `config/area_registry/list` - List all areas
- `config/area_registry/update` - Update an existing area
- `config/area_registry/delete` - Delete an area
- `config/floor_registry/list` - List all floors (to get valid floor_id values)
- `config/label_registry/list` - List all labels (to get valid label IDs)





