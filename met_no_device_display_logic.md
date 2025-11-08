# Met.no Device Display Logic - Comprehensive Documentation

## Overview

This document explains the complete logic flow of how the Home Assistant frontend displays a device with manufacturer "Met.no" and device name "Forecast" on the home screen. This traces the journey from integration code to frontend display.

## Device Information Flow

The display of device information follows this path:

1. **Integration Entity Creation** - Met.no integration creates weather entity with device info
2. **Device Registry Creation** - Device registry entry is created/updated from entity device_info
3. **Entity Registry Association** - Entity is associated with device in entity registry
4. **Frontend Data Retrieval** - Frontend retrieves device and entity information
5. **Frontend Display** - Frontend renders device name and manufacturer

## Step 1: Integration Entity Creation

### Met.no Weather Entity Initialization

**File:** `homeassistant/components/met/weather.py`

**Code Location:** Lines 120-141

When the Met.no integration sets up a weather entity, it creates a `MetWeather` entity with device information:

```python
def __init__(
    self,
    coordinator: MetDataUpdateCoordinator,
    config_entry: MetWeatherConfigEntry,
    name: str,
    is_metric: bool,
) -> None:
    """Initialise the platform with a data instance and site."""
    super().__init__(coordinator)
    self._attr_unique_id = _calculate_unique_id(config_entry.data, False)
    self._config = config_entry.data
    self._is_metric = is_metric
    self._attr_device_info = DeviceInfo(
        name="Forecast",
        entry_type=DeviceEntryType.SERVICE,
        identifiers={(DOMAIN, config_entry.entry_id)},
        manufacturer="Met.no",
        model="Forecast",
        configuration_url="https://www.met.no/en",
    )
    self._attr_track_home = self._config.get(CONF_TRACK_HOME, False)
    self._attr_name = name
```

### Key Device Information Set

| Field | Value | Source |
|-------|-------|--------|
| `name` | `"Forecast"` | Hardcoded in integration |
| `manufacturer` | `"Met.no"` | Hardcoded in integration |
| `model` | `"Forecast"` | Hardcoded in integration |
| `entry_type` | `DeviceEntryType.SERVICE` | Indicates service-type device |
| `identifiers` | `{(DOMAIN, config_entry.entry_id)}` | Unique device identifier |
| `configuration_url` | `"https://www.met.no/en"` | Link to service website |

### Important Clarification: API vs Device Information

**API Endpoint:** The Met.no integration uses the API endpoint:
- `https://aa015h6buqvih86i1.api.met.no/weatherapi/locationforecast/2.0/complete`

**What the API Provides:**
- Weather data (temperature, humidity, pressure, wind, etc.)
- Weather forecasts (daily and hourly)
- Current weather conditions
- **Does NOT provide device information** (manufacturer, device name, model)

**Device Information Source:**
- Device information (`name="Forecast"`, `manufacturer="Met.no"`) is **hardcoded** in the integration code
- This information is **not retrieved from the Met.no API**
- The API is used solely for weather data, not device metadata
- The `configuration_url` points to `https://www.met.no/en` as a reference, but device info comes from code

**Why Hardcoded:**
- Met.no is a weather service provider, not a device manufacturer
- The service doesn't provide device metadata in API responses
- Device information represents the service itself, not a physical device
- Consistent naming across all Met.no integrations regardless of location

### Entity Properties

- `_attr_has_entity_name = True` - Entity uses device name as prefix
- `_attr_name = name` - Entity name (from config or "Met.no")
- `unique_id` - Calculated from latitude/longitude or "home"

## Step 2: Device Registry Creation

### Entity Platform Processing

**File:** `homeassistant/helpers/entity_platform.py`

**Code Location:** Lines 786-926

When an entity is added to Home Assistant, the entity platform processes it:

1. **Extract Device Info** - Gets `device_info` from entity
2. **Create/Update Device** - Calls device registry to create or update device entry
3. **Link Entity to Device** - Associates entity with device via `device_id`

### Device Registry Creation Logic

**File:** `homeassistant/helpers/device_registry.py`

**Method:** `async_get_or_create`

**Process:**

1. **Check Identifiers** - Looks for existing device with matching identifiers
   - Identifiers: `{("met", config_entry.entry_id)}`

2. **Create New Device** (if not exists):
   - Uses `device_info.name` → Device name: `"Forecast"`
   - Uses `device_info.manufacturer` → Manufacturer: `"Met.no"`
   - Uses `device_info.model` → Model: `"Forecast"`
   - Uses `device_info.entry_type` → Entry type: `SERVICE`
   - Uses `device_info.identifiers` → Device identifiers
   - Links to `config_entry_id`

