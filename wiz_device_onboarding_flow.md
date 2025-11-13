# WiZ Device Onboarding Flow - Complete API Guide

## Overview

This document provides a comprehensive guide to onboarding WiZ devices (smart lights) into Home Assistant using the WiZ integration. The WiZ integration supports multiple onboarding paths: automatic discovery (DHCP), integration discovery, and manual setup.

## Integration Details

- **Domain:** `wiz`
- **Integration Name:** WiZ
- **Protocol:** Local Push (IoT Class)
- **Discovery Methods:** DHCP, Integration Discovery
- **Required Field:** IP Address (`host`)

## Onboarding Paths

WiZ devices can be onboarded through three different paths:

1. **DHCP Discovery** - Automatic discovery when device appears on network
2. **Integration Discovery** - Programmatic discovery via API
3. **Manual User Flow** - User manually enters IP or selects from discovered devices

## Path 1: DHCP Discovery (Automatic)

### Flow Overview

When a WiZ device appears on the network, Home Assistant automatically discovers it via DHCP and creates a config flow.

### Step 1: Device Discovery

**Trigger:** Automatic (DHCP discovery)

**What Happens:**
- Home Assistant monitors DHCP traffic
- When a device with WiZ MAC address patterns is detected, discovery is triggered
- MAC address patterns: `A8BB50*`, `D8A011*`, `444F8E*`, `6C2990*`, or hostname `wiz_*`

**No API Call Required** - This happens automatically

### Step 2: Discovery Confirmation

**WebSocket Command:** `config_entries/flow/subscribe` (to receive flow notifications)

**Or Check Flow Progress:**

**REST API:**
```http
GET /api/config/config_entries/flow/{flow_id}
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "flow_id": "flow_123",
  "handler": "wiz",
  "type": "form",
  "step_id": "discovery_confirm",
  "description": "Do you want to set up WiZ Light AA:BB:CC (192.168.1.100)?",
  "description_placeholders": {
    "name": "WiZ Light AA:BB:CC",
    "host": "192.168.1.100"
  }
}
```

### Step 3: Confirm Discovery

**REST API:**
```http
POST /api/config/config_entries/flow/{flow_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{}
```

**Response (Config Entry Created):**
```json
{
  "flow_id": "flow_123",
  "handler": "wiz",
  "type": "create_entry",
  "title": "WiZ Light AA:BB:CC",
  "version": 1,
  "minor_version": 1,
  "result": {
    "entry_id": "abc123def456",
    "domain": "wiz",
    "title": "WiZ Light AA:BB:CC",
    "source": "dhcp",
    "state": "loaded",
    "created_at": 1234567890.123,
    "modified_at": 1234567890.123,
    ...
  }
}
```

**Note:** If onboarding is not complete (`onboarding.async_is_onboarded` is False), the device is automatically added without confirmation.

## Path 2: Integration Discovery (Programmatic)

### Flow Overview

This path allows programmatic discovery and onboarding of WiZ devices.

### Step 1: Trigger Integration Discovery

**Internal API:** This is typically triggered internally by Home Assistant, but you can monitor for flows created with `source: "integration_discovery"`.

**Discovery Data:**
```json
{
  "ip_address": "192.168.1.100",
  "mac_address": "A8BB50CCDDEE"
}
```

### Step 2: Monitor Flow Creation

**WebSocket Command:**
```json
{
  "id": 1,
  "type": "config_entries/flow/subscribe"
}
```

**Events:**
```json
{
  "id": 1,
  "type": "event",
  "event": [
    {
      "type": "added",
      "flow_id": "flow_123",
      "flow": {
        "flow_id": "flow_123",
        "handler": "wiz",
        "step_id": "discovery_confirm",
        "context": {
          "source": "integration_discovery"
        }
      }
    }
  ]
}
```

### Step 3: Confirm Discovery

Same as Path 1, Step 3 - POST to the flow with empty body.

## Path 3: Manual User Flow

### Flow Overview

User manually initiates the flow and can either:
- Enter an IP address directly
- Leave IP empty to discover devices on the network

### Step 1: Initialize Config Flow

**REST API:**
```http
POST /api/config/config_entries/flow
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "handler": "wiz",
  "show_advanced_options": false
}
```

**Response:**
```json
{
  "flow_id": "flow_123",
  "handler": "wiz",
  "type": "form",
  "step_id": "user",
  "data_schema": [
    {
      "name": "host",
      "required": false,
      "type": "string",
      "default": ""
    }
  ],
  "description": "If you leave the IP Address empty, discovery will be used to find devices.",
  "errors": {}
}
```

### Step 2A: Enter IP Address Directly

**REST API:**
```http
POST /api/config/config_entries/flow/flow_123
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "host": "192.168.1.100"
}
```

