# Home Assistant Information APIs

This document describes REST API endpoints to get information about Home Assistant.

## Authentication

All endpoints require authentication via:
- **Bearer Token**: Include `Authorization: Bearer YOUR_ACCESS_TOKEN` header
- **Long-Lived Access Token**: Get from Profile → Long-Lived Access Tokens in Home Assistant UI

---

## 1. API Status

Check if the API is running.

**Endpoint:** `GET /api/`

**Authentication:** Not required

**Response:**
```json
{
  "message": "API running."
}
```

**Example:**
```bash
curl http://localhost:8123/api/
```

**Python Example:**
```python
import requests

response = requests.get("http://localhost:8123/api/")
print(response.json())  # {"message": "API running."}
```

---

## 2. Core State

Get the current state of Home Assistant core and recorder status.

**Endpoint:** `GET /api/core/state`

**Authentication:** Required

**Response:**
```json
{
  "state": "running",
  "recorder_state": {
    "migration_in_progress": false,
    "migration_is_live": false
  }
}
```

**State Values:**
- `"not_running"`: Home Assistant is not running
- `"starting"`: Home Assistant is starting up
- `"running"`: Home Assistant is running normally
- `"stopping"`: Home Assistant is shutting down
- `"final_write"`: Home Assistant is in final write state

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8123/api/core/state
```

**Python Example:**
```python
import requests

headers = {"Authorization": "Bearer YOUR_ACCESS_TOKEN"}
response = requests.get("http://localhost:8123/api/core/state", headers=headers)
data = response.json()
print(f"State: {data['state']}")
print(f"Migration in progress: {data['recorder_state']['migration_in_progress']}")
```

---

## 3. Configuration

Get current Home Assistant configuration.

**Endpoint:** `GET /api/config`

**Authentication:** Required

**Response:**
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "elevation": 10,
  "unit_system": {
    "length": "mi",
    "mass": "lb",
    "temperature": "°F",
    "volume": "gal"
  },
  "location_name": "Home",
  "time_zone": "America/New_York",
  "components": [
    "api",
    "automation",
    "config",
    "frontend",
    "history",
    "logbook",
    "map",
    "person",
    "recorder",
    "scene",
    "script",
    "sun",
    "system_health",
    "zeroconf"
  ],
  "config_dir": "/config",
  "whitelist_external_dirs": [],
  "allowlist_external_dirs": [],
  "allowlist_external_urls": [],
  "version": "2025.12.0.dev0",
  "safe_mode": false
}
```

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8123/api/config
```

**Python Example:**
```python
import requests

headers = {"Authorization": "Bearer YOUR_ACCESS_TOKEN"}
response = requests.get("http://localhost:8123/api/config", headers=headers)
config = response.json()
print(f"Location: {config['location_name']}")
print(f"Version: {config['version']}")
print(f"Components: {len(config['components'])} loaded")
```

---

## 4. Loaded Components

Get list of all loaded components/integrations.

**Endpoint:** `GET /api/components`

**Authentication:** Required

**Response:**
```json
[
  "api",
  "automation",
  "config",
  "frontend",
  "history",
  "logbook",
  "map",
  "person",
  "recorder",
  "scene",
  "script",
  "sun",
  "system_health",
  "zeroconf"
]
```

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8123/api/components
```

**Python Example:**
```python
import requests

headers = {"Authorization": "Bearer YOUR_ACCESS_TOKEN"}
response = requests.get("http://localhost:8123/api/components", headers=headers)
components = response.json()
print(f"Loaded {len(components)} components")
for component in components:
    print(f"  - {component}")
```

---

## 5. System Health (WebSocket)

Get detailed system health information. This is available via **WebSocket API** only.

**WebSocket Command:**
```json
{
  "id": 1,
  "type": "system_health/info"
}
```

**Response:**
```json
{
  "id": 1,
  "type": "result",
  "success": true,
  "result": {
    "homeassistant": {
      "version": "core-2025.12.0.dev0",
      "installation_type": "Home Assistant Core",
      "dev": true,
      "hassio": false,
      "docker": false,
      "virtualenv": true,
      "python_version": "3.13.0",
      "os_name": "Darwin",
      "os_version": "24.6.0",
      "arch": "arm64",
      "timezone": "America/New_York",
      "config_dir": "/config"
    },
    "supervisor": {
      "host_os": "Home Assistant OS 12.0",
      "update_channel": "stable",
      "supervisor_version": "supervisor-2024.12.0",
      "docker_version": "24.0.0",
      "disk_total": "32.0 GB",
      "disk_used": "8.5 GB"
    }
  }
}
```

**Python Example:**
```python
import asyncio
import websockets
import json

async def get_system_health(access_token):
    uri = "ws://localhost:8123/api/websocket"
    async with websockets.connect(uri) as websocket:
        # Authenticate
        await websocket.send(json.dumps({
            "type": "auth",
            "access_token": access_token
        }))
        await websocket.recv()
        
        # Get system health
        await websocket.send(json.dumps({
            "id": 1,
            "type": "system_health/info"
        }))
        response = await websocket.recv()
        result = json.loads(response)
        return result["result"]

# Usage
health = asyncio.run(get_system_health("YOUR_ACCESS_TOKEN"))
print(health)
```

---

## 6. All States

Get all entity states (see separate documentation for entity management).

**Endpoint:** `GET /api/states`

