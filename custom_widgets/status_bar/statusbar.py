import time
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.atlas import Atlas
from kivy.animation import Animation
from kivy.properties import BoundedNumericProperty, ObjectProperty, StringProperty, ListProperty
from kivy.graphics import Line, Rectangle, Ellipse, Color
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label


class StatusBarImage(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch):
            pass


class StatusBar(GridLayout):
    battery = ObjectProperty()
    battery_image = ObjectProperty()
    wifi_status = ObjectProperty()
    _state = ObjectProperty()
    speed = ObjectProperty()
    battery_percentage = BoundedNumericProperty(100, min=0, max=100, errorvalue=0)

    def __init__(self, **kwargs):
        super(StatusBar, self).__init__(**kwargs)
        self._IMAGE_PATH = "custom_widgets//status_bar//images//"
        self._background_image = self._IMAGE_PATH + "background_image.png"
        self._state_image = self._IMAGE_PATH + "state_idle.png"
        self._wifi_image = self._IMAGE_PATH + "wifi_not_connected.png"

    def on_pos(self, instance, value):
        instance.pos = self.pos
        if self.battery_image is None:
            return
        #self.battery_image.source = "atlas://custom_widgets/bunny_widget/images/bunny_widget/bunny_widget_active_red"
        self.battery_image.source = self._IMAGE_PATH + "battery_20.png"

    def on_size(self, instance, value):
        instance.size = self.size

    def call_me(self):
        print("called!!")
        return True


if __name__ == "__main__":
    pass