#!/bin/bash
# Swagger UI Integration Generator Script
# This script automatically generates the Swagger UI integration files
# before launching Home Assistant

set -e  # Exit on any error

echo "🚀 Generating Swagger UI Integration..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed."
    exit 1
fi

# Run the Python script to generate Swagger UI integration
python3 generate_swagger_integration.py

echo "✅ Swagger UI Integration Generated Successfully!"
echo "🌐 Swagger UI will be available at:"
echo "   - http://localhost:8123/api/swagger"
echo "   - http://localhost:8123/api/swagger/spec"
