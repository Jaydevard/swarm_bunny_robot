from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.properties import BoundedNumericProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.uix.button import ButtonBehavior


class RadioDongleWidget(BoxLayout, Widget, ButtonBehavior):
    _wifi_image = ObjectProperty()
    _spinner = ObjectProperty()
    _search_button = ObjectProperty()
    _connect_button = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self._IMAGE_PATH = "custom_widgets\\radio_dongle_widget\\images\\"
        Clock.schedule_once(self.initialize_images, 1)

    def on_pos(self, instance, pos):
        self.pos = pos

    def on_size(self, instance, size):
        self.size = size

    def initialize_images(self, *args):
        pass

    def add_radio_options(self, options):
        if isinstance(options, list):
            self._spinner.values.append(*options)




