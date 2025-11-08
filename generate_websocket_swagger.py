#!/usr/bin/env python3
"""
Generate Swagger/OpenAPI documentation for Home Assistant WebSocket API commands.

This script analyzes the WebSocket API command handlers and generates
comprehensive Swagger documentation with request/response payloads.
"""

import ast
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_websocket_commands(file_path: Path) -> Dict[str, Any]:
    """Parse WebSocket command handlers from commands.py."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract decorator patterns
    command_pattern = r'@decorators\.websocket_command\s*\(\s*({.*?})\s*\)'
    function_pattern = r'async\s+def\s+(\w+)\(.*?:"|def\s+(\w+)\(.*?:'
    
    commands = []
    
    # Find all websocket_command decorators
    for match in re.finditer(command_pattern, content, re.DOTALL):
        decorator_content = match.group(1)
        # Extract the required type field
        type_match = re.search(r'"type":\s*"([^"]+)"', decorator_content)
        if type_match:
            command_type = type_match.group(1)
            
            # Try to find the associated function
            func_match = re.search(r'async\s+def\s+(\w+)\s*\(', content[match.end():])
            if func_match:
                func_name = func_match.group(1)
                commands.append({
                    'type': command_type,
                    'function': func_name
                })
    
    return commands

def generate_websocket_schemas() -> Dict[str, Any]:
    """Generate comprehensive WebSocket command schemas."""
    
    return {
        "components": {
            "schemas": {
                # Existing schemas
                "WebSocketAuthMessage": {
                    "type": "object",
                    "required": ["type", "access_token"],
                    "properties": {
                        "type": {"type": "string", "enum": ["auth"], "example": "auth"},
                        "access_token": {"type": "string", "description": "Long-lived access token"}
                    },
                    "example": {"type": "auth", "access_token": "YOUR_LONG_LIVED_ACCESS_TOKEN"}
                },
                
                # Get States Command
                "WebSocketGetStates": {
                    "type": "object",
                    "required": ["id", "type"],
                    "properties": {
                        "id": {"type": "integer", "example": 1, "description": "Message ID"},
                        "type": {"type": "string", "enum": ["get_states"], "example": "get_states"}
                    },
                    "example": {"id": 1, "type": "get_states"}
                },
                
                # Get States Response
                "WebSocketGetStatesResponse": {
                    "type": "object",
                    "required": ["id", "type", "success", "result"],
                    "properties": {
                        "id": {"type": "integer"},
                        "type": {"type": "string", "enum": ["result"]},
                        "success": {"type": "boolean", "example": True},
                        "result": {
                            "type": "array",
                            "items": {
                                "$ref": "#/components/schemas/State"
                            }
                        }
                    }
                },
                
                # Subscribe Entities Command
                "WebSocketSubscribeEntities": {
                    "type": "object",
                    "required": ["id", "type"],
                    "properties": {
                        "id": {"type": "integer", "example": 2, "description": "Message ID"},
                        "type": {"type": "string", "enum": ["subscribe_entities"], "example": "subscribe_entities"},
                        "entity_ids": {"type": "array", "items": {"type": "string"}, "description": "Optional: specific entity IDs to subscribe to"},
                        "include": {"type": "array", "items": {"type": "string"}, "description": "Include filter"},
                        "exclude": {"type": "array", "items": {"type": "string"}, "description": "Exclude filter"}
                    },
                    "example": {"id": 2, "type": "subscribe_entities"}
                },
                
                # Call Service Command
                "WebSocketCallService": {
                    "type": "object",
                    "required": ["id", "type", "domain", "service"],
                    "properties": {
                        "id": {"type": "integer", "example": 3},
                        "type": {"type": "string", "enum": ["call_service"], "example": "call_service"},
                        "domain": {"type": "string", "example": "climate"},
                        "service": {"type": "string", "example": "set_temperature"},
                        "service_data": {"type": "object", "description": "Service call parameters"},
                        "target": {
                            "type": "object",
                            "properties": {
                                "entity_id": {"type": "string", "example": "climate.yh_thermostat"},
                                "area_id": {"type": "string"},
                                "device_id": {"type": "string"}
                            }
                        },
                        "return_response": {"type": "boolean", "description": "Return service response"}
                    },
                    "example": {
                        "id": 3,
                        "type": "call_service",
                        "domain": "climate",
                        "service": "set_temperature",
                        "service_data": {"temperature": 25}
                    }
                },
                
                # Entity Registry List
                "WebSocketEntityRegistryList": {
                    "type": "object",
                    "required": ["id", "type"],
                    "properties": {
                        "id": {"type": "integer", "example": 4},
                        "type": {"type": "string", "enum": ["config/entity_registry/list"], "example": "config/entity_registry/list"}
                    },
                    "example": {"id": 4, "type": "config/entity_registry/list"}
                },
                
                # Device Registry List
                "WebSocketDeviceRegistryList": {
                    "type": "object",
                    "required": ["id", "type"],
                    "properties": {
                        "id": {"type": "integer", "example": 5},
                        "type": {"type": "string", "enum": ["config/device_registry/list"], "example": "config/device_registry/list"}
                    },
                    "example": {"id": 5, "type": "config/device_registry/list"}
                },
                
                # Config Entries Get
                "WebSocketConfigEntriesGet": {
                    "type": "object",
                    "required": ["id", "type"],
                    "properties": {
                        "id": {"type": "integer", "example": 6},
                        "type": {"type": "string", "enum": ["config_entries/get"], "example": "config_entries/get"},
                        "type_filter": {"type": "array", "items": {"type": "string"}, "description": "Filter by integration type"},
                        "domain": {"type": "string", "description": "Filter by domain"}
                    },
                    "example": {"id": 6, "type": "config_entries/get"}
                },
                
                # Subscribe Events
                "WebSocketSubscribeEvents": {
                    "type": "object",
                    "required": ["id", "type"],
                    "properties": {
                        "id": {"type": "integer", "example": 7},
                        "type": {"type": "string", "enum": ["subscribe_events"], "example": "subscribe_events"},
                        "event_type": {"type": "string", "description": "Optional: specific event type", "example": "state_changed"}
                    },
                    "example": {"id": 7, "type": "subscribe_events"}
                },
                
                # Get Config
                "WebSocketGetConfig": {
                    "type": "object",
                    "required": ["id", "type"],
                    "properties": {
                        "id": {"type": "integer", "example": 8},
                        "type": {"type": "string", "enum": ["get_config"], "example": "get_config"}
                    },
                    "example": {"id": 8, "type": "get_config"}
                },
                
                # Get Services
                "WebSocketGetServices": {
                    "type": "object",
                    "required": ["id", "type"],
                    "properties": {
                        "id": {"type": "integer", "example": 9},
                        "type": {"type": "string", "enum": ["get_services"], "example": "get_services"}
                    },
                    "example": {"id": 9, "type": "get_services"}
                },
                
                # Integration Descriptions
                "WebSocketIntegrationDescriptions": {
                    "type": "object",
                    "required": ["id", "type"],
                    "properties": {
                        "id": {"type": "integer", "example": 10},
                        "type": {"type": "string", "enum": ["integration/descriptions"], "example": "integration/descriptions"}
                    },
                    "example": {"id": 10, "type": "integration/descriptions"}
                },
                
                # Error Response
                "WebSocketError": {
                    "type": "object",
                    "required": ["id", "type", "success"],
                    "properties": {
                        "id": {"type": "integer"},
                        "type": {"type": "string", "enum": ["result"], "example": "result"},
                        "success": {"type": "boolean", "example": False},
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
                    },
                    "example": {
                        "id": 1,
                        "type": "result",
                        "success": False,
                        "error": {
                            "code": "invalid_format",
                            "message": "Message incorrectly formatted"
                        }
                    }
                },
                
                # Generic Result
                "WebSocketResult": {
                    "type": "object",
                    "required": ["id", "type", "success"],
                    "properties": {
                        "id": {"type": "integer"},
                        "type": {"type": "string", "enum": ["result"]},
                        "success": {"type": "boolean"},
                        "result": {"type": "object", "description": "Command-specific result data"}
                    }
                }
            }
        }
    }

def main():
    """Generate WebSocket Swagger documentation."""
    logger.info("Generating WebSocket API Swagger documentation...")
    
    schemas = generate_websocket_schemas()
    
    # Write to a JSON file
    output_file = Path("websocket_swagger_schemas.json")
    with open(output_file, 'w') as f:
        json.dump(schemas, f, indent=2)
    
    logger.info(f"Generated: {output_file}")
    
    # Print summary
    logger.info(f"Generated {len(schemas['components']['schemas'])} WebSocket schemas")
    logger.info("\nSchemas generated:")
    for schema_name in schemas['components']['schemas'].keys():
        logger.info(f"  - {schema_name}")

if __name__ == "__main__":
    main()

