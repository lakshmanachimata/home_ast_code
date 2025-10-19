#!/usr/bin/env python3
"""
Swagger UI Integration Generator for Home Assistant

This script automatically generates the Swagger UI integration files
whenever Home Assistant is built or launched. It ensures the Swagger UI
is always up-to-date with the latest API endpoints.

Usage:
    python generate_swagger_integration.py
"""

import os
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_directory_exists(path):
    """Ensure directory exists, create if it doesn't."""
    Path(path).mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured directory exists: {path}")

def generate_swagger_init():
    """Generate the __init__.py file for the Swagger UI integration."""
    content = '''"""The Swagger UI integration."""
import os
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from .http import SwaggerUIView, SwaggerSpecView

DOMAIN = "swagger_ui"

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Swagger UI component."""
    hass.http.register_view(SwaggerUIView())
    hass.http.register_view(SwaggerSpecView())
    return True
'''
    
    init_path = "homeassistant/components/swagger_ui/__init__.py"
    ensure_directory_exists(os.path.dirname(init_path))
    
    with open(init_path, 'w') as f:
        f.write(content)
    
    logger.info(f"Generated: {init_path}")

def generate_swagger_manifest():
    """Generate the manifest.json file for the Swagger UI integration."""
    manifest = {
        "domain": "swagger_ui",
        "name": "Swagger UI",
        "codeowners": [],
        "dependencies": ["http"],
        "documentation": "https://www.home-assistant.io/integrations/swagger_ui",
        "issue_tracker": "https://github.com/home-assistant/core/issues?q=is%3Aissue+is%3Aopen+label%3A%22integration%3A+swagger_ui%22",
        "requirements": [],
        "version": "0.1.0"
    }
    
    manifest_path = "homeassistant/components/swagger_ui/manifest.json"
    ensure_directory_exists(os.path.dirname(manifest_path))
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    logger.info(f"Generated: {manifest_path}")

