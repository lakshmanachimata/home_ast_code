"""The Swagger UI integration."""
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
