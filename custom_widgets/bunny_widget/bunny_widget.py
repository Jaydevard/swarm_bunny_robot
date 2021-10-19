import random

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, StringProperty, BoundedNumericProperty, \
    ReferenceListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.uix.button import ButtonBehavior
from core.constants import Constants as Cons


class BunnyWidget(Image, ButtonBehavior):
    _bunny_state = ObjectProperty()

    def __init__(self, **kw):
        super(BunnyWidget, self).__init__(**kw)
        self._IMAGE_PATH = "atlas://custom_widgets/bunny_widget/images/bunny_widget/"
        Clock.schedule_once(self._initialize_bunny, 2)

    def _initialize_bunny(self):
        self.source = self._IMAGE_PATH + "active"

    def on__bunny_state(self):
        print("state changed!!")

    def __setitem__(self, key, value):
        if key == "x":
            self.pos[0] = value
        elif key == "y":
            self.pos[1] = value
        elif key == "state":
            if value not in Cons.BUNNY_STATES:
                print(f"incorrect state {value}")
                raise ValueError
            else:
                self._bunny_state = value
        elif key == "size":
            self.size = value


