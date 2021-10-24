from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, StringProperty, BoundedNumericProperty, \
    ReferenceListProperty, ListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.uix.button import ButtonBehavior
from core.constants import Constants as Cons
from pathlib import Path

class BunnyWidget(Image, ButtonBehavior):
    _bunny_state = ObjectProperty()
    _rotation_angle = BoundedNumericProperty(0, min=0, max=360, errorvalue=0)

    def __init__(self, _id, **kwargs):
        super(BunnyWidget, self).__init__(**kwargs)
        self._IMAGE_PATH = "atlas://custom_widgets/bunny_widget/images/bunny_widget"
        Clock.schedule_once(self._initialize_bunny, 2)
        self._uid = _id
        self._normalized_pos = [0, 0]

    def _initialize_bunny(self, *args):
        self.size_hint = (0.1, 0.1)

    def on__bunny_state(self, instance, value):
        self.source =  self._IMAGE_PATH + f"/bunny_widget_{value}"
    
    def on__rotation_angle():
        print("None!!")

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
        elif key == "size_hint":
            self.size_hint = value
        elif key == "normalized_pos":
            self._normalized_pos = value
        elif key == "rotation_angle":
            self._rotation_angle = value

    
    @property
    def normalized_pos(self):
        return self._normalized_pos

    @property
    def rotation_angle(self):
        return self._rotation_angle