3. **Update Existing Device** (if exists):
   - Updates device properties if changed
   - Maintains device ID for entity association

### Device Entry Structure

The created device entry contains:

```python
DeviceEntry(
    id="device_unique_id",
    name="Forecast",
    manufacturer="Met.no",
    model="Forecast",
    entry_type=DeviceEntryType.SERVICE,
    identifiers={("met", "config_entry_id")},
    config_entries={config_entry_id},
    area_id=None,  # Can be assigned later
    name_by_user=None,  # User can customize
    ...
)
```

## Step 3: Entity Registry Association

### Entity Registration

**File:** `homeassistant/helpers/entity_platform.py`

**Code Location:** Lines 895-916

When entity is registered:

```python
entry = entity_registry.async_get_or_create(
    self.domain,  # "weather"
    self.platform_name,  # "met"
    entity.unique_id,  # Calculated unique ID
    device_id=device.id if device else None,  # Links to device
    ...
)
```

### Entity Registry Entry

**File:** `homeassistant/helpers/entity_registry.py`

**Structure:**

```python
RegistryEntry(
    entity_id="weather.met_no",  # Generated entity ID
    device_id="device_unique_id",  # Links to device
    domain="weather",
    platform="met",
    unique_id="calculated_unique_id",
    name=None,  # Uses device name (has_entity_name=True)
    has_entity_name=True,  # Entity name comes from device
    ...
)
```

### Entity-Device Relationship

- **Entity** `weather.met_no` → **Device** `device_unique_id`
- Entity inherits device name when `has_entity_name=True`
- Device name "Forecast" is used as base for entity display

## Step 4: Frontend Data Retrieval

### WebSocket API Subscriptions

The frontend retrieves device information through multiple WebSocket APIs:

#### 1. Get Entity Registry

**Command:** `config/entity_registry/list`

**Response includes:**
```json
{
  "entity_id": "weather.met_no",
  "device_id": "device_unique_id",
  "name": null,
  "has_entity_name": true,
  "domain": "weather",
  "platform": "met",
  ...
}
```

#### 2. Get Device Registry

**Command:** `config/device_registry/list`

**Response includes:**
```json
{
  "id": "device_unique_id",
  "name": "Forecast",
  "manufacturer": "Met.no",
  "model": "Forecast",
  "entry_type": "service",
  "identifiers": [["met", "config_entry_id"]],
  ...
}
```

#### 3. Subscribe to Entity States

**Command:** `subscribe_entities`

**Response includes entity states with device association**

### Frontend Data Processing

The frontend:

1. **Maps Entities to Devices** - Uses `device_id` from entity registry
2. **Retrieves Device Info** - Gets device details from device registry
3. **Builds Display Data** - Combines entity and device information

## Step 5: Frontend Display Logic

### Device Name Display

The frontend determines what to display using this priority:

1. **User Custom Name** (`name_by_user`)
   - If user has customized device name, use that
   - Checked first for user preferences

2. **Device Name** (`name`)
   - From device registry: `"Forecast"`
   - Used if no user custom name

3. **Entity Name** (if no device)
   - Fallback to entity name if device not available

### Manufacturer Display

The frontend displays manufacturer from:

1. **Device Registry** - `manufacturer` field: `"Met.no"`
2. **Device Entry** - Retrieved via device registry API
3. **Display Format** - Usually shown as "Manufacturer: Met.no" or similar

### Display Location

Device information appears in:

1. **Device Card** - Device overview card showing device details
2. **Entity Card** - Entity cards showing associated device
3. **Device Info Panel** - Detailed device information panel
4. **Entity Info** - Entity information showing device association

### Frontend Rendering Logic

**Device Display Algorithm:**

```javascript
function getDeviceDisplayName(device, entity) {
  // Priority 1: User custom name
  if (device.name_by_user) {
    return device.name_by_user;
  }
  
  // Priority 2: Device name
  if (device.name) {
    return device.name;  // "Forecast"
  }
  
  // Priority 3: Entity name (fallback)
  return entity.name || entity.entity_id;
}

function getManufacturer(device) {
  return device.manufacturer;  // "Met.no"
}
```

## Complete Data Flow Diagram

