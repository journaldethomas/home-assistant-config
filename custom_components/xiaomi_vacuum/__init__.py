"""The Xiaomi Vacuum component."""
DOMAIN = 'xiaomi_vacuum'

async def async_setup(hass, config):

     return True

async def async_setup_entry(hass, config_entry):
    """Set up entry."""
    hass.data[DOMAIN] = {}

    return True
