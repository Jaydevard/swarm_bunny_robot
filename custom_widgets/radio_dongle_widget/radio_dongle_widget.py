
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.properties import BoundedNumericProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.uix.button import ButtonBehavior
from functools import partial
from utils import InformationPopup


class RadioDongleWidget(BoxLayout, Widget, ButtonBehavior):
    _wifi_image = ObjectProperty()
    _spinner = ObjectProperty()
    _search_button = ObjectProperty()
    _connect_button = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self._IMAGE_PATH = "custom_widgets\\radio_dongle_widget\\images\\"
        self._SPINNER_INITIAL_TEXT = "[b][i]Select radio dongle[/i][/b]"
        Clock.schedule_once(self.initialize_widgets, 1)
        self._active_radio_dongle = None

    def on_pos(self, instance, pos):
        self.pos = pos

    def on_size(self, instance, size):
        self.size = size

    def initialize_widgets(self, *args):
        self._wifi_image.source = self._IMAGE_PATH + "wifi_not_connected.png"
        self._spinner.text = self._SPINNER_INITIAL_TEXT
        self._connect_button.bind(on_release=self.connect_to_radio)
        self._search_button.bind(on_release=self.search_for_radio_dongles)
        self._spinner.bind(text=self.update_on_spinner_selection)

    def update_on_spinner_selection(self, *args):
        if self._spinner.text == self._SPINNER_INITIAL_TEXT or self._active_radio_dongle is None:
            return
        elif self._active_radio_dongle != self._spinner.text:
            self._connect_button.text = "[b][i]Connect[i][/b]"
            self._wifi_image.source = self._IMAGE_PATH + "wifi_not_connected.png"
        elif self._active_radio_dongle == self._spinner.text:
            self._connect_button.text = "[b][i]Disconnect[i][/b]"
            self._wifi_image.source = self._IMAGE_PATH + "wifi_connected.png"

    def search_for_radio_dongles(self, *args):
        self._wifi_image.source = self._IMAGE_PATH + "searching_wheel.gif"
        self._search_button.text = "[b][i]Searching[/i][/b]"
        self._search_button.disabled = True
        # call communication class here as a Clock schedule
        Clock.schedule_once(partial(self.update_radio_dongles, ['radio_1', 'radio_2']), 3)

    def update_radio_dongles(self, radios: list, *largs):
        """
        Callback for radio dongles
        ==========
        This must be called by the communication class
        :param radios: list of radios available
        :param largs: handle extra arguments
        :return: None
        """
        self._spinner.values = radios
        self._search_button.disabled = False
        self._search_button.text = "[b][i]Search[/i][/b]"
        self._wifi_image.source = self._IMAGE_PATH + "wifi_not_connected.png"

    def connect_to_radio(self, *args):
        if self._spinner.text == self._SPINNER_INITIAL_TEXT:
            InformationPopup(_type='e', _message="Select a radio dongle").open()

        else:
            self._spinner.disabled = True
            self._connect_button.text = "[b][i]Connecting[i][/b]"
            self._wifi_image.source = self._wifi_image.source = self._IMAGE_PATH + "wifi_connecting.gif"
        # call communication function to start connection as a Clock schedule
            Clock.schedule_once(partial(self.finalize_radio_connection, True), 3)

    def finalize_radio_connection(self, connection_established: bool, *args):
        """
        Callback for radio connection
        ==========
        callback function when radio connection has been established or not
        :param connection_established: True if connected, False if not connected
        :param args: handle callback arguments from kivy clock
        :return: None
        """
        if connection_established:
            self._spinner.disabled = False
            self._active_radio_dongle = self._spinner.text
            self._connect_button.text = "[b][i]Disconnect[i][/b]"
            self._wifi_image.source = self._IMAGE_PATH + "wifi_connected.png"
        else:
            InformationPopup(_type='e', _message="Connection to radio could not be established!!").open()
            self._active_radio_dongle = None







