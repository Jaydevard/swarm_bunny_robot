import random
import time
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.atlas import Atlas
from kivy.animation import Animation
from kivy.properties import BoundedNumericProperty, ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from functools import partial


class StatusBarWidgetImage(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(StatusBarWidgetImage, self).__init__(**kwargs)


class StatusBarWidget(GridLayout):
    _battery_image = ObjectProperty()
    _battery_label = ObjectProperty()
    _wifi_image = ObjectProperty()
    _state_image = ObjectProperty()
    _speed_image = ObjectProperty()
    _speed_label = ObjectProperty()
    _battery_percentage = BoundedNumericProperty(100, min=0, max=100, errorvalue=0)

    def __init__(self, **kwargs):
        super(StatusBarWidget, self).__init__(**kwargs)
        self._IMAGE_PATH = "custom_widgets//status_bar_widget//images//"
        self._background_image = self._IMAGE_PATH + "background_image.png"
        Clock.schedule_once(self.initialize_images, 2)

    def initialize_images(self, *args):
        self._state_image.source = self._IMAGE_PATH + "state_formation.png"
        self._wifi_image.source = self._IMAGE_PATH + "wifi_not_connected.png"
        self._battery_image.source = self._IMAGE_PATH + "battery_40.png"
        self._speed_image.source = self._IMAGE_PATH + "speed.png"

    def on_pos(self, instance, value):
        instance.pos = self.pos
        if self._battery_image is None:
            return
        #self.battery_image.source = "atlas://custom_widgets/bunny_widget/images/bunny_widget/bunny_widget_active_red"

    def on_size(self, instance, value):
        instance.size = self.size

    def on_image_press(self, *args):
        """
        callback when image is clicked!
        :param args: the name of the object that has been clicked
        :return: None
        """
        image_pressed = args[0]
        if image_pressed == "battery_image":
            pass
        elif image_pressed == "wifi_image":
            pass

    def update_battery_level(self, value, *args):
        if 0 <= value <= 10:
            self._battery_image.source = self._IMAGE_PATH + "battery_10.png"
        elif 10 < value <= 20:
            self._battery_image.source = self._IMAGE_PATH + "battery_20.png"
        elif 20 < value <= 40:
            self._battery_image.source = self._IMAGE_PATH + "battery_40.png"
        elif 40 < value <= 60:
            self._battery_image.source = self._IMAGE_PATH + "battery_60.png"
        elif 60 < value <= 80:
            self._battery_image.source= self._IMAGE_PATH + "battery_80.png"
        elif 80 < value <= 100:
            self._battery_image.source = self._IMAGE_PATH + "battery_full.png"
        self._battery_label.text = f"[b]  {value}%[/b]"

    def update_state(self, state):
        if state not in ("formation", "idle", "charge", "roam"):
            print(f"state {state} is unknown, states are ('formation', 'idle', 'charge', 'roam')")
            raise TypeError
        else:
            self._state_image.source = self._IMAGE_PATH + f"state_{state}.png"


if __name__ == "__main__":
    pass