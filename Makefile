# Home Assistant Development Makefile
# This Makefile provides convenient commands for Home Assistant development

.PHONY: help swagger install test run clean

# Default target
help:
	@echo "Home Assistant Development Commands:"
	@echo ""
	@echo "  make swagger     - Generate Swagger UI integration files"
	@echo "  make install     - Install all requirements"
	@echo "  make test        - Run tests"
	@echo "  make run         - Run Home Assistant with Swagger UI"
	@echo "  make clean       - Clean up generated files"
	@echo "  make help        - Show this help message"

# Generate Swagger UI integration files
swagger:
	@echo "🚀 Generating Swagger UI Integration..."
	@python3 generate_swagger_integration.py
	@echo "✅ Swagger UI Integration Generated!"

# Install all requirements
install:
	@echo "📦 Installing all requirements..."
	@uv pip install -r requirements_all.txt
	@echo "✅ Requirements installed!"

# Run tests
test:
	@echo "🧪 Running tests..."
	@python3 -m pytest --timeout=10 tests
	@echo "✅ Tests completed!"

# Run Home Assistant with Swagger UI
run: swagger
	@echo "🏠 Starting Home Assistant with Swagger UI..."
	@echo "🌐 Swagger UI will be available at:"
	@echo "   - http://localhost:8123/api/swagger"
	@echo "   - http://localhost:8123/api/swagger/spec"
	@python3 -m homeassistant --debug -c config

# Clean up generated files
clean:
	@echo "🧹 Cleaning up generated files..."
	@rm -rf homeassistant/components/swagger_ui/
	@echo "✅ Cleanup completed!"

# Generate Swagger UI and run Home Assistant
dev: swagger run
