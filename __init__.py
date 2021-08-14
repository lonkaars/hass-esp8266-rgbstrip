from homeassistant.core import HomeAssistant

DOMAIN = "espled"
PLATFORMS = ["light"]

def setup(hass: HomeAssistant, config):
  hass.data[DOMAIN] = {}
  return True

def setup_entry(hass, entry):
  return True