```
Met.no Integration
    ↓
MetWeather Entity Created
    ↓
device_info = DeviceInfo(
    name="Forecast",
    manufacturer="Met.no",
    ...
)
    ↓
Entity Platform Processes Entity
    ↓
Device Registry: async_get_or_create()
    ↓
Device Entry Created:
    - name: "Forecast"
    - manufacturer: "Met.no"
    - identifiers: {("met", entry_id)}
    ↓
Entity Registry: async_get_or_create()
    ↓
Entity Entry Created:
    - device_id: device.id
    - has_entity_name: True
    ↓
Frontend: config/device_registry/list
    ↓
Frontend: config/entity_registry/list
    ↓
Frontend: subscribe_entities
    ↓
Frontend Maps Entities → Devices
    ↓
Frontend Displays:
    - Device Name: "Forecast"
    - Manufacturer: "Met.no"
```

## Key Code Locations

### Integration Code

**File:** `homeassistant/components/met/weather.py`
- **Line 132-139:** Device info creation
- **Line 111:** `has_entity_name = True` setting
- **Line 141:** Entity name assignment

### Device Registry

**File:** `homeassistant/helpers/device_registry.py`
- **Line 832-910:** `async_get_or_create` method
- **Line 322-352:** `DeviceEntry` class definition

### Entity Registry

**File:** `homeassistant/helpers/entity_registry.py`
- **Line 179-216:** `RegistryEntry` class definition
- **Line 693-702:** `get_entries_for_device_id` method

### Entity Platform

**File:** `homeassistant/helpers/entity_platform.py`
- **Line 786-926:** `_async_add_entity` method
- **Line 895-916:** Entity registry creation with device association

## Device Information Sources

### Hardcoded Values (Not from API)

**Important Clarification:** The device information (manufacturer "Met.no" and device name "Forecast") is **hardcoded in the integration code** and is **NOT retrieved from the Met.no API backend**.

While the integration connects to `https://aa015h6buqvih86i1.api.met.no/weatherapi/locationforecast/2.0/complete`, this API endpoint:
- **Provides:** Weather data (temperature, humidity, pressure, wind, forecasts)
- **Does NOT Provide:** Device metadata (manufacturer, device name, model)

**Code Evidence:**
- `coordinator.py:78-89` - `fetch_data()` method only retrieves weather data
- `coordinator.py:83` - `get_current_weather()` returns weather conditions  
- `coordinator.py:85-88` - `get_forecast()` returns forecast data
- No code extracts device information from API responses
- Device info is set directly in `weather.py:132-139` without any API calls

### Hardcoded Values

The Met.no integration hardcodes device information:

| Field | Value | Location |
|-------|-------|----------|
| `name` | `"Forecast"` | `weather.py:133` |
| `manufacturer` | `"Met.no"` | `weather.py:136` |
| `model` | `"Forecast"` | `weather.py:137` |
| `entry_type` | `SERVICE` | `weather.py:134` |

### Why "Forecast"?

- **Service Type Device** - Met.no is a weather forecast service, not a physical device
- **Generic Name** - "Forecast" describes the service type
- **Consistent Naming** - All Met.no instances use same device name
- **User Customization** - Users can change via `name_by_user` if desired

### Why "Met.no"?

- **Service Provider** - Met.no is the Norwegian Meteorological Institute
- **Data Source** - Weather data comes from met.no API
- **Attribution** - Identifies the source of weather information
- **Branding** - Official name of the service provider

## Frontend Display Scenarios

### Scenario 1: Default Display

**Device Registry:**
- `name`: `"Forecast"`
- `manufacturer`: `"Met.no"`
- `name_by_user`: `null`

**Frontend Displays:**
- Device Name: **"Forecast"**
- Manufacturer: **"Met.no"**

### Scenario 2: User Custom Name

**Device Registry:**
- `name`: `"Forecast"`
- `manufacturer`: `"Met.no"`
- `name_by_user`: `"My Weather"`

**Frontend Displays:**
- Device Name: **"My Weather"** (user custom name takes priority)
- Manufacturer: **"Met.no"**

### Scenario 3: Entity with Device

**Entity Registry:**
- `entity_id`: `"weather.met_no"`
- `device_id`: `"device_unique_id"`
- `has_entity_name`: `true`

**Device Registry:**
- `name`: `"Forecast"`

**Frontend Displays:**
- Entity appears as: **"Forecast"** (uses device name)
- Full entity ID: `weather.met_no`
- Device association shown in entity info

## WebSocket API Responses

### Device Registry Response

```json
{
  "id": 1,
  "type": "result",
  "success": true,
  "result": [
    {
      "id": "abc123...",
      "name": "Forecast",
      "manufacturer": "Met.no",
      "model": "Forecast",
      "entry_type": "service",
      "identifiers": [["met", "config_entry_id"]],
      "config_entries": ["config_entry_id"],
      "area_id": null,
      "name_by_user": null,
      "created_at": 1234567890.123,
      "modified_at": 1234567890.123
    }
  ]
}
```

