import random

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, StringProperty, BoundedNumericProperty, \
    ReferenceListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock


class BunnyWidget(Widget):

    IMAGE_PATH = "atlas://custom_widgets/bunny_widget/images/bunny_widget"
    background_image_source = StringProperty(IMAGE_PATH + "/bunny_widget_active_blue")
    battery_percentage_label = ObjectProperty()
    pos_x = BoundedNumericProperty(0.0, min=0.0, max=1.0, errorvalue=0.0)
    pos_y = BoundedNumericProperty(1.0, min=0.0, max=1.0, errorvalue=0.0)
    position = ReferenceListProperty(pos_x, pos_y)

    def __init__(self, *args, **kwargs, ):
        super(BunnyWidget, self).__init__(**kwargs)
        self.id = kwargs.get("id")
        Clock.schedule_interval(self.move, 2)

    def change_state(self, state):
        self._background_image_source = self.IMAGE_PATH + "/bunny_widget_blue"