def generate_swagger_http():
    """Generate the http.py file with complete API endpoints."""
    content = '''import json
import logging
from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant
from homeassistant.const import (
    CONTENT_TYPE_JSON,
    URL_API,
    URL_API_COMPONENTS,
    URL_API_CONFIG,
    URL_API_CORE_STATE,
    URL_API_EVENTS,
    URL_API_SERVICES,
    URL_API_STATES,
    URL_API_STREAM,
    URL_API_TEMPLATE,
)
from homeassistant.helpers.json import json_dumps

_LOGGER = logging.getLogger(__name__)

SWAGGER_UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta
        name="description"
        content="SwaggerUI for Home Assistant API"
    />
    <title>Swagger UI</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.1/swagger-ui.css" />
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.1/swagger-ui-bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.1/swagger-ui-standalone-preset.js"></script>
<script>
    window.onload = function() {
        window.ui = SwaggerUIBundle({
            url: "/api/swagger/spec", // Our dynamically generated spec
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIStandalonePreset
            ],
            plugins: [
                SwaggerUIBundle.plugins.DownloadUrl
            ],
            layout: "StandaloneLayout",
            oauth2RedirectUrl: window.location.origin + '/api/swagger/oauth2-redirect.html'
        });
    };
</script>
</body>
</html>
"""

class SwaggerUIView(HomeAssistantView):
    """Web view for Swagger UI."""

    url = "/api/swagger"
    name = "api:swagger"
    requires_auth = False

    async def get(self, request: web.Request) -> web.Response:
        """Serve the Swagger UI."""
        return web.Response(text=SWAGGER_UI_HTML, content_type="text/html")

class SwaggerSpecView(HomeAssistantView):
    """Web view for OpenAPI specification."""

    url = "/api/swagger/spec"
    name = "api:swagger:spec"
    requires_auth = False # Spec itself doesn't require auth, but API calls will

    async def get(self, request: web.Request) -> web.Response:
        """Return the OpenAPI specification."""
        hass = request.app["hass"]
        spec = await self._generate_openapi_spec(hass)
        return web.Response(text=json_dumps(spec), content_type=CONTENT_TYPE_JSON)

    async def _generate_openapi_spec(self, hass: HomeAssistant):
        """Dynamically generate the OpenAPI specification."""
        return {
            "openapi": "3.0.3",
            "info": {
                "title": "Home Assistant API",
                "description": "REST API for Home Assistant home automation platform",
                "version": "2024.10.0",
                "contact": {
                    "name": "Home Assistant",
                    "url": "https://www.home-assistant.io/",
                    "email": "hello@home-assistant.io"
                },
                "license": {
                    "name": "Apache 2.0",
                    "url": "https://github.com/home-assistant/core/blob/dev/LICENSE"
                }
            },
            "servers": [
                {"url": "http://localhost:8123", "description": "Home Assistant instance"}
            ],
            "security": [
                {"bearerAuth": []},
                {"basicAuth": []}
            ],
            "paths": {
                "/api/": {
                    "get": {
                        "summary": "API Status",
                        "description": "Returns a message if the API is up and running",
                        "tags": ["System"],
                        "responses": {
                            "200": {
                                "description": "API is running",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "message": {"type": "string", "example": "API running."}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/config": {
                    "get": {
                        "summary": "Get Configuration",
                        "description": "Returns the current configuration as JSON",
                        "tags": ["Configuration"],
                        "responses": {
                            "200": {
                                "description": "Configuration retrieved successfully",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "components": {"type": "array", "items": {"type": "string"}},
                                                "config_dir": {"type": "string"},
                                                "elevation": {"type": "number"},
                                                "latitude": {"type": "number"},
                                                "longitude": {"type": "number"},
                                                "location_name": {"type": "string"},
                                                "time_zone": {"type": "string"},
                                                "unit_system": {"type": "object"},
                                                "version": {"type": "string"},
                                                "whitelist_external_dirs": {"type": "array", "items": {"type": "string"}},
                                                "allowlist_external_dirs": {"type": "array", "items": {"type": "string"}},
                                                "allowlist_external_urls": {"type": "array", "items": {"type": "string"}}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/components": {
                    "get": {
                        "summary": "Get Components",
                        "description": "Returns a list of currently loaded components",
                        "tags": ["System"],
                        "responses": {
                            "200": {
                                "description": "Components retrieved successfully",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "example": ["currentcost.sensor", "tapo.switch", "tuya_ble.sensor", "backup", "ble_monitor.binary_sensor"]
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/events": {
                    "get": {
                        "summary": "Get Event Listeners",
                        "description": "Returns an array of event objects. Each event object contains event name and listener count",
                        "tags": ["Events"],
                        "responses": {
                            "200": {
                                "description": "Event listeners retrieved successfully",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "event": {"type": "string"},
                                                    "listener_count": {"type": "number"}
                                                }
                                            },
                                            "example": [
                                                {"event": "state_changed", "listener_count": 5},
                                                {"event": "time_changed", "listener_count": 2}
                                            ]
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/events/{event_type}": {
                    "post": {
                        "summary": "Fire Event",
                        "description": "Fires an event with event_type. Please be mindful of the data structure",
                        "tags": ["Events"],
                        "parameters": [
                            {
                                "name": "event_type",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                                "description": "Event type to fire"
                            }
                        ],
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "description": "Optional event data"
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Event fired successfully",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "message": {"type": "string", "example": "Event download_file fired."}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/services": {
                    "get": {
                        "summary": "Get All Services",
                        "description": "Returns an array of service objects. Each object contains the domain and which services it contains",
                        "tags": ["Services"],
                        "responses": {
                            "200": {
                                "description": "Services retrieved successfully",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "domain": {"type": "string"},
                                                    "services": {"type": "array", "items": {"type": "string"}}
                                                }
                                            },
                                            "example": [
                                                {"domain": "browser", "services": ["browse_url"]},
                                                {"domain": "keyboard", "services": ["volume_up", "volume_down"]}
                                            ]
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/services/{domain}/{service}": {
                    "post": {
                        "summary": "Call Service",
                        "description": "Calls a service within a specific domain. Will return when the service has been executed",
                        "tags": ["Services"],
                        "parameters": [
                            {
                                "name": "domain",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                                "description": "Service domain (e.g., light, switch)"
                            },
                            {
                                "name": "service",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                                "description": "Service name (e.g., turn_on, turn_off)"
                            },
                            {
                                "name": "return_response",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "boolean"},
                                "description": "Return service response data if supported"
                            }
                        ],
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "entity_id": {"type": "string"},
                                            "area_id": {"type": "string"},
                                            "device_id": {"type": "string"}
                                        },
                                        "example": {"entity_id": "light.study_light"}
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Service called successfully",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "oneOf": [
                                                {
                                                    "type": "array",
                                                    "items": {"$ref": "#/components/schemas/State"},
                                                    "description": "List of changed states"
                                                },
                                                {
                                                    "type": "object",
                                                    "properties": {
                                                        "changed_states": {
                                                            "type": "array",
                                                            "items": {"$ref": "#/components/schemas/State"}
                                                        },
                                                        "service_response": {"type": "object"}
                                                    },
                                                    "description": "Response with service data (when return_response=true)"
                                                }
                                            ]
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/states": {
                    "get": {
                        "summary": "Get All States",
                        "description": "Get current states of all entities",
                        "tags": ["States"],
                        "responses": {
                            "200": {
                                "description": "States retrieved successfully",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/State"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/states/{entity_id}": {
                    "get": {
                        "summary": "Get Entity State",
                        "description": "Get current state of a specific entity",
                        "tags": ["States"],
                        "parameters": [
                            {
                                "name": "entity_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                                "description": "Entity ID (e.g., light.living_room)"
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Entity state retrieved successfully",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/State"}
                                    }
                                }
                            },
                            "404": {
                                "description": "Entity not found"
                            }
                        }
                    },
                    "post": {
                        "summary": "Update Entity State",
                        "description": "Update state of a specific entity",
                        "tags": ["States"],
                        "parameters": [
                            {
                                "name": "entity_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                                "description": "Entity ID (e.g., sensor.kitchen_temperature)"
                            }
                        ],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["state"],
                                        "properties": {
                                            "state": {"type": "string", "description": "New state value"},
                                            "attributes": {"type": "object", "description": "Entity attributes"},
                                            "force_update": {"type": "boolean", "default": False, "description": "Force update even if state hasn't changed"}
                                        },
                                        "example": {"state": "25", "attributes": {"unit_of_measurement": "°C"}}
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "State updated successfully",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/State"}
                                    }
                                }
                            },
                            "201": {
                                "description": "New entity created",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/State"}
                                    }
                                }
                            },
                            "400": {
                                "description": "Invalid request data"
                            }
                        }
                    },
                    "delete": {
                        "summary": "Delete Entity",
                        "description": "Deletes an entity with the specified entity_id",
                        "tags": ["States"],
                        "parameters": [
                            {
                                "name": "entity_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                                "description": "Entity ID to delete"
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Entity deleted successfully"
                            },
                            "404": {
                                "description": "Entity not found"
                            }
                        }
                    }
                },
                "/api/history/period/{timestamp}": {
                    "get": {
                        "summary": "Get History",
                        "description": "Returns an array of state changes in the past. Each object contains further details for the entities",
                        "tags": ["History"],
                        "parameters": [
                            {
                                "name": "timestamp",
                                "in": "path",
                                "required": False,
                                "schema": {"type": "string", "format": "date-time"},
                                "description": "YYYY-MM-DDThh:mm:ssTZD format, defaults to 1 day before request time"
                            },
                            {
                                "name": "filter_entity_id",
                                "in": "query",
                                "required": True,
                                "schema": {"type": "string"},
                                "description": "Filter on one or more entities - comma separated"
                            },
                            {
                                "name": "end_time",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "string", "format": "date-time"},
                                "description": "End of the period in URL encoded format (defaults to 1 day)"
                            },
                            {
                                "name": "minimal_response",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "boolean"},
                                "description": "Only return last_changed and state for states other than the first and last state (much faster)"
                            },
                            {
                                "name": "no_attributes",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "boolean"},
                                "description": "Skip returning attributes from the database (much faster)"
                            },
                            {
                                "name": "significant_changes_only",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "boolean"},
                                "description": "Only return significant state changes"
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "History retrieved successfully",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/State"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/logbook/{timestamp}": {
                    "get": {
                        "summary": "Get Logbook",
                        "description": "Get logbook entries for a specific timestamp",
                        "tags": ["Logbook"],
                        "parameters": [
                            {
                                "name": "timestamp",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string", "format": "date-time"},
                                "description": "Timestamp for logbook entries"
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Logbook entries retrieved successfully",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/error_log": {
                    "get": {
                        "summary": "Get Error Log",
                        "description": "Get the current error log",
                        "tags": ["System"],
                        "responses": {
                            "200": {
                                "description": "Error log retrieved successfully",
                                "content": {
                                    "text/plain": {
                                        "schema": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/camera_proxy/{camera_entity_id}": {
                    "get": {
                        "summary": "Camera Proxy",
                        "description": "Get camera image through proxy",
                        "tags": ["Camera"],
                        "parameters": [
                            {
                                "name": "camera_entity_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                                "description": "Camera entity ID"
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Camera image retrieved successfully",
                                "content": {
                                    "image/jpeg": {
                                        "schema": {"type": "string", "format": "binary"}
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/calendars": {
                    "get": {
                        "summary": "Get All Calendars",
                        "description": "Get all available calendars",
                        "tags": ["Calendar"],
                        "responses": {
                            "200": {
                                "description": "Calendars retrieved successfully",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/calendars/{calendar_entity_id}": {
                    "get": {
                        "summary": "Get Calendar Events",
                        "description": "Get events for a specific calendar within a time range",
                        "tags": ["Calendar"],
                        "parameters": [
                            {
                                "name": "calendar_entity_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                                "description": "Calendar entity ID"
                            },
                            {
                                "name": "start",
                                "in": "query",
                                "required": True,
                                "schema": {"type": "string", "format": "date-time"},
                                "description": "Start timestamp"
                            },
                            {
                                "name": "end",
                                "in": "query",
                                "required": True,
                                "schema": {"type": "string", "format": "date-time"},
                                "description": "End timestamp"
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Calendar events retrieved successfully",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/template": {
                    "post": {
                        "summary": "Render Template",
                        "description": "Render a Home Assistant template",
                        "tags": ["Templates"],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["template"],
                                        "properties": {
                                            "template": {"type": "string", "description": "Jinja2 template to render"}
                                        },
                                        "example": {"template": "Paulus is at {{ states('device_tracker.paulus') }}!"}
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Template rendered successfully",
                                "content": {
                                    "text/plain": {
                                        "schema": {"type": "string", "example": "Paulus is at work!"}
                                    }
                                }
                            },
                            "400": {
                                "description": "Template error"
                            }
                        }
                    }
                },
                "/api/config/core/check_config": {
                    "post": {
                        "summary": "Check Configuration",
                        "description": "Trigger a check of configuration.yaml. No additional data needs to be passed in with this request. Needs config integration enabled",
                        "tags": ["Configuration"],
                        "responses": {
                            "200": {
                                "description": "Configuration check completed",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "errors": {"type": "string", "nullable": True},
                                                "result": {"type": "string", "enum": ["valid", "invalid"]}
                                            },
                                            "example": {"errors": None, "result": "valid"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/intent/handle": {
                    "post": {
                        "summary": "Handle Intent",
                        "description": "Handle an intent. You must add intent: to your configuration.yaml to enable this endpoint",
                        "tags": ["Intents"],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["name"],
                                        "properties": {
                                            "name": {"type": "string", "description": "Intent name"},
                                            "data": {"type": "object", "description": "Intent data"}
                                        },
                                        "example": {"name": "SetTimer", "data": {"seconds": "30"}}
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Intent handled successfully",
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object"}
                                    }
                                }
                            }
                        }
                    }
                },
                "/api/websocket": {
                    "get": {
                        "summary": "WebSocket API",
                        "description": "Establish a WebSocket connection for real-time communication with Home Assistant. Supports authentication, event subscription, service calls, and state management.",
                        "tags": ["WebSocket"],
                        "parameters": [
                            {
                                "name": "Authorization",
                                "in": "header",
                                "required": True,
                                "schema": {"type": "string"},
                                "description": "Bearer token for authentication (e.g., 'Bearer YOUR_ACCESS_TOKEN')"
                            }
                        ],
                        "responses": {
                            "101": {
                                "description": "WebSocket handshake successful. Connection established.",
                                "headers": {
                                    "Upgrade": {"schema": {"type": "string", "example": "websocket"}},
                                    "Connection": {"schema": {"type": "string", "example": "Upgrade"}},
                                    "Sec-WebSocket-Accept": {"schema": {"type": "string"}}
                                }
                            },
                            "401": {
                                "description": "Authentication required"
                            },
                            "400": {
                                "description": "Invalid WebSocket request"
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "State": {
                        "type": "object",
                        "properties": {
                            "entity_id": {"type": "string"},
                            "state": {"type": "string"},
                            "attributes": {"type": "object"},
                            "last_changed": {"type": "string", "format": "date-time"},
                            "last_updated": {"type": "string", "format": "date-time"},
                            "context": {"type": "object"}
                        }
                    },
                    "WebSocketAuthMessage": {
                        "type": "object",
                        "required": ["type", "access_token"],
                        "properties": {
                            "type": {"type": "string", "enum": ["auth"], "example": "auth"},
                            "access_token": {"type": "string", "description": "Long-lived access token"}
                        }
                    },
                    "WebSocketAuthRequired": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["auth_required"], "example": "auth_required"},
                            "ha_version": {"type": "string", "example": "2024.10.0"}
                        }
                    },
                    "WebSocketAuthOk": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["auth_ok"], "example": "auth_ok"},
                            "ha_version": {"type": "string", "example": "2024.10.0"}
                        }
                    },
                    "WebSocketAuthInvalid": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["auth_invalid"], "example": "auth_invalid"},
                            "message": {"type": "string", "example": "Invalid password"}
                        }
                    },
                    "WebSocketSubscribeEvents": {
                        "type": "object",
                        "required": ["id", "type"],
                        "properties": {
                            "id": {"type": "integer", "example": 18},
                            "type": {"type": "string", "enum": ["subscribe_events"], "example": "subscribe_events"},
                            "event_type": {"type": "string", "description": "Optional: specific event type to subscribe to", "example": "state_changed"}
                        }
                    },
                    "WebSocketEventMessage": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "example": 18},
                            "type": {"type": "string", "enum": ["event"], "example": "event"},
                            "event": {
                                "type": "object",
                                "properties": {
                                    "data": {"type": "object"},
                                    "event_type": {"type": "string", "example": "state_changed"},
                                    "time_fired": {"type": "string", "format": "date-time"},
                                    "origin": {"type": "string", "example": "LOCAL"},
                                    "context": {"type": "object"}
                                }
                            }
                        }
                    },
                    "WebSocketCallService": {
                        "type": "object",
                        "required": ["id", "type", "domain", "service"],
                        "properties": {
                            "id": {"type": "integer", "example": 24},
                            "type": {"type": "string", "enum": ["call_service"], "example": "call_service"},
                            "domain": {"type": "string", "example": "light"},
                            "service": {"type": "string", "example": "turn_on"},
                            "service_data": {"type": "object", "description": "Optional service data"},
                            "target": {
                                "type": "object",
                                "properties": {
                                    "entity_id": {"type": "string", "example": "light.kitchen"},
                                    "area_id": {"type": "string"},
                                    "device_id": {"type": "string"}
                                }
                            },
                            "return_response": {"type": "boolean", "description": "Return service response data if supported"}
                        }
                    },
                    "WebSocketGetStates": {
                        "type": "object",
                        "required": ["id", "type"],
                        "properties": {
                            "id": {"type": "integer", "example": 19},
                            "type": {"type": "string", "enum": ["get_states"], "example": "get_states"}
                        }
                    },
                    "WebSocketResult": {
                        "type": "object",
                        "required": ["id", "type", "success"],
                        "properties": {
                            "id": {"type": "integer", "example": 19},
                            "type": {"type": "string", "enum": ["result"], "example": "result"},
                            "success": {"type": "boolean", "example": True},
                            "result": {"type": "object", "description": "Command result data"},
                            "error": {
                                "type": "object",
                                "properties": {
                                    "code": {"type": "string", "example": "invalid_format"},
                                    "message": {"type": "string", "example": "Message incorrectly formatted"},
                                    "translation_key": {"type": "string"},
                                    "translation_domain": {"type": "string"},
                                    "translation_placeholders": {"type": "object"}
                                }
                            }
                        }
                    }
                },
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "Token",
                        "description": "Long-lived access token"
                    },
                    "basicAuth": {
                        "type": "http",
                        "scheme": "basic"
                    }
                }
            },
            "tags": [
                {"name": "System", "description": "System information and status"},
                {"name": "Configuration", "description": "Configuration management"},
                {"name": "States", "description": "Entity state management"},
                {"name": "Services", "description": "Service calls"},
                {"name": "Events", "description": "Event handling"},
                {"name": "History", "description": "Historical data"},
                {"name": "Logbook", "description": "Logbook entries"},
                {"name": "Templates", "description": "Template rendering"},
                {"name": "Intents", "description": "Intent handling"},
                {"name": "Camera", "description": "Camera proxy and images"},
                {"name": "Calendar", "description": "Calendar events and management"},
                {"name": "WebSocket", "description": "Real-time WebSocket communication with authentication, event subscription, service calls, and state management"}
            ]
        }


def async_register(hass: HomeAssistant) -> None:
    """Register HTTP views."""
'''
    
    http_path = "homeassistant/components/swagger_ui/http.py"
    ensure_directory_exists(os.path.dirname(http_path))
    
    with open(http_path, 'w') as f:
        f.write(content)
    
    logger.info(f"Generated: {http_path}")

