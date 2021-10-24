import random

from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, StringProperty, BoundedNumericProperty, \
    ReferenceListProperty, ListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.uix.button import ButtonBehavior
from core.constants import Constants as Cons


<<<<<<< HEAD
class BunnyWidget(Widget):

    IMAGE_PATH = "atlas://custom_widgets/bunny_widget/images/bunny_widget"
    background_image_source = StringProperty(IMAGE_PATH + "/bunny_widget_active_blue")
    battery_percentage_label = ObjectProperty()
    pos_x = BoundedNumericProperty(0.0, min=0.0, max=1.0, errorvalue=0.0)
    pos_y = BoundedNumericProperty(1.0, min=0.0, max=1.0, errorvalue=0.0)
    position = ReferenceListProperty(pos_x, pos_y)
=======
class BunnyWidget(Image, ButtonBehavior):
    _bunny_state = ObjectProperty()
>>>>>>> 3c30194ebb305e1f1726d83b4765765ba059fc66

    def __init__(self, _id, **kwargs):
        super(BunnyWidget, self).__init__(**kwargs)
<<<<<<< HEAD
        self.id = kwargs.get("id")
        Clock.schedule_interval(self.move, 2)

    def change_state(self, state):
        self._background_image_source = self.IMAGE_PATH + "/bunny_widget_blue"



=======
        self._IMAGE_PATH = "custom_widgets\\bunny_widget\\images\\"
        Clock.schedule_once(self._initialize_bunny, 2)
        self._uid = _id
        self._normalized_pos = [0, 0]

    def _initialize_bunny(self, *args):

        self.size_hint = (0.1, 0.1)

    def on__bunny_state(self, instance, value):
        self.source = self._IMAGE_PATH + f"bunny_widget_state_{value}.png"

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

    @property
    def normalized_pos(self):
        return self._normalized_pos
>>>>>>> 3c30194ebb305e1f1726d83b4765765ba059fc66