### Entity Registry Response

```json
{
  "id": 2,
  "type": "result",
  "success": true,
  "result": [
    {
      "entity_id": "weather.met_no",
      "device_id": "abc123...",
      "name": null,
      "has_entity_name": true,
      "domain": "weather",
      "platform": "met",
      "unique_id": "calculated_unique_id",
      "device_class": null,
      "original_name": null
    }
  ]
}
```

## Entity Name Resolution

### has_entity_name = True

When `has_entity_name = True`:

1. **Entity Name** (`name` field) is typically `null`
2. **Device Name** is used as the base name
3. **Entity Display** shows device name
4. **Entity ID** remains `weather.met_no`

### Entity Display Logic

```javascript
function getEntityDisplayName(entity, device) {
  if (entity.has_entity_name) {
    // Entity name comes from device
    if (entity.name) {
      return entity.name;  // Custom entity name
    }
    return device.name;  // Use device name: "Forecast"
  } else {
    // Entity has its own name
    return entity.name || entity.entity_id;
  }
}
```

## Device Type: SERVICE

### Entry Type Significance

**`entry_type: DeviceEntryType.SERVICE`** indicates:

1. **Service Device** - Not a physical hardware device
2. **Cloud Service** - Data comes from cloud API
3. **Virtual Device** - Represents a service, not hardware
4. **No Physical Location** - Doesn't have physical presence

### Service Device Characteristics

- **No MAC Address** - No network connection identifier
- **No Hardware Info** - No hardware version, serial number
- **API-Based** - Data retrieved via API calls
- **Configuration URL** - Links to service website

## Frontend Display Components

### Device Card

Shows device information:
- **Name:** "Forecast" (from device registry)
- **Manufacturer:** "Met.no" (from device registry)
- **Model:** "Forecast" (from device registry)
- **Type:** Service (from entry_type)
- **Entities:** List of associated entities

### Entity Card

Shows entity with device context:
- **Entity:** weather.met_no
- **Display Name:** "Forecast" (from device)
- **Device:** Links to device card
- **Manufacturer:** "Met.no" (from device)

### Device Info Panel

Detailed device information:
- **Device Name:** "Forecast"
- **Manufacturer:** "Met.no"
- **Model:** "Forecast"
- **Device Type:** Service
- **Configuration URL:** https://www.met.no/en
- **Associated Entities:** weather.met_no

## Customization Options

### User Customization

Users can customize device display:

1. **Device Name** - Set `name_by_user` via device registry update API
2. **Entity Name** - Set entity `name` via entity registry update API
3. **Area Assignment** - Assign device to area
4. **Labels** - Add labels to device/entity

### API for Customization

**Update Device:**
```json
{
  "type": "config/device_registry/update",
  "device_id": "abc123...",
  "name_by_user": "My Custom Weather"
}
```

**Result:** Frontend displays "My Custom Weather" instead of "Forecast"

## Summary

The display of "Met.no" manufacturer and "Forecast" device name follows this logic:

1. **Integration Sets Device Info** - Met.no integration hardcodes device info in entity (NOT from API)
2. **Device Registry Created** - Device entry created with name "Forecast" and manufacturer "Met.no"
3. **Entity Linked to Device** - Weather entity associated with device via device_id
4. **Frontend Retrieves Data** - Frontend gets device and entity info via WebSocket APIs
5. **Frontend Displays** - Frontend shows device name "Forecast" and manufacturer "Met.no"

**Key Points:**
- **Device information is hardcoded** - NOT retrieved from Met.no API backend
- Device name "Forecast" is hardcoded in integration code (`weather.py:133`)
- Manufacturer "Met.no" is hardcoded in integration code (`weather.py:136`)
- The Met.no API (`https://aa015h6buqvih86i1.api.met.no/...`) provides **only weather data**, not device metadata
- Device type is SERVICE (cloud service, not physical device)
- Frontend prioritizes user custom name over device name
- Entity uses device name when `has_entity_name = True`
- Device information flows through device registry and entity registry
- Frontend combines data from both registries for display

**API vs Device Info:**
- **Met.no API** → Provides weather data (temperature, forecasts, conditions)
- **Integration Code** → Provides device information (name, manufacturer, model)
- The API endpoint `https://www.met.no/en` is referenced in `configuration_url` but device info comes from code, not API responses