**Response (Success - Config Entry Created):**
```json
{
  "flow_id": "flow_123",
  "handler": "wiz",
  "type": "create_entry",
  "title": "WiZ Light AA:BB:CC",
  "version": 1,
  "minor_version": 1,
  "result": {
    "entry_id": "abc123def456",
    "domain": "wiz",
    "title": "WiZ Light AA:BB:CC",
    "source": "user",
    "state": "loaded",
    ...
  }
}
```

**Response (Error - Validation Failed):**
```json
{
  "flow_id": "flow_123",
  "handler": "wiz",
  "type": "form",
  "step_id": "user",
  "errors": {
    "base": "no_ip"
  },
  "data_schema": [...]
}
```

**Possible Errors:**
- `"no_ip"`: Not a valid IP address
- `"bulb_time_out"`: Cannot connect to bulb (timeout)
- `"cannot_connect"`: Connection refused
- `"no_wiz_light"`: Device is not a WiZ light
- `"unknown"`: Unexpected error

### Step 2B: Leave IP Empty (Discovery)

**REST API:**
```http
POST /api/config/config_entries/flow/flow_123
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "host": ""
}
```

**Response (Discovery Started):**
```json
{
  "flow_id": "flow_123",
  "handler": "wiz",
  "type": "form",
  "step_id": "pick_device",
  "data_schema": [
    {
      "name": "device",
      "required": true,
      "type": "select",
      "options": {
        "A8BB50CCDDEE": "WiZ AA:BB:CC (192.168.1.100)",
        "D8A011EEDDFF": "WiZ DD:EE:FF (192.168.1.101)"
      }
    }
  ],
  "errors": {}
}
```

**Response (No Devices Found):**
```json
{
  "flow_id": "flow_123",
  "handler": "wiz",
  "type": "abort",
  "reason": "no_devices_found"
}
```

### Step 3: Select Device from Discovery

**REST API:**
```http
POST /api/config/config_entries/flow/flow_123
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "device": "A8BB50CCDDEE"
}
```

**Response (Config Entry Created):**
```json
{
  "flow_id": "flow_123",
  "handler": "wiz",
  "type": "create_entry",
  "title": "WiZ Light AA:BB:CC",
  "version": 1,
  "minor_version": 1,
  "result": {
    "entry_id": "abc123def456",
    "domain": "wiz",
    "title": "WiZ Light AA:BB:CC",
    "source": "user",
    "state": "loaded",
    ...
  }
}
```

## Complete Flow Examples

### Example 1: Manual Setup with IP Address

```bash
# Step 1: Initialize flow
POST /api/config/config_entries/flow
{
  "handler": "wiz"
}

# Response: flow_id = "flow_123", step_id = "user"

# Step 2: Submit IP address
POST /api/config/config_entries/flow/flow_123
{
  "host": "192.168.1.100"
}

# Response: type = "create_entry", entry created
```

### Example 2: Manual Setup with Discovery

```bash
# Step 1: Initialize flow
POST /api/config/config_entries/flow
{
  "handler": "wiz"
}

# Response: flow_id = "flow_123", step_id = "user"

# Step 2: Trigger discovery (empty host)
POST /api/config/config_entries/flow/flow_123
{
  "host": ""
}

# Response: flow_id = "flow_123", step_id = "pick_device", devices listed

# Step 3: Select device
POST /api/config/config_entries/flow/flow_123
{
  "device": "A8BB50CCDDEE"
}

# Response: type = "create_entry", entry created
```

### Example 3: DHCP Discovery (Automatic)

```bash
# Step 1: Monitor for flows (WebSocket)
{
  "id": 1,
  "type": "config_entries/flow/subscribe"
}

# Event received when device discovered:
{
  "id": 1,
  "type": "event",
  "event": [{
    "type": "added",
    "flow_id": "flow_123",
    "flow": {
      "step_id": "discovery_confirm",
      "handler": "wiz"
    }
  }]
}

# Step 2: Confirm discovery
POST /api/config/config_entries/flow/flow_123
{}

# Response: type = "create_entry", entry created
```

## Device Connection Process

During onboarding, the integration performs the following operations:

1. **Connect to Device:** Creates a `wizlight` connection to the IP address
2. **Get Bulb Type:** Calls `bulb.get_bulbtype()` to identify the device
3. **Get MAC Address:** Calls `bulb.getMac()` to get unique identifier
4. **Generate Name:** Creates device name from bulb type and MAC address
5. **Set Unique ID:** Uses MAC address as unique identifier
6. **Check Duplicates:** Aborts if device already configured

## Error Handling

### Connection Errors

| Error Code | Description | Solution |
|------------|-------------|----------|
| `bulb_time_out` | Cannot connect to bulb (timeout) | Ensure device is powered on and on the network |
| `cannot_connect` | Connection refused | Check IP address and network connectivity |
| `no_wiz_light` | Device is not a WiZ light | Verify device supports WiZ protocol |
| `no_ip` | Invalid IP address format | Enter valid IPv4 address |
| `unknown` | Unexpected error | Check logs for details |

