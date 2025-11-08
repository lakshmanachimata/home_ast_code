# Frontend Home Screen API Documentation

## Overview

This document explains how the Home Assistant frontend (web UI) determines what capabilities to display on the home screen and which WebSocket APIs it subscribes to for real-time updates.

## Frontend Architecture

The Home Assistant frontend uses a dashboard system called **Lovelace** to determine what to display. The frontend follows this workflow:

1. **Load Dashboard Configuration** - Get the Lovelace dashboard configuration
2. **Subscribe to Entity States** - Subscribe to entity state changes for real-time updates
3. **Render Dashboard** - Display cards and entities based on configuration
4. **Handle Updates** - Receive and process state change events

## Step 1: Loading Dashboard Configuration

### WebSocket Command: Get Lovelace Config

**Command Type:** `lovelace/config`

**Request:**
```json
{
  "id": 1,
  "type": "lovelace/config",
  "force": false,
  "url_path": null
}
```

**Parameters:**
- `force` (optional, default: `false`): Force reload configuration
- `url_path` (optional): Dashboard URL path (null for default dashboard)

**Response:**
```json
{
  "id": 1,
  "type": "result",
  "success": true,
  "result": {
    "title": "Home",
    "views": [
      {
        "title": "Main View",
        "path": "main",
        "cards": [
          {
            "type": "entities",
            "title": "Living Room",
            "entities": [
              "sensor.temperature",
              "light.living_room",
              "switch.tv"
            ]
          },
          {
            "type": "thermostat",
            "entity": "climate.thermostat"
          }
        ]
      }
    ]
  }
}
```

### Dashboard Configuration Structure

The Lovelace configuration defines:

1. **Views** - Different pages/tabs in the UI
2. **Cards** - UI components that display entities or information
3. **Entities** - Specific entities to display in cards

**Common Card Types:**
- `entities`: List of entities
- `thermostat`: Climate control card
- `gauge`: Gauge visualization
- `history-graph`: Historical data graph
- `picture`: Image card
- `markdown`: Markdown content
- `map`: Map with entity locations
- `weather-forecast`: Weather forecast
- `energy`: Energy consumption
- `alarm-panel`: Alarm control panel
- `media-control`: Media player controls

### How Capabilities Are Determined

The frontend determines what to display based on:

1. **Dashboard Configuration** - The Lovelace config explicitly lists entities and cards
2. **Entity Domain** - Each entity's domain (sensor, light, switch, etc.) determines available UI components
3. **Entity State** - Current state determines what controls/display options are available
4. **Entity Attributes** - Attributes like `device_class`, `supported_features` determine UI behavior

**Example:**
- A `light` entity with `supported_features` including brightness → Shows brightness slider
- A `sensor` entity with `device_class: "temperature"` → Shows temperature display
- A `climate` entity → Shows thermostat card with temperature controls

## Step 2: Subscribing to Entity States

### WebSocket Command: Subscribe to Entities

**Command Type:** `subscribe_entities`

**Request:**
```json
{
  "id": 2,
  "type": "subscribe_entities"
}
```

**Optional Parameters:**
- `entity_ids` (array): Subscribe to specific entities only
- `include` (array): Include filter patterns (e.g., `["light.*", "sensor.*"]`)
- `exclude` (array): Exclude filter patterns (e.g., `["sensor.battery_*"]`)

**Response:**
```json
{
  "id": 2,
  "type": "result",
  "success": true,
  "result": null
}
```

**Initial State Event:**
After subscription, the frontend receives an initial event with all entity states:

```json
{
  "id": 2,
  "type": "event",
  "event": {
    "a": {
      "sensor.temperature": {
        "a": {"unit_of_measurement": "°C", "device_class": "temperature"},
        "c": "context_id",
        "lc": "2024-01-01T12:00:00.000Z",
        "s": "22.5"
      },
      "light.living_room": {
        "a": {"brightness": 255, "color_mode": "rgb"},
        "c": "context_id",
        "lc": "2024-01-01T12:00:00.000Z",
        "s": "on"
      }
    }
  }
}
```

