"""Swagger UI integration for Home Assistant API documentation."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .http import async_register

_LOGGER = logging.getLogger(__name__)

DOMAIN = "swagger_ui"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Swagger UI integration."""
    _LOGGER.info("Setting up Swagger UI integration")
    
    # Register HTTP views
    async_register(hass)
    
    return True
