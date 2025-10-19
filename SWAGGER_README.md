# Swagger UI Integration for Home Assistant

This project provides automatic generation of Swagger UI integration files for Home Assistant, ensuring your API documentation is always up-to-date.

## 🚀 Quick Start

### Option 1: Using the Python Script
```bash
python3 generate_swagger_integration.py
```

### Option 2: Using the Shell Script
```bash
./generate_swagger.sh
```

### Option 3: Using Make
```bash
make swagger
```

### Option 4: Using VS Code Tasks
1. Open Command Palette (`Cmd+Shift+P` or `Ctrl+Shift+P`)
2. Type "Tasks: Run Task"
3. Select "Generate Swagger UI Integration"

## 📋 Available Commands

### Python Script
- **`python3 generate_swagger_integration.py`** - Generate all Swagger UI files

### Shell Script
- **`./generate_swagger.sh`** - Generate Swagger UI files (executable)

### Make Commands
- **`make swagger`** - Generate Swagger UI integration files
- **`make install`** - Install all requirements
- **`make test`** - Run tests
- **`make run`** - Run Home Assistant with Swagger UI
- **`make clean`** - Clean up generated files
- **`make dev`** - Generate Swagger UI and run Home Assistant
- **`make help`** - Show all available commands

### VS Code Tasks
- **"Generate Swagger UI Integration"** - Generate Swagger UI files
- **"Run Home Assistant Core (with Swagger)"** - Run HA with auto-generated Swagger UI

## 🔧 Integration with Build Process

### Pre-Launch Hook
Add this to your VS Code `launch.json`:
```json
{
    "name": "Home Assistant (with Swagger)",
    "type": "python",
    "request": "launch",
    "module": "homeassistant",
    "args": ["-c", "config"],
    "preLaunchTask": "Generate Swagger UI Integration"
}
```

### Pre-Build Hook
Add this to your build process:
```bash
# Before building Home Assistant
python3 generate_swagger_integration.py
```

## 📁 Generated Files

The script generates the following files:

- **`homeassistant/components/swagger_ui/__init__.py`** - Integration entry point
- **`homeassistant/components/swagger_ui/manifest.json`** - Integration metadata
- **`homeassistant/components/swagger_ui/http.py`** - HTTP views and OpenAPI spec
- **`config/configuration.yaml`** - Updated to include swagger_ui

## 🌐 Accessing Swagger UI

Once Home Assistant is running, Swagger UI will be available at:

- **Swagger UI Interface**: http://localhost:8123/api/swagger
- **OpenAPI Specification**: http://localhost:8123/api/swagger/spec

## 📚 API Endpoints Covered

The generated Swagger UI includes documentation for all Home Assistant REST API endpoints:

### System & Configuration
- `GET /api/` - API status check
- `GET /api/config` - Get current configuration
- `GET /api/components` - Get loaded components
- `GET /api/error_log` - Get error log
- `POST /api/config/core/check_config` - Check configuration

### States Management
- `GET /api/states` - Get all entity states
- `GET /api/states/{entity_id}` - Get specific entity state
- `POST /api/states/{entity_id}` - Update entity state
- `DELETE /api/states/{entity_id}` - Delete entity

### Services & Events
- `GET /api/services` - Get all services
- `POST /api/services/{domain}/{service}` - Call service
- `GET /api/events` - Get event listeners
- `POST /api/events/{event_type}` - Fire event

### History & Logbook
- `GET /api/history/period/{timestamp}` - Get historical data
- `GET /api/logbook/{timestamp}` - Get logbook entries

### Additional Features
- `POST /api/template` - Render templates
- `POST /api/intent/handle` - Handle intents
- `GET /api/camera_proxy/{camera_entity_id}` - Camera proxy
- `GET /api/calendars` - Get calendars
- `GET /api/calendars/{calendar_entity_id}` - Get calendar events

## 🔐 Authentication

The Swagger UI supports both authentication methods:

- **Bearer Token**: Long-lived access tokens
- **Basic Auth**: Username/password authentication

## 🛠️ Customization

To customize the Swagger UI:

1. Edit `generate_swagger_integration.py`
2. Modify the `_generate_openapi_spec` method
3. Add or remove API endpoints as needed
4. Regenerate the integration files

## 📝 Notes

- The script automatically detects if `swagger_ui` is already configured in `configuration.yaml`
- All generated files are overwritten each time the script runs
- The script ensures all required directories exist
- Logging is provided for debugging and monitoring

## 🐛 Troubleshooting

### Common Issues

1. **Permission Denied**: Make sure the shell script is executable
   ```bash
   chmod +x generate_swagger.sh
   ```

2. **Python Not Found**: Ensure Python 3 is installed and in PATH
   ```bash
   python3 --version
   ```

3. **Configuration Not Updated**: Check if `config/configuration.yaml` exists and is writable

4. **Swagger UI Not Loading**: Ensure Home Assistant is running and the integration is loaded

### Debug Mode

Run the script with debug logging:
```bash
python3 -c "import logging; logging.basicConfig(level=logging.DEBUG); exec(open('generate_swagger_integration.py').read())"
```

## 🤝 Contributing

To add new API endpoints:

1. Edit the `_generate_openapi_spec` method in `generate_swagger_integration.py`
2. Add the new endpoint to the `paths` dictionary
3. Include appropriate tags, parameters, and response schemas
4. Test the generated Swagger UI

## 📄 License

This project follows the same license as Home Assistant (Apache 2.0).
