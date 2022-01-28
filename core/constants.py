from kivy.properties import ObjectProperty, StringProperty, BoundedNumericProperty, \
    ReferenceListProperty, ListProperty, NumericProperty, BooleanProperty, DictProperty


__all__ = ["Constants"]


class Constants:
    GUI_REFRESH_RATE = 1.0/60.0
    RADIO_BIT_RATE = 2  # in MBPS
    LOG_PATH = "..//logs//"
    BUNNY_BATTERY_MIN = 0.1
    BUNNY_MAX_SPEED = 0.10  # m/s
    RADIO_CONN_TIMEOUT = 10  # s
    BUNNY_STATES = ("formation", "roam", "charge", "idle")
    SAFETY_MARGIN = 0.10 # m
    BUNNY_DIAMETER = 0.30 # m
    CANVAS_SCALE = ListProperty([100, "1", "m"]) # 100 pixels represents 1 m

