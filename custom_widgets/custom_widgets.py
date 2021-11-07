from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.widget import Widget
from functools import partial
from utils import InformationPopup
from pathlib import Path
from kivy.uix.behaviors import DragBehavior
from kivy.animation import Animation
from kivy.properties import ObjectProperty, StringProperty, BoundedNumericProperty, \
    ReferenceListProperty, ListProperty, NumericProperty, BooleanProperty
from kivy.uix.actionbar import ActionBar, ActionItem
from core.constants import Constants as Cons
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.lang import Builder
import random
import os

Builder.load_file(str(Path(os.getcwd()) / "custom_widgets" / "custom_widgets.kv"))


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
        self._IMAGE_PATH = Path("custom_widgets/images/status_bar_widget")
        self._background_image = str(self._IMAGE_PATH / "background_image.png")
        Clock.schedule_once(self.initialize_images, 2)

    def initialize_images(self, *args):
        self._state_image.source = str(self._IMAGE_PATH / "state_formation.png")
        self._wifi_image.source = str(self._IMAGE_PATH / "wifi_not_connected.png")
        self._battery_image.source = str(self._IMAGE_PATH / "battery_40.png")
        self._speed_image.source = str(self._IMAGE_PATH / "speed.png")

    def on_pos(self, instance, value):
        instance.pos = self.pos
        if self._battery_image is None:
            return

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
            self._battery_image.source = str(self._IMAGE_PATH / "battery_10.png")
        elif 10 < value <= 20:
            self._battery_image.source = str(self._IMAGE_PATH / "battery_20.png")
        elif 20 < value <= 40:
            self._battery_image.source = str(self._IMAGE_PATH / "battery_40.png")
        elif 40 < value <= 60:
            self._battery_image.source = str(self._IMAGE_PATH / "battery_60.png")
        elif 60 < value <= 80:
            self._battery_image.source = str(self._IMAGE_PATH / "battery_80.png")
        elif 80 < value <= 100:
            self._battery_image.source = str(self._IMAGE_PATH / "battery_full.png")
        self._battery_label.text = f"[b]  {value}%[/b]"

    def update_state(self, state):
        if state not in ("formation", "idle", "charge", "roam"):
            print(f"state {state} is unknown, states are ('formation', 'idle', 'charge', 'roam')")
            raise TypeError
        else:
            self._state_image.source = str(self._IMAGE_PATH / f"state_{state}.png")


class BunnyWidget(Image, ButtonBehavior):
    _bunny_state = ObjectProperty()
    _angle = NumericProperty(0)

    def __init__(self, uid, **kwargs):
        super(BunnyWidget, self).__init__(**kwargs)
        self._IMAGE_PATH = "atlas://custom_widgets/images/bunny_widget/bunny_widget"
        Clock.schedule_once(self._initialize_bunny, 1)
        self._id = uid

    def _initialize_bunny(self, *args):
        self.size_hint = (0.1, 0.1)

    # state callback
    def on__bunny_state(self, instance, value):
        self.source = self._IMAGE_PATH + f"/bunny_widget_{value}"

    # rotation_angle_callback
    def on__angle(self, instance, value):
        if value == 360:
            instance.angle = 0

    def __setitem__(self, key, value):
        if key == "state":
            if value not in Cons.BUNNY_STATES:
                print(f"incorrect state {value}")
                raise ValueError
            else:
                self._bunny_state = value
        elif key == "size_hint":
            self.size_hint = value
        elif key == "theta":
            anim = Animation(_angle=360, duration=2)
            anim.start(self)

    @property
    def id(self):
        return self._id


class TransmitterWidget(DragBehavior, Image):

    def __init__(self, **kwargs):
        super(TransmitterWidget, self).__init__(**kwargs)
        self.source = str(Path("custom_widgets/images/transmitter_widget/transmitter.png"))


