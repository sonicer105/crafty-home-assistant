"""The Crafty Controller integration."""
import logging

LOGGER = logging.getLogger(__name__)
DOMAIN = "crafty_controller"


def setup(hass, config):
    """Setup for Crafty Controller component."""
    LOGGER.info("Setting up Crafty Controller")
    return True