### Duplicate Device

**Response:**
```json
{
  "flow_id": "flow_123",
  "handler": "wiz",
  "type": "abort",
  "reason": "already_configured"
}
```

**Action:** Device is already configured. Check existing config entries.

### No Devices Found

**Response:**
```json
{
  "flow_id": "flow_123",
  "handler": "wiz",
  "type": "abort",
  "reason": "no_devices_found"
}
```

**Action:** Ensure WiZ devices are powered on and on the same network.

## Device Naming Convention

Devices are automatically named using the format:
```
{bulb_type} {short_mac}
```

Example: `WiZ Light AA:BB:CC`

Where:
- `bulb_type`: Retrieved from device (e.g., "WiZ Light")
- `short_mac`: Last 6 characters of MAC address (e.g., "AA:BB:CC")

## Discovery Timeout

The discovery process uses a timeout defined in constants:
- **Default Timeout:** `DISCOVER_SCAN_TIMEOUT` (typically 5-10 seconds)

During discovery:
- System scans all network broadcast addresses
- Waits for WiZ devices to respond
- Combines results from all network interfaces
- Filters out already configured devices

## WebSocket APIs for Monitoring

### Subscribe to Flow Changes

**Command:** `config_entries/flow/subscribe`

**Request:**
```json
{
  "id": 1,
  "type": "config_entries/flow/subscribe"
}
```

**Events:**
```json
{
  "id": 1,
  "type": "event",
  "event": [
    {
      "type": "added",
      "flow_id": "flow_123",
      "flow": {
        "flow_id": "flow_123",
        "handler": "wiz",
        "step_id": "discovery_confirm",
        "context": {
          "source": "dhcp"
        }
      }
    }
  ]
}
```

### Get Flow Progress

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
      "handler": "wiz",
      "step_id": "discovery_confirm",
      "context": {
        "source": "dhcp"
      }
    }
  ]
}
```

**Note:** This only returns flows not started by a user (discovery flows).

## Config Entry Data Structure

After successful onboarding, the config entry contains:

```json
{
  "entry_id": "abc123def456",
  "domain": "wiz",
  "title": "WiZ Light AA:BB:CC",
  "data": {
    "host": "192.168.1.100"
  },
  "source": "user",
  "state": "loaded",
  "unique_id": "A8BB50CCDDEE"
}
```

**Key Fields:**
- `data.host`: IP address of the WiZ device
- `unique_id`: MAC address of the device
- `title`: Auto-generated device name

## Post-Onboarding

After the config entry is created:

1. **Integration Setup:** `async_setup_entry()` is called
2. **Device Registration:** Device is registered in device registry
3. **Entity Creation:** Light entities are created for the device
4. **Platform Setup:** Light platform is set up with the device

## Best Practices

### 1. Handle Multiple Discovery Methods

- Monitor both DHCP and integration discovery flows
- Use `config_entries/flow/subscribe` to receive real-time notifications
- Check flow `context.source` to identify discovery method

### 2. Error Recovery

- Retry connection errors (device may be temporarily offline)
- Validate IP addresses before submission
- Provide user feedback for timeout errors

### 3. Discovery Optimization

- Use manual IP entry for faster setup when IP is known
- Use discovery when IP is unknown or multiple devices need setup
- Cache discovered devices to avoid repeated scans

### 4. User Experience

- Show discovered devices with clear identifiers (MAC + IP)
- Provide option to enter IP manually if discovery fails
- Display connection status during device verification

## Code References

**Config Flow:**
- `homeassistant/components/wiz/config_flow.py` - Complete flow implementation

**Discovery:**
- `homeassistant/components/wiz/discovery.py` - Device discovery logic

**Constants:**
- `homeassistant/components/wiz/const.py` - Timeout and configuration constants

**Manifest:**
- `homeassistant/components/wiz/manifest.json` - DHCP discovery patterns

## Summary

WiZ device onboarding supports three paths:

1. **DHCP Discovery:** Automatic - monitor flows and confirm
2. **Integration Discovery:** Programmatic - trigger and confirm
3. **Manual Flow:** User-initiated - enter IP or discover devices

**Key APIs:**
- `POST /api/config/config_entries/flow` - Initialize flow
- `POST /api/config/config_entries/flow/{flow_id}` - Submit steps
- `GET /api/config/config_entries/flow/{flow_id}` - Check flow status
- `config_entries/flow/subscribe` (WebSocket) - Monitor flow changes

**Required Data:**
- IP address (`host`) - Can be entered manually or discovered

**Device Identification:**
- MAC address used as unique ID
- Device name auto-generated from bulb type and MAC



