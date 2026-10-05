# ==================================================================================
from enum import Enum


# ==================================================================================
class eCommandType(Enum):  
  UNKNOWN = -1
  INJECT_KEYCODE = 0
  INJECT_TEXT = 1
  INJECT_TOUCH_EVENT = 2
  INJECT_SCROLL_EVENT = 3
  BACK_OR_SCREEN_ON = 4
  EXPAND_NOTIFICATION_PANEL = 5
  EXPAND_SETTINGS_PANEL = 6
  COLLAPSE_PANELS = 7
  GET_CLIPBOARD = 8
  SET_CLIPBOARD = 9
  SET_SCREEN_POWER_MODE = 10
  ROTATE_DEVICE = 11