**Authentication:** Required

**Response:**
```json
[
  {
    "entity_id": "sun.sun",
    "state": "above_horizon",
    "attributes": {
      "next_dawn": "2024-01-01T06:00:00+00:00",
      "next_dusk": "2024-01-01T18:00:00+00:00",
      "next_midnight": "2024-01-02T00:00:00+00:00",
      "next_noon": "2024-01-01T12:00:00+00:00",
      "next_rising": "2024-01-01T06:30:00+00:00",
      "next_setting": "2024-01-01T18:30:00+00:00",
      "elevation": 45.0,
      "azimuth": 180.0,
      "rising": true,
      "friendly_name": "Sun"
    },
    "last_changed": "2024-01-01T12:00:00+00:00",
    "last_updated": "2024-01-01T12:00:00+00:00",
    "context": {
      "id": "context_id",
      "parent_id": null,
      "user_id": null
    }
  }
]
```

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8123/api/states
```

---

## 7. All Services

Get all available services.

**Endpoint:** `GET /api/services`

**Authentication:** Required

**Response:**
```json
[
  {
    "domain": "homeassistant",
    "services": {
      "restart": {
        "name": "Restart",
        "description": "Restart the Home Assistant instance.",
        "fields": {}
      },
      "stop": {
        "name": "Stop",
        "description": "Stop the Home Assistant instance.",
        "fields": {}
      }
    }
  },
  {
    "domain": "automation",
    "services": {
      "trigger": {
        "name": "Trigger",
        "description": "Trigger the action of an automation.",
        "fields": {
          "entity_id": {
            "description": "Name(s) of entities to trigger",
            "example": "automation.alarm"
          }
        }
      }
    }
  }
]
```

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8123/api/services
```

**Python Example:**
```python
import requests

headers = {"Authorization": "Bearer YOUR_ACCESS_TOKEN"}
response = requests.get("http://localhost:8123/api/services", headers=headers)
services = response.json()

for domain in services:
    print(f"\n{domain['domain']}:")
    for service_name, service_info in domain['services'].items():
        print(f"  - {service_name}: {service_info['description']}")
```

---

## 8. Services by Domain

Get services for a specific domain.

**Endpoint:** `GET /api/services/{domain}`

**Authentication:** Required

**Example:**
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8123/api/services/homeassistant
```

**Response:**
```json
{
  "restart": {
    "name": "Restart",
    "description": "Restart the Home Assistant instance.",
    "fields": {}
  },
  "stop": {
    "name": "Stop",
    "description": "Stop the Home Assistant instance.",
    "fields": {}
  }
}
```

---

## Complete Python Example

```python
import requests
import json

class HomeAssistantInfo:
    def __init__(self, base_url, access_token):
        self.base_url = base_url.rstrip('/')
        self.headers = {"Authorization": f"Bearer {access_token}"}
    
    def get_status(self):
        """Check if API is running."""
        response = requests.get(f"{self.base_url}/api/")
        return response.json()
    
    def get_core_state(self):
        """Get core state."""
        response = requests.get(
            f"{self.base_url}/api/core/state",
            headers=self.headers
        )
        return response.json()
    
    def get_config(self):
        """Get configuration."""
        response = requests.get(
            f"{self.base_url}/api/config",
            headers=self.headers
        )
        return response.json()
    
    def get_components(self):
        """Get loaded components."""
        response = requests.get(
            f"{self.base_url}/api/components",
            headers=self.headers
        )
        return response.json()
    
    def get_services(self, domain=None):
        """Get services (all or for specific domain)."""
        url = f"{self.base_url}/api/services"
        if domain:
            url += f"/{domain}"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_all_info(self):
        """Get all available information."""
        return {
            "status": self.get_status(),
            "core_state": self.get_core_state(),
            "config": self.get_config(),
            "components": self.get_components(),
            "services": self.get_services()
        }

# Usage
ha = HomeAssistantInfo("http://localhost:8123", "YOUR_ACCESS_TOKEN")

# Get all info
info = ha.get_all_info()
print(json.dumps(info, indent=2))

# Or get specific info
print(f"State: {ha.get_core_state()['state']}")
print(f"Version: {ha.get_config()['version']}")
print(f"Components: {len(ha.get_components())}")
```

---

## Error Responses

All endpoints return standard HTTP status codes:

- **200 OK**: Success
- **401 Unauthorized**: Invalid or missing authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Endpoint not found
- **500 Internal Server Error**: Server error

**Error Response Format:**
```json
{
  "message": "Error message here"
}
```

---

## Notes

1. **API Status** (`/api/`) does not require authentication - it's a simple health check.

2. **All other endpoints** require authentication with a valid access token.

3. **System Health** information is only available via WebSocket API, not REST API.

4. **Configuration** endpoint returns the current runtime configuration, not the YAML files.

5. **Components** list shows all loaded integrations/components, not all available ones.

6. **Services** endpoint shows all available services across all domains.

---

## Quick Reference

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/` | GET | No | Check API status |
| `/api/core/state` | GET | Yes | Get core state |
| `/api/config` | GET | Yes | Get configuration |
| `/api/components` | GET | Yes | Get loaded components |
| `/api/services` | GET | Yes | Get all services |
| `/api/services/{domain}` | GET | Yes | Get services for domain |
| `/api/states` | GET | Yes | Get all entity states |

