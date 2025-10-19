"""HTTP views for Swagger UI integration."""

import json
import logging
from typing import Any

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class SwaggerUIView(HomeAssistantView):
    """View to serve Swagger UI."""

    url = "/api/swagger"
    name = "api:swagger"
    requires_auth = False

    async def get(self, request: web.Request) -> web.Response:
        """Serve Swagger UI HTML page."""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home Assistant API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
    <style>
        html {
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }
        *, *:before, *:after {
            box-sizing: inherit;
        }
        body {
            margin:0;
            background: #fafafa;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: '/api/swagger/spec',
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
                tryItOutEnabled: true,
                requestInterceptor: function(request) {
                    // Add authentication header if available
                    const token = localStorage.getItem('ha_token');
                    if (token) {
                        request.headers['Authorization'] = 'Bearer ' + token;
                    }
                    return request;
                }
            });
        };
    </script>
</body>
</html>
        """
        return web.Response(text=html_content, content_type="text/html")


class SwaggerSpecView(HomeAssistantView):
    """View to serve OpenAPI specification."""

    url = "/api/swagger/spec"
    name = "api:swagger:spec"
    requires_auth = False

    async def get(self, request: web.Request) -> web.Response:
        """Generate and serve OpenAPI specification."""
        hass = request.app["hass"]
        
        # Generate dynamic OpenAPI spec
        spec = await self._generate_openapi_spec(hass)
        
        return web.Response(
            text=json.dumps(spec, indent=2),
            content_type="application/json"
        )

    async def _generate_openapi_spec(self, hass: HomeAssistant) -> dict[str, Any]:
        """Generate OpenAPI specification from Home Assistant instance."""
        base_url = f"http://localhost:{hass.config.api.port}"
        
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
                }
            },
            "servers": [
                {
                    "url": base_url,
                    "description": "Home Assistant instance"
                }
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
                    }
                },
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
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
                {"name": "Calendar", "description": "Calendar events and management"}
            ]
        }


def async_register(hass: HomeAssistant) -> None:
    """Register HTTP views."""
    hass.http.register_view(SwaggerUIView())
    hass.http.register_view(SwaggerSpecView())
