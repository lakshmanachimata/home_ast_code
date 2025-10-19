#!/usr/bin/env python3
"""
Generate Swagger/OpenAPI specification for Home Assistant API
"""

import json
from datetime import datetime
from typing import Any, Dict, List

def generate_openapi_spec() -> Dict[str, Any]:
    """Generate OpenAPI 3.0 specification for Home Assistant API."""
    
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
            {
                "url": "http://localhost:8123",
                "description": "Local Home Assistant instance"
            },
            {
                "url": "https://your-home-assistant-instance.duckdns.org",
                "description": "Remote Home Assistant instance"
            }
        ],
        "security": [
            {
                "bearerAuth": []
            },
            {
                "basicAuth": []
            }
        ],
        "paths": {
            "/api/": {
                "get": {
                    "summary": "API Status",
                    "description": "Check if the API is running",
                    "tags": ["System"],
                    "responses": {
                        "200": {
                            "description": "API is running",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "message": {
                                                "type": "string",
                                                "example": "API running."
                                            }
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
                    "description": "Get current Home Assistant configuration",
                    "tags": ["Configuration"],
                    "responses": {
                        "200": {
                            "description": "Configuration retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "location_name": {"type": "string"},
                                            "latitude": {"type": "number"},
                                            "longitude": {"type": "number"},
                                            "elevation": {"type": "number"},
                                            "unit_system": {"type": "string"},
                                            "time_zone": {"type": "string"},
                                            "components": {"type": "array", "items": {"type": "string"}},
                                            "config_dir": {"type": "string"},
                                            "whitelist_external_dirs": {"type": "array", "items": {"type": "string"}},
                                            "allowlist_external_dirs": {"type": "array", "items": {"type": "string"}},
                                            "allowlist_external_urls": {"type": "array", "items": {"type": "string"}},
                                            "version": {"type": "string"},
                                            "config_source": {"type": "string"},
                                            "recovery_mode": {"type": "boolean"},
                                            "state": {"type": "string"},
                                            "external_url": {"type": "string"},
                                            "internal_url": {"type": "string"},
                                            "currency": {"type": "string"},
                                            "country": {"type": "string"},
                                            "language": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/core/state": {
                "get": {
                    "summary": "Get Core State",
                    "description": "Get the current core state of Home Assistant",
                    "tags": ["System"],
                    "responses": {
                        "200": {
                            "description": "Core state retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "state": {
                                                "type": "string",
                                                "enum": ["STARTING", "RUNNING", "STOPPING", "STOPPED"],
                                                "description": "Current state of Home Assistant core"
                                            },
                                            "recorder_state": {
                                                "type": "object",
                                                "properties": {
                                                    "migration_in_progress": {"type": "boolean"},
                                                    "migration_is_live": {"type": "boolean"}
                                                }
                                            }
                                        }
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
                                        "items": {
                                            "$ref": "#/components/schemas/State"
                                        }
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
                            "description": "Entity ID (e.g., light.living_room)"
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
                                        "state": {
                                            "type": "string",
                                            "description": "New state value"
                                        },
                                        "attributes": {
                                            "type": "object",
                                            "description": "Entity attributes"
                                        },
                                        "force_update": {
                                            "type": "boolean",
                                            "default": False,
                                            "description": "Force update even if state hasn't changed"
                                        }
                                    }
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
                    "summary": "Remove Entity",
                    "description": "Remove an entity from Home Assistant",
                    "tags": ["States"],
                    "parameters": [
                        {
                            "name": "entity_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "Entity ID to remove"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Entity removed successfully"
                        },
                        "404": {
                            "description": "Entity not found"
                        }
                    }
                }
            },
            "/api/services": {
                "get": {
                    "summary": "Get All Services",
                    "description": "Get all available services",
                    "tags": ["Services"],
                    "responses": {
                        "200": {
                            "description": "Services retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "additionalProperties": {
                                            "type": "object",
                                            "properties": {
                                                "description": {"type": "string"},
                                                "fields": {
                                                    "type": "object",
                                                    "additionalProperties": {
                                                        "type": "object",
                                                        "properties": {
                                                            "description": {"type": "string"},
                                                            "example": {"type": "string"}
                                                        }
                                                    }
                                                }
                                            }
                                        }
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
                    "description": "Call a specific service",
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
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "entity_id": {
                                            "type": "string",
                                            "description": "Entity ID to target"
                                        },
                                        "area_id": {
                                            "type": "string",
                                            "description": "Area ID to target"
                                        },
                                        "device_id": {
                                            "type": "string",
                                            "description": "Device ID to target"
                                        }
                                    }
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
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/State"},
                                        "description": "List of changed states"
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid service call"
                        }
                    }
                }
            },
            "/api/events": {
                "get": {
                    "summary": "Get Event Listeners",
                    "description": "Get all event listeners",
                    "tags": ["Events"],
                    "responses": {
                        "200": {
                            "description": "Event listeners retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "additionalProperties": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
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
                    "description": "Fire a custom event",
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
                                    "description": "Event data"
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
                                            "message": {
                                                "type": "string",
                                                "example": "Event custom_event fired."
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/stream": {
                "get": {
                    "summary": "Event Stream",
                    "description": "Stream events via Server-Sent Events",
                    "tags": ["Events"],
                    "parameters": [
                        {
                            "name": "restrict",
                            "in": "query",
                            "schema": {"type": "string"},
                            "description": "Comma-separated list of event types to restrict to"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Event stream",
                            "content": {
                                "text/event-stream": {
                                    "schema": {
                                        "type": "string",
                                        "description": "Server-Sent Events stream"
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
                    "description": "Get all loaded components",
                    "tags": ["System"],
                    "responses": {
                        "200": {
                            "description": "Components retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"type": "string"}
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
                    "description": "Render a Jinja2 template",
                    "tags": ["Templates"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["template"],
                                    "properties": {
                                        "template": {
                                            "type": "string",
                                            "description": "Jinja2 template to render"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Template rendered successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "result": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Template error"
                        }
                    }
                }
            },
            "/api/websocket": {
                "get": {
                    "summary": "WebSocket Connection",
                    "description": "Establish WebSocket connection for real-time communication",
                    "tags": ["WebSocket"],
                    "responses": {
                        "101": {
                            "description": "Switching Protocols - WebSocket connection established"
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
                        "entity_id": {
                            "type": "string",
                            "description": "Entity ID",
                            "example": "light.living_room"
                        },
                        "state": {
                            "type": "string",
                            "description": "Current state",
                            "example": "on"
                        },
                        "attributes": {
                            "type": "object",
                            "description": "Entity attributes",
                            "additionalProperties": True
                        },
                        "last_changed": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Last time the state changed"
                        },
                        "last_updated": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Last time the state was updated"
                        },
                        "context": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "parent_id": {"type": "string"},
                                "user_id": {"type": "string"}
                            }
                        }
                    },
                    "required": ["entity_id", "state", "attributes", "last_changed", "last_updated", "context"]
                }
            },
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "Long-lived access token"
                },
                "basicAuth": {
                    "type": "http",
                    "scheme": "basic",
                    "description": "Basic authentication with username/password"
                }
            }
        },
        "tags": [
            {
                "name": "System",
                "description": "System information and status"
            },
            {
                "name": "Configuration",
                "description": "Configuration management"
            },
            {
                "name": "States",
                "description": "Entity state management"
            },
            {
                "name": "Services",
                "description": "Service calls"
            },
            {
                "name": "Events",
                "description": "Event handling"
            },
            {
                "name": "Templates",
                "description": "Template rendering"
            },
            {
                "name": "WebSocket",
                "description": "WebSocket real-time communication"
            }
        ]
    }

def main():
    """Generate and save the OpenAPI specification."""
    spec = generate_openapi_spec()
    
    # Save as JSON
    with open("homeassistant-api-swagger.json", "w") as f:
        json.dump(spec, f, indent=2)
    
    # Save as YAML (requires PyYAML)
    try:
        import yaml
        with open("homeassistant-api-swagger.yaml", "w") as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
        yaml_generated = True
    except ImportError:
        yaml_generated = False
    
    if yaml_generated:
        print("✅ Generated both JSON and YAML formats")
    else:
        print("✅ Generated JSON format (install PyYAML for YAML format)")
    
    print(f"📄 OpenAPI specification generated:")
    print(f"   - homeassistant-api-swagger.json")
    print(f"   - homeassistant-api-swagger.yaml (if PyYAML available)")
    print(f"\n🌐 You can view this in Swagger UI at:")
    print(f"   https://editor.swagger.io/")
    print(f"   (Copy and paste the JSON content)")

if __name__ == "__main__":
    main()
