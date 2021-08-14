import homeassistant.helpers.config_validation as cv
import voluptuous as vol
import requests
import threading
from math import floor
from homeassistant.const import CONF_MAC
from homeassistant.components.light import (
  LightEntity,
  SUPPORT_BRIGHTNESS,
  SUPPORT_COLOR,
  ATTR_BRIGHTNESS,
  ATTR_RGB_COLOR,
  COLOR_MODE_RGB,
  PLATFORM_SCHEMA
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
  vol.Required("name"): cv.string,
  vol.Required("host"): cv.string
})

SUPPORT_FEATURES_RGB = SUPPORT_BRIGHTNESS | SUPPORT_COLOR
SUPPORT_FEATURES_WHITE = SUPPORT_BRIGHTNESS

def setup_platform(hass, config, add_entities, discovery_info=None):
  add_entities([ ESPLedStripLight(name=config["name"], host=config["host"]) ])

class ESPLedStripLight(LightEntity):
  def __init__(self, **kwargs):
    self._name = kwargs["name"]
    self._host = kwargs["host"]
    self._on = False
    self._brightness = 255
    self._rgb = (255, 255, 255)

  @property
  def color_mode(self):
    return COLOR_MODE_RGB

  @property
  def supported_color_modes(self):
    return set([ COLOR_MODE_RGB ])

  @property
  def supported_features(self):
    return SUPPORT_BRIGHTNESS | SUPPORT_COLOR

  @property
  def unique_id(self):
    return self._host

  @property
  def name(self):
    return self._name

  @property
  def is_on(self):
    return self._on

  @property
  def brightness(self):
    return self._brightness

  @property
  def rgb_color(self):
    return self._rgb

  def turn_on(self, **kwargs):
    self._on = True

    brightness = kwargs.get(ATTR_BRIGHTNESS)
    if brightness != None:
      self._brightness = brightness

    rgb = kwargs.get(ATTR_RGB_COLOR)
    if rgb != None:
      self._rgb = rgb

    self.update_espled()

  def turn_off(self, **kwargs):
    self._on = False
    self.update_espled()

  def update_espled(self):
    r = int( int(self._on) * self._rgb[0] * ( self._brightness / 255 ) )
    g = int( int(self._on) * self._rgb[1] * ( self._brightness / 255 ) )
    b = int( int(self._on) * self._rgb[2] * ( self._brightness / 255 ) )

    def req():
      success = False
      while not success:
        try:
          requests.post("http://" + self._host, f"{r:02x}{g:02x}{b:02x}")
          success = True
        except:
          continue

    threading.Thread(target=req).start()

