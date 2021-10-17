import random
import time
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.atlas import Atlas
from kivy.animation import Animation
from kivy.properties import BoundedNumericProperty, ObjectProperty, StringProperty, ListProperty
from kivy.graphics import Line, Rectangle, Ellipse, Color
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock


class StatusBarImage(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(StatusBarImage, self).__init__(**kwargs)


class StatusBar(GridLayout):
    _battery_image = ObjectProperty()
    _battery_label = ObjectProperty()
    _wifi = ObjectProperty()
    _state = ObjectProperty()
    _speed_image = ObjectProperty()
    _speed_label = ObjectProperty()
    _battery_percentage = BoundedNumericProperty(100, min=0, max=100, errorvalue=0)

    def __init__(self, **kwargs):
        super(StatusBar, self).__init__(**kwargs)
        self._IMAGE_PATH = "custom_widgets//status_bar//images//"
        self._background_image = self._IMAGE_PATH + "background_image.png"
        Clock.schedule_once(self.initialize_images, 2)

    def initialize_images(self, *args):
        self._state.source = self._IMAGE_PATH + "state_idle.png"
        self._wifi.source = self._IMAGE_PATH + "wifi_not_connected.png"
        self._battery_image.source = self._IMAGE_PATH + "battery_20.png"
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
        if image_pressed == "battery":
            pass
        elif image_pressed == "wifi":
            pass

    def update_battery_level(self, value):
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
        pass


if __name__ == "__main__":
    pass