class RadioDongleWidget(BoxLayout, Widget, ButtonBehavior):
    _wifi_image = ObjectProperty()
    _spinner = ObjectProperty()
    _search_button = ObjectProperty()
    _connect_button = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self._IMAGE_PATH = Path("custom_widgets/images/radio_dongle_widget")
        self._SPINNER_INITIAL_TEXT = "[b][i]Select radio dongle[/i][/b]"
        Clock.schedule_once(self.initialize_widgets, 1)
        self._active_radio_dongle = None

    def on_pos(self, instance, pos):
        self.pos = pos

    def on_size(self, instance, size):
        self.size = size

    def initialize_widgets(self, *args):
        self._wifi_image.source = str(self._IMAGE_PATH / "wifi_not_connected.png")
        self._spinner.text = self._SPINNER_INITIAL_TEXT
        self._connect_button.bind(on_release=self.connect_to_radio)
        self._search_button.bind(on_release=self.search_for_radio_dongles)
        self._spinner.bind(text=self.update_on_spinner_selection)

    def update_on_spinner_selection(self, *args):
        if self._spinner.text == self._SPINNER_INITIAL_TEXT or self._active_radio_dongle is None:
            return
        elif self._active_radio_dongle != self._spinner.text:
            self._connect_button.text = "[b][i]Connect[i][/b]"
            self._wifi_image.source = str(self._IMAGE_PATH / "wifi_not_connected.png")
        elif self._active_radio_dongle == self._spinner.text:
            self._connect_button.text = "[b][i]Disconnect[i][/b]"
            self._wifi_image.source = str(self._IMAGE_PATH / "wifi_connected.png")

    def search_for_radio_dongles(self, *args):
        self._wifi_image.source = str(self._IMAGE_PATH / "searching_wheel.gif")
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
        self._wifi_image.source = str(self._IMAGE_PATH / "wifi_not_connected.png")

    def connect_to_radio(self, *args):
        if self._spinner.text == self._SPINNER_INITIAL_TEXT:
            InformationPopup(_type='e', _message="Select a radio dongle").open()

        else:
            self._spinner.disabled = True
            self._connect_button.text = "[b][i]Connecting[i][/b]"
            self._wifi_image.source = self._wifi_image.source = str(self._IMAGE_PATH / "wifi_connecting.gif")
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
            self._wifi_image.source = str(self._IMAGE_PATH / "wifi_connected.png")
        else:
            InformationPopup(_type='e', _message="Connection to radio could not be established!!").open()
            self._active_radio_dongle = None


class BunnyActionBar(ActionBar):

    # need to be completed
    connected_checkbox = ObjectProperty()
    charge_checkbox = ObjectProperty()
    roam_checkbox = ObjectProperty()
    formation_checkbox = ObjectProperty()
    idle_checkbox = ObjectProperty()

    def __init__(self, uid=None, **kwargs):
        super().__init__(**kwargs)
        self._id = uid

    def on_pos(self, item, value):
        self.pos = value

    @property
    def id(self):
        return self._id

    