**Event Format:**
- `a`: Attributes object
- `c`: Context ID
- `lc`: Last changed timestamp
- `s`: State value

### State Change Events

When entity states change, the frontend receives incremental updates:

```json
{
  "id": 2,
  "type": "event",
  "event": {
    "a": {
      "light.living_room": {
        "a": {"brightness": 128},
        "c": "new_context_id",
        "s": "on"
      }
    }
  }
}
```

**Update Behavior:**
- Only changed attributes are sent (incremental updates)
- State changes trigger UI updates automatically
- Frontend merges updates with existing state

## Step 3: Additional Subscriptions

### Subscribe to Events

**Command Type:** `subscribe_events`

**Request:**
```json
{
  "id": 3,
  "type": "subscribe_events",
  "event_type": "state_changed"
}
```

**Purpose:** Subscribe to Home Assistant events (state changes, service calls, etc.)

### Get States (One-Time)

**Command Type:** `get_states`

**Request:**
```json
{
  "id": 4,
  "type": "get_states"
}
```

**Response:** All current entity states (one-time snapshot)

**Purpose:** Initial state load or refresh without subscription

## Frontend Decision Flow

### 1. Dashboard Configuration Loading

```
Frontend Startup
    ↓
Connect to WebSocket
    ↓
Authenticate
    ↓
Request Lovelace Config (lovelace/config)
    ↓
Parse Configuration
    ↓
Extract Entity IDs from Cards
```

### 2. Entity Subscription

```
Extract Entity IDs from Config
    ↓
Subscribe to Entities (subscribe_entities)
    ↓
Receive Initial States
    ↓
Render Dashboard with Current States
```

### 3. Real-Time Updates

```
Entity State Changes
    ↓
WebSocket Event Received
    ↓
Update Local State
    ↓
Re-render Affected UI Components
```

## Capability Detection

### Entity Domain-Based Capabilities

The frontend determines capabilities based on entity domain:

| Domain | Capabilities |
|--------|-------------|
| `light` | On/off, brightness, color, color temperature, effects |
| `switch` | On/off control |
| `sensor` | Value display, unit conversion, history |
| `binary_sensor` | On/off state display |
| `climate` | Temperature control, mode selection, fan control |
| `cover` | Open/close, position control, tilt |
| `fan` | On/off, speed control, direction |
| `lock` | Lock/unlock control |
| `media_player` | Play/pause, volume, source selection |
| `camera` | Image/video display, stream |
| `alarm_control_panel` | Arm/disarm, code entry |
| `button` | Button press action |
| `number` | Numeric input with min/max |
| `select` | Dropdown selection |
| `text` | Text input |
| `date` | Date picker |
| `time` | Time picker |
| `datetime` | Date-time picker |
| `update` | Update installation |
| `valve` | Valve control |

### Supported Features Detection

Entities expose `supported_features` as a bitmask indicating additional capabilities:

**Light Features:**
- Brightness control
- Color support (RGB)
- Color temperature
- White value
- Effects
- Flash
- Transition

**Cover Features:**
- Open
- Close
- Set position
- Set tilt position
- Stop
- Open tilt
- Close tilt

**Climate Features:**
- Target temperature
- Target temperature range
- Target humidity
- Fan mode
- Preset mode
- Swing mode
- Auxiliary heat

**Media Player Features:**
- Pause
- Seek
- Volume set
- Volume mute
- Previous track
- Next track
- Turn on
- Turn off
- Play media
- Volume step
- Select source
- Stop
- Clear playlist
- Play
- Shuffle set
- Select sound mode

### Device Class Detection

Device classes provide context for UI rendering:

**Sensor Device Classes:**
- `temperature` → Temperature display with unit conversion
- `humidity` → Humidity percentage display
- `battery` → Battery level with icon
- `pressure` → Pressure display
- `illuminance` → Light level display
- `power` → Power consumption display
- `energy` → Energy consumption display

