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
  SUPPORT_TRANSITION,
  ATTR_BRIGHTNESS,
  ATTR_RGB_COLOR,
  ATTR_TRANSITION,
  COLOR_MODE_RGB,
  PLATFORM_SCHEMA
)
from time import sleep

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
    return SUPPORT_BRIGHTNESS | SUPPORT_COLOR | SUPPORT_TRANSITION

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
    on_old = self._on
    brightness_old = self._brightness
    rgb_old = self._rgb

    self._on = True

    brightness = kwargs.get(ATTR_BRIGHTNESS)
    if brightness != None: self._brightness = brightness

    rgb = kwargs.get(ATTR_RGB_COLOR)
    if rgb != None: self._rgb = rgb

    transition = kwargs.get(ATTR_TRANSITION)
    if transition != None:
        self.interpolate(brightness_old if on_old else 0, brightness, rgb_old if on_old else (0, 0, 0,), rgb, transition)

    self.update_espled()

  def turn_off(self, **kwargs):
    self._on = False
    self.update_espled()

  def interpolate(self, brightness_old, brightness, rgb_old, rgb, transition):
    step_duration = 0.250
    steps = int(transition / step_duration)
    if rgb_old == None: rgb_old = (0, 0, 0,)
    if rgb == None: rgb = (0, 0, 0,)
    if brightness_old == None: brightness_old = 0
    if brightness == None: brightness = 0
    for x in range(steps):
        weight = x / steps
        r = rgb_old[0] * (1 - weight) + rgb[0] * weight
        g = rgb_old[1] * (1 - weight) + rgb[1] * weight
        b = rgb_old[2] * (1 - weight) + rgb[2] * weight
        self._rgb = (r, g, b,)
        self._brightness = brightness_old * (1 - weight) + brightness * weight
        self.update_espled()
        sleep(step_duration)

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