class DragAndResizeRect(DragBehavior, Widget):
    _border_coord = ListProperty([0 ,0, 0, 0])
    _border_width = NumericProperty(2)
    _draw_border = BooleanProperty(True)
    _fill_color = ListProperty([1, 0, 1, 1])
    _border_color = ListProperty([0, 0, 1, 1])
    _edit_mode = StringProperty("")
    
    def __init__(self, **kwargs):
        super(DragAndResizeRect, self).__init__(**kwargs)

    def on_pos(self, item, pos):
        self.pos = pos
        if self._draw_border:
            self._border_coord = [self._border_width+self.x, 
                                  self.y + self._border_width,  
                                  self.width - 2 * self._border_width, 
                                  self.height - 2 * self._border_width]
        else:
            self._border_coord = [0, 0, 0, 0]

    def on_size(self, item, size):
            self.size = size
            if self._draw_border:
                self._border_coord = [self._border_width+self.x, 
                                      self.y + self._border_width,  
                                      self.width - 2 * self._border_width, 
                                      self.height - 2 * self._border_width]
            else:
                self._border_coord = [0, 0, 0, 0]

    def on_touch_down(self, touch):
        self.pos_hint = {}
        
        if not self.collide_point(*touch.pos):
            return super(DragAndResizeRect, self).on_touch_up(touch)
            
        diff = self._border_width * 2
        xx, yy  = self.to_widget(*touch.pos, relative=True)
        
        if touch.button == "left":
            self._edit_mode = "pos"
            
            if self.height - yy < diff:
                self._edit_mode = 'top'
                if self.width - xx < diff:
                    self._edit_mode = 'ne'
                    Window.set_system_cursor('crosshair')
                elif xx < diff:
                    self._edit_mode = 'nw'
                    Window.set_system_cursor('crosshair')
                else:
                    Window.set_system_cursor('size_ns')

            elif yy < diff:
                self._edit_mode = 'bottom'
                if self.width - xx < diff:
                    self._edit_mode = 'se'         
                    Window.set_system_cursor('crosshair') 
                elif xx < diff:
                    self._edit_mode = 'sw'
                    Window.set_system_cursor('crosshair') 
                else:
                    Window.set_system_cursor('size_ns')

            elif self.width - xx < diff:
                self._edit_mode = 'right'
                Window.set_system_cursor('size_we')
            
            elif xx < diff:
                self._edit_mode = 'left'
                Window.set_system_cursor('size_we')
            else:
                Window.set_system_cursor('crosshair')
            touch.ud['edit_mode'] = self._edit_mode
            if self._edit_mode != 'pos':
                touch.ud['size_node'] = self
                return True

        return super(DragAndResizeRect, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if 'size_node' in touch.ud.keys():
            xx, yy = self.to_widget(*touch.pos, relative=True)
            if touch.ud["edit_mode"] == 'top':
                if yy > 0:
                    if self.size_hint_y is None:
                        self.height = min(yy, self.parent.height)
                    else:
                        self.size_hint_y = yy / self.parent.height
                        if self.size_hint_y >= 1:
                            self.size_hint_y = 1
            
            elif touch.ud["edit_mode"] == "bottom":
                if self.height - yy > 0:
                    if self.size_hint_y is None:
                        self.height -= yy
                        self.y += yy
                    else:
                        self.size_hint_y = (self.height - yy) / self.parent.height
                        self.y += yy
            
            elif touch.ud["edit_mode"] == 'left':
                if self.width - xx > 0:
                    if self.size_hint is None:
                        self.width -= xx
                        self.x += xx
                    else:
                        self.size_hint_x = min(1, (self.width - xx) / self.parent.width)
                        self.x += xx
            
            elif touch.ud["edit_mode"] == 'right':
                if xx > 0:
                    if self.size_hint_x is None:
                        self.width = xx
                    else:
                        self.size_hint_x = xx / self.parent.width
                        self.width = xx

            elif touch.ud["edit_mode"] == 'nw':
                if yy > 0:
                    if self.size_hint_y is None:
                        self.height = min(yy, self.parent.height)
                    else:
                        self.size_hint_y = yy / self.parent.height
                        if self.size_hint_y >= 1:
                            self.size_hint_y = 1
                if self.width - xx > 0:
                    if self.size_hint is None:
                        self.width -= xx
                        self.x += xx
                    else:
                        self.size_hint_x = min(1, (self.width - xx) / self.parent.width)
                        self.x += xx
            elif touch.ud["edit_mode"] == 'ne':
                if yy > 0:
                    if self.size_hint_y is None:
                        self.height = min(yy, self.parent.height)
                    else:
                        self.size_hint_y = yy / self.parent.height
                        if self.size_hint_y >= 1:
                            self.size_hint_y = 1
                if xx > 0:
                    if self.size_hint_x is None:
                        self.width = xx
                    else:
                        self.size_hint_x = xx / self.parent.width
                        self.width = xx
            
            elif touch.ud["edit_mode"] == 'se':
                if self.height - yy > 0:
                    if self.size_hint_y is None:
                        self.height -= yy
                        self.y += yy
                    else:
                        self.size_hint_y = (self.height - yy) / self.parent.height
                        self.y += yy
                if xx > 0:
                    if self.size_hint_x is None:
                        self.width = xx
                    else:
                        self.size_hint_x = xx / self.parent.width
                        self.width = xx
            
            elif touch.ud["edit_mode"] == 'sw':
                if self.width - xx > 0:
                    if self.size_hint is None:
                        self.width -= xx
                        self.x += xx
                    else:
                        self.size_hint_x = min(1, (self.width - xx) / self.parent.width)
                        self.x += xx
                if self.height - yy > 0:
                    if self.size_hint_y is None:
                        self.height -= yy
                        self.y += yy
                    else:
                        self.size_hint_y = (self.height - yy) / self.parent.height
                        self.y += yy
                
            return super(DragAndResizeRect, self).on_touch_move(touch)
        return super(DragAndResizeRect, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        Window.set_system_cursor('arrow')
        self.pos_hint = {"x": (self.x - self.parent.x) / self.parent.width,
                         "y": (self.y - self.parent.y) / self.parent.height}
        return super(DragAndResizeRect, self).on_touch_up(touch)