**Binary Sensor Device Classes:**
- `motion` → Motion detection indicator
- `door` → Door state (open/closed)
- `window` → Window state
- `occupancy` → Occupancy indicator
- `smoke` → Smoke detection alert

## Complete Frontend Workflow

### Initial Load Sequence

1. **WebSocket Connection**
   ```json
   {"type": "auth", "access_token": "..."}
   ```

2. **Get Dashboard Configuration**
   ```json
   {"id": 1, "type": "lovelace/config"}
   ```

3. **Subscribe to Entity States**
   ```json
   {"id": 2, "type": "subscribe_entities"}
   ```

4. **Receive Initial States**
   - Event with all entity states
   - Parse and store in local state

5. **Render Dashboard**
   - Create cards based on configuration
   - Populate with entity states
   - Apply styling and layout

### Runtime Update Sequence

1. **Entity State Change**
   - Backend fires `state_changed` event
   - WebSocket forwards to frontend

2. **Frontend Receives Update**
   ```json
   {
     "id": 2,
     "type": "event",
     "event": {
       "a": {
         "light.living_room": {"s": "off"}
       }
     }
   }
   ```

3. **Update Local State**
   - Merge update with existing state
   - Trigger re-render of affected components

4. **UI Update**
   - Update card displays
   - Update entity badges
   - Update control states

## Dashboard Configuration Modes

### Storage Mode (Default)

- Configuration stored in database
- Editable via UI
- Per-user dashboards supported
- Retrieved via `lovelace/config` command

### YAML Mode

- Configuration from `ui-lovelace.yaml` file
- Not editable via UI
- Requires file editing
- Retrieved via `lovelace/config` command

### Auto-Generated Mode

- Automatically generated from entities
- No explicit configuration
- Entities grouped by area/device
- Generated on-the-fly

## Entity Registry Integration

### Getting Entity Metadata

The frontend may also query entity registry for additional information:

**Command:** `config/entity_registry/list`

**Purpose:** Get entity metadata (name, icon, device_class, etc.)

**Usage:** Used to enhance UI display with proper names, icons, and categorization

## Best Practices for Frontend Development

### 1. Efficient Subscriptions

- Subscribe to all entities initially
- Use filters if only specific entities needed
- Unsubscribe when not needed

### 2. State Management

- Cache entity states locally
- Merge incremental updates
- Handle missing entities gracefully

### 3. UI Rendering

- Render based on entity domain
- Check `supported_features` for capabilities
- Use `device_class` for appropriate UI components
- Handle unavailable entities

### 4. Performance

- Debounce rapid state changes
- Use virtual scrolling for large entity lists
- Lazy load dashboard views
- Cache dashboard configuration

## Related WebSocket APIs

### Dashboard Management

- `lovelace/config` - Get dashboard configuration
- `lovelace/config/save` - Save dashboard configuration (admin)
- `lovelace/config/delete` - Delete dashboard configuration (admin)
- `lovelace/resources` - Get dashboard resources

### Entity Management

- `subscribe_entities` - Subscribe to entity state changes
- `get_states` - Get current entity states (one-time)
- `config/entity_registry/list` - List entity registry entries
- `config/entity_registry/get` - Get specific entity registry entry

### Service Calls

- `call_service` - Call Home Assistant services (control entities)
- `subscribe_events` - Subscribe to Home Assistant events

## Summary

The Home Assistant frontend determines what to display through:

1. **Lovelace Dashboard Configuration** - Defines views, cards, and entities to display
2. **Entity Domain** - Determines available UI components and controls
3. **Supported Features** - Indicates additional capabilities (brightness, color, etc.)
4. **Device Class** - Provides context for appropriate UI rendering

The frontend subscribes to:

1. **`subscribe_entities`** - Real-time entity state updates
2. **`lovelace/config`** - Dashboard configuration
3. **`subscribe_events`** - Home Assistant events (optional)

This architecture allows the frontend to:
- Display entities based on dashboard configuration
- Show appropriate controls based on entity capabilities
- Update in real-time as states change
- Provide a responsive, dynamic user interface

