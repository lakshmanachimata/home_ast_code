# Device Type and Capabilities API Documentation

## Overview

This document provides comprehensive information about retrieving devices for an area, determining device types, and discovering device capabilities (such as sensors, switches, lights, etc.) through Home Assistant's WebSocket API.

## Workflow Overview

To get complete information about devices in an area and their capabilities:

1. **Get Devices by Area** - Retrieve devices assigned to one or more areas
2. **Get Device Type** - Determine the device entry type (service, hub, etc.)
3. **Get Device Entities** - Retrieve all entities associated with each device
4. **Analyze Entity Capabilities** - Determine what each entity provides (sensor, switch, light, etc.)

## Step 1: Get Devices for an Area

### WebSocket Command

**Command Type:** `config/device_registry/list`

**Request:**
```json
{
  "id": 1,
  "type": "config/device_registry/list"
}
```

**Response:** Returns all devices. Filter by `area_id` client-side.

**Device Entry Fields:**
- `id`: Device identifier
- `area_id`: Area assignment (string or null)
- `entry_type`: Device type (string or null) - See Device Types section
- `name`: Device name
- `name_by_user`: User-customizable name
- `manufacturer`: Manufacturer name
- `model`: Device model
- `device_id`: Same as `id` field

### Filtering by Area

After receiving all devices, filter by `area_id`:
- Single area: `device.area_id === "target_area_id"`
- Multiple areas: `device.area_id` in array of target area IDs

## Step 2: Device Type Information

### Device Entry Type

The `entry_type` field in device entries indicates the device classification:

**Possible Values:**
- `"service"`: Service-type device (cloud services, integrations without physical devices)
- `null`: Standard physical device (most common)

**Device Entry Type Enum:**
- `DeviceEntryType.SERVICE = "service"`

**Usage:**
- Service devices typically represent cloud services or virtual devices
- Physical devices usually have `entry_type: null`
- Use this to distinguish between physical hardware and service integrations

### Device Information Fields

Additional device metadata available in device entries:

| Field | Type | Description |
|-------|------|-------------|
| `manufacturer` | string \| null | Device manufacturer |
| `model` | string \| null | Device model name |
| `model_id` | string \| null | Model identifier |
| `sw_version` | string \| null | Software/firmware version |
| `hw_version` | string \| null | Hardware version |
| `serial_number` | string \| null | Serial number |
| `configuration_url` | string \| null | URL to device configuration |

## Step 3: Get Entities for a Device

### WebSocket Command

**Command Type:** `config/entity_registry/list`

**Request:**
```json
{
  "id": 2,
  "type": "config/entity_registry/list"
}
```

**Response:** Returns all entities. Filter by `device_id` client-side.

### Filtering Entities by Device

After receiving all entities, filter by `device_id`:
```javascript
const deviceEntities = allEntities.filter(
  entity => entity.device_id === targetDeviceId
);
```

### Entity Entry Fields

Each entity entry contains:

| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | string | Full entity ID (e.g., `"sensor.temperature"`) |
| `device_id` | string \| null | Associated device ID |
| `domain` | string | Entity domain (sensor, switch, light, etc.) |
| `platform` | string | Integration platform name |
| `device_class` | string \| null | Device class (e.g., `"temperature"`, `"battery"`) |
| `original_device_class` | string \| null | Original device class set by integration |
| `name` | string \| null | Entity name |
| `original_name` | string \| null | Original name set by integration |
| `unit_of_measurement` | string \| null | Unit of measurement (e.g., `"°C"`, `"%`") |
| `supported_features` | integer | Bitmask of supported features |
| `entity_category` | string \| null | Category (e.g., `"diagnostic"`, `"config"`) |
| `disabled_by` | string \| null | Disabler if entity is disabled |
| `hidden_by` | string \| null | Hider if entity is hidden |
| `icon` | string \| null | Icon identifier |
| `original_icon` | string \| null | Original icon set by integration |
| `capabilities` | object \| null | Entity capabilities mapping |
| `labels` | array of strings | Label identifiers |
| `area_id` | string \| null | Area assignment |

## Step 4: Understanding Device Capabilities

### Entity Domain

The `domain` field indicates the primary capability type:

**Common Domains:**
- `"sensor"`: Sensor entities (temperature, humidity, motion, etc.)
- `"binary_sensor"`: Binary sensors (on/off states like motion, door, etc.)
- `"switch"`: Switch entities (on/off control)
- `"light"`: Light entities (brightness, color control)
- `"climate"`: Climate/thermostat entities
- `"cover"`: Cover entities (blinds, garage doors, etc.)
- `"fan"`: Fan entities
- `"lock"`: Lock entities
- `"media_player"`: Media player entities
- `"camera"`: Camera entities
- `"alarm_control_panel"`: Alarm system entities
- `"button"`: Button entities
- `"number"`: Number input entities
- `"select"`: Select/dropdown entities
- `"text"`: Text input entities
- `"date"`: Date input entities
- `"time"`: Time input entities
- `"datetime"`: Date-time input entities
- `"update"`: Update entities (firmware updates)
- `"valve"`: Valve entities

### Device Class

The `device_class` field provides more specific information about entity type:

**Sensor Device Classes:**
- `"temperature"`: Temperature sensor
- `"humidity"`: Humidity sensor
- `"battery"`: Battery level sensor
- `"pressure"`: Pressure sensor
- `"illuminance"`: Light level sensor
- `"signal_strength"`: Signal strength sensor
- `"timestamp"`: Timestamp sensor
- `"power"`: Power consumption sensor
- `"current"`: Current sensor
- `"voltage"`: Voltage sensor
- `"energy"`: Energy consumption sensor
- `"gas"`: Gas sensor
- `"co2"`: CO2 sensor
- `"pm25"`: PM2.5 sensor
- `"pm10"`: PM10 sensor
- `"aqi"`: Air quality index sensor
- `"moisture"`: Moisture sensor
- `"wind_speed"`: Wind speed sensor
- `"wind_bearing"`: Wind direction sensor
- `"precipitation"`: Precipitation sensor
- `"distance"`: Distance sensor
- `"duration"`: Duration sensor
- `"speed"`: Speed sensor
- `"volume"`: Volume sensor
- `"weight"`: Weight sensor
- `"data_rate"`: Data rate sensor
- `"data_size"`: Data size sensor
- `"frequency"`: Frequency sensor
- `"reactive_power"`: Reactive power sensor
- `"apparent_power"`: Apparent power sensor
- `"power_factor"`: Power factor sensor
- `"reactive_energy"`: Reactive energy sensor
- `"apparent_energy"`: Apparent energy sensor
- `"monetary"`: Monetary value sensor
- `"enum"`: Enumeration sensor

**Binary Sensor Device Classes:**
- `"battery"`: Battery low indicator
- `"battery_charging"`: Battery charging indicator
- `"cold"`: Cold condition
- `"connectivity"`: Connectivity status
- `"door"`: Door state
- `"garage_door"`: Garage door state
- `"gas"`: Gas detection
- `"heat"`: Heat condition
- `"light"`: Light detection
- `"lock"`: Lock state
- `"moisture"`: Moisture detection
- `"motion"`: Motion detection
- `"moving"`: Moving state
- `"occupancy"`: Occupancy detection
- `"opening"`: Opening state
- `"plug"`: Plug state
- `"power"`: Power state
- `"presence"`: Presence detection
- `"problem"`: Problem indicator
- `"running"`: Running state
- `"safety"`: Safety indicator
- `"smoke"`: Smoke detection
- `"sound"`: Sound detection
- `"tamper"`: Tamper detection
- `"update"`: Update available
- `"vibration"`: Vibration detection
- `"window"`: Window state

**Switch Device Classes:**
- `"outlet"`: Electrical outlet
- `"switch"`: Generic switch

**Cover Device Classes:**
- `"awning"`: Awning
- `"blind"`: Blind
- `"curtain"`: Curtain
- `"damper"`: Damper
- `"door"`: Door
- `"garage"`: Garage door
- `"gate"`: Gate
- `"shade"`: Shade
- `"shutter"`: Shutter
- `"window"`: Window

**Other Device Classes:**
- Various device classes exist for other domains (light, climate, lock, etc.)

### Entity Category

The `entity_category` field indicates the purpose category:

**Categories:**
- `"diagnostic"`: Diagnostic/technical information
- `"config"`: Configuration entities
- `null`: Primary functional entity

### Supported Features

The `supported_features` field is a bitmask indicating additional capabilities:

**Common Feature Flags:**
- Light: Brightness, color, color temperature, effects
- Cover: Open, close, stop, position, tilt
- Climate: Target temperature, fan mode, preset mode
- Media Player: Play, pause, volume, mute, etc.
- Camera: Stream, record, etc.

## Complete Workflow Example

### Step-by-Step Process

1. **Get All Devices:**
   ```json
   {
     "id": 1,
     "type": "config/device_registry/list"
   }
   ```

2. **Filter Devices by Area:**
   - Filter response where `area_id` matches target area(s)

3. **For Each Device, Get Entities:**
   ```json
   {
     "id": 2,
     "type": "config/entity_registry/list"
   }
   ```

4. **Filter Entities by Device:**
   - Filter entities where `device_id` matches device ID

5. **Analyze Entity Capabilities:**
   - Check `domain` for primary capability (sensor, switch, light, etc.)
   - Check `device_class` for specific type (temperature, motion, etc.)
   - Check `entity_category` for purpose (diagnostic, config, etc.)
   - Check `unit_of_measurement` for measurement units
   - Check `supported_features` for additional capabilities

## Device Capability Summary

### Determining Device Capabilities

To understand what a device provides:

1. **List all entities for the device** (filter by `device_id`)
2. **Group entities by domain** to see capability types:
   - Sensors: `domain === "sensor"` or `domain === "binary_sensor"`
   - Controls: `domain === "switch"`, `domain === "light"`, etc.
   - Climate: `domain === "climate"`
   - Covers: `domain === "cover"`
   - Media: `domain === "media_player"`
   - Security: `domain === "alarm_control_panel"`, `domain === "lock"`
   - Inputs: `domain === "button"`, `domain === "number"`, etc.

3. **Analyze device_class** for specific functionality:
   - Temperature sensors: `device_class === "temperature"`
   - Motion sensors: `device_class === "motion"`
   - Battery sensors: `device_class === "battery"`
   - Door sensors: `device_class === "door"`

4. **Check entity_category** to filter diagnostic/config entities:
   - Primary entities: `entity_category === null`
   - Diagnostic entities: `entity_category === "diagnostic"`
   - Config entities: `entity_category === "config"`

### Example: Sensor Device Analysis

For a temperature sensor device:

**Device Information:**
- `entry_type`: `null` (physical device)
- `manufacturer`: `"Sensor Corp"`
- `model`: `"TempSensor Pro"`

**Entity Information:**
- `domain`: `"sensor"`
- `device_class`: `"temperature"`
- `unit_of_measurement`: `"°C"`
- `entity_category`: `null` (primary entity)

**Capability Summary:**
- Provides temperature sensing
- Reports in Celsius
- Primary functional entity

### Example: Multi-Capability Device

For a smart thermostat device:

**Device Information:**
- `entry_type`: `null`
- `manufacturer`: `"Thermostat Inc"`
- `model`: `"SmartThermo 3000"`

**Entities:**
1. Climate entity:
   - `domain`: `"climate"`
   - `device_class`: `null`
   - Primary control entity

2. Temperature sensor:
   - `domain`: `"sensor"`
   - `device_class`: `"temperature"`
   - `unit_of_measurement`: `"°C"`

3. Battery sensor:
   - `domain`: `"sensor"`
   - `device_class`: `"battery"`
   - `unit_of_measurement`: `"%"`
   - `entity_category`: `"diagnostic"`

**Capability Summary:**
- Provides climate control
- Monitors temperature
- Reports battery level (diagnostic)

## Related APIs

### Get Entity Details

**Command:** `config/entity_registry/get`

**Request:**
```json
{
  "id": 3,
  "type": "config/entity_registry/get",
  "entity_id": "sensor.temperature"
}
```

**Response:** Extended entity information including all fields.

### Get Multiple Entities

**Command:** `config/entity_registry/get_entries`

**Request:**
```json
{
  "id": 4,
  "type": "config/entity_registry/get_entries",
  "entity_ids": ["sensor.temperature", "sensor.humidity"]
}
```

**Response:** Dictionary mapping entity IDs to entity data.

### List Entities for Display

**Command:** `config/entity_registry/list_for_display`

**Request:**
```json
{
  "id": 5,
  "type": "config/entity_registry/list_for_display"
}
```

**Response:** Entities formatted for display, excluding disabled entities.

## Best Practices

### 1. Cache Device and Entity Lists

- Fetch device list once
- Fetch entity list once
- Filter client-side for multiple queries
- Refresh on device/entity registry update events

### 2. Filter Efficiently

- Use device `id` field to match entities
- Group entities by domain for capability analysis
- Filter out disabled entities: `entity.disabled_by === null`
- Filter out hidden entities: `entity.hidden_by === null`

### 3. Understand Entity Categories

- Primary entities (`entity_category === null`): Main device functionality
- Diagnostic entities (`entity_category === "diagnostic"`): Technical information
- Config entities (`entity_category === "config"`): Configuration options

### 4. Device Type Interpretation

- `entry_type === "service"`: Cloud service or virtual device
- `entry_type === null`: Physical hardware device
- Use manufacturer/model for additional device identification

### 5. Capability Detection

- Check `domain` first for primary capability type
- Use `device_class` for specific functionality
- Review `supported_features` for advanced capabilities
- Check `unit_of_measurement` for measurement context

## Limitations

1. **No Direct Device-to-Entities API:** Must fetch all entities and filter client-side
2. **No Capability Aggregation:** Must analyze entities manually to determine capabilities
3. **No Device Type Enumeration:** Limited device type values (mainly "service" or null)
4. **Client-Side Processing:** All filtering and analysis performed client-side

## Summary

To get devices for an area and understand their capabilities:

1. **Get Devices:** Use `config/device_registry/list` and filter by `area_id`
2. **Get Device Type:** Check `entry_type` field (usually `null` or `"service"`)
3. **Get Entities:** Use `config/entity_registry/list` and filter by `device_id`
4. **Analyze Capabilities:**
   - Check `domain` for capability type (sensor, switch, light, etc.)
   - Check `device_class` for specific functionality
   - Check `entity_category` for entity purpose
   - Check `unit_of_measurement` for measurement units
   - Review `supported_features` for advanced capabilities

The combination of device information and entity analysis provides a complete picture of what each device can do.