def update_configuration_yaml():
    """Update configuration.yaml to include swagger_ui if not already present."""
    config_path = "config/configuration.yaml"
    
    if not os.path.exists(config_path):
        logger.warning(f"Configuration file not found: {config_path}")
        return
    
    with open(config_path, 'r') as f:
        content = f.read()
    
    # Check if swagger_ui is already in the configuration
    if "swagger_ui:" in content:
        logger.info("Swagger UI already configured in configuration.yaml")
        return
    
    # Add swagger_ui to the configuration
    if content.strip():
        content += "\n\n# Swagger UI for API documentation\nswagger_ui:\n"
    else:
        content = "# Swagger UI for API documentation\nswagger_ui:\n"
    
    with open(config_path, 'w') as f:
        f.write(content)
    
    logger.info(f"Updated: {config_path}")

def main():
    """Main function to generate all Swagger UI integration files."""
    logger.info("🚀 Starting Swagger UI Integration Generation...")
    
    try:
        # Generate all integration files
        generate_swagger_init()
        generate_swagger_manifest()
        generate_swagger_http()
        update_configuration_yaml()
        
        logger.info("✅ Swagger UI Integration Generation Complete!")
        logger.info("📁 Generated files:")
        logger.info("   - homeassistant/components/swagger_ui/__init__.py")
        logger.info("   - homeassistant/components/swagger_ui/manifest.json")
        logger.info("   - homeassistant/components/swagger_ui/http.py")
        logger.info("   - config/configuration.yaml (updated)")
        
        logger.info("🌐 Swagger UI will be available at:")
        logger.info("   - http://localhost:8123/api/swagger")
        logger.info("   - http://localhost:8123/api/swagger/spec")
        
    except Exception as e:
        logger.error(f"❌ Error generating Swagger UI integration: {e}")
        raise

if __name__ == "__main__":
    main()
