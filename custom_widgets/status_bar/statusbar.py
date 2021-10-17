import time

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


class StatusBar(GridLayout):
    battery = ObjectProperty()
    _background_color = ListProperty([0.6, 0.5, 0.8, 1])
    battery_label = ObjectProperty()
    battery_image = ObjectProperty()
    battery_percentage = BoundedNumericProperty(100, min=0, max=100, errorvalue=0)

    def __init__(self, **kwargs):
        super(StatusBar, self).__init__(**kwargs)

    def on_pos(self, instance, value):
        instance.pos = self.pos
        self.battery_label.font_size = f"{int(max(self.battery_label.size) * 0.8)}sp"
        if self.battery_image is None:
            return
        self.battery_image.source = "atlas://custom_widgets/bunny_widget/images/bunny_widget/bunny_widget_active_red"
        # "custom_widgets\\status_bar\\images\\battery_full.png"

    def on_size(self, instance, value):
        instance.size = self.size


if __name__ == "__main__":
    pass