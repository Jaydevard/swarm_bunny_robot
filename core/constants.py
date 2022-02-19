from kivy.properties import ObjectProperty, StringProperty, BoundedNumericProperty, \
    ReferenceListProperty, ListProperty, NumericProperty, BooleanProperty, DictProperty
from kivy.uix.widget import Widget

__all__ = ["Constants"]


class Constants(Widget):
    """
    Global Variables 
    that can be changed by the user

    """
    GUI_REFRESH_RATE = NumericProperty(1.0/60.0)
    RADIO_DATA_RATE = NumericProperty(2)  # in MBPS
    LOG_PATH = StringProperty("..//logs//")
    BUNNY_BATTERY_MIN = NumericProperty(0.1)
    BUNNY_MAX_SPEED = NumericProperty(0.10)  # m/s
    RADIO_CONN_TIMEOUT = NumericProperty(10)  # ms
    BUNNY_STATES = ("formation", "roam", "charge", "idle")
    SAFETY_MARGIN = NumericProperty(0.10) # m
    BUNNY_DIAMETER = 0.30 # m
    CANVAS_SCALE = ListProperty(["1", "m"]) # 100 pixels represents 1 m

    ACK_STATE = {
        """
        IF STATE BIT IS 8-BIT THEN
        
        """
        # XX00 0000 (STATE BITS 0:1)
        "LEFT_TWO":{ "idle": 0,
                     "running": 1,
                     "charging": 2,
                     "error": 3,
                    },
        # STATE BITS 2:4 ARE FOR BATTERY LEVEL

        # 0000 0XXX (STATE BITS 5:7)
        "RIGHT_THREE":{
                        "no_error": 0,
                        "battery_low": 1,
                        "localization_filter_unstable": 2,
                        "motor_driver_communication_failed": 3,
                        "compass_communication_failed": 4,
                        "uwb_communication_failed": 5
                     }
    }

    URI = 'radio://0/30/2M/E7E7E7E711'
    CHANNEL = 40
    ADDR_PREFIX = "LGN"


