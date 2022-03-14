from kivy.uix.treeview import TreeView, TreeViewNode, TreeViewLabel
from kivy.core.text import markup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from functools import partial
from communication.radio import Radio
from utils import InformationPopup 
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from pathlib import Path
from kivy.uix.behaviors import DragBehavior, button
from kivy.animation import Animation
from kivy.properties import ObjectProperty, StringProperty, BoundedNumericProperty, \
    ReferenceListProperty, ListProperty, NumericProperty, BooleanProperty, DictProperty
from kivy.uix.actionbar import ActionBar, ActionItem
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, InstructionGroup, Line, Point, Rectangle, PopMatrix, PushMatrix, Rotate, Scale, Translate, Ellipse
from kivy.core.window import Window
from kivy.lang import Builder
import random
from math import pi, cos, sin
import math
import numpy as np
import os
from core.exceptions import *
from kivy.graphics.transformation import Matrix



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
        Clock.schedule_once(self.initialize_images, 0.5)

    def initialize_images(self, *args):
        self._state_image.source = str(self._IMAGE_PATH / "state_formation.png")
        self._wifi_image.source = str(self._IMAGE_PATH / "wifi_not_connected.png")
        self._battery_image.source = str(self._IMAGE_PATH / "battery_80.png")
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
    _state = ObjectProperty()
    v = []
    angle = NumericProperty(0)
    battery_level = BoundedNumericProperty(0, min=0, max=100)

    def __init__(self, uid, **kwargs):
        super(BunnyWidget, self).__init__(**kwargs)
        self._IMAGE_PATH = "atlas://custom_widgets/images/bunny_widget/bunny_widget"
        self._id = uid
        self.addr = uid
        self.Cons = None
        self._radio = None
        self.scale = 5000   # 5m grid
        self.canvas_manager = None
        self.size_hint = (0.2/5, 0.2/5)

    def on_size(self, instance, value):
        self.size_hint = (0.2/5, 0.2/5)

    def update_property(self, property, value):
        setattr(self, property, value)


    def update_scale(self, value):
        self.size_hint = (self.Cons.BUNNY_DIAMETER/ float(value), self.Cons.BUNNY_DIAMETER / float(value))
        self.pos_hint = self.pos_hint
    
    # battery_level callback
    def on_battery_level(self, instance, value):
        print(f"battery level is {value}")

    # state callback
    def on__state(self, instance, value):
        self.source = self._IMAGE_PATH + f"/bunny_widget_{value}"

    # rotation_angle_callback
    def on_angle(self, instance, value):
        if value == 360:
            instance.angle = 0

    def __setitem__(self, key, value):
        if key == "state":
            if value not in self.Cons.BUNNY_STATES:
                print(f"incorrect state {value}")
                raise ValueError
            else:
                self._state = value
        elif key == "angle":
            anim = Animation(angle=value, duration=2)
            anim.start(self)
    
    # bunny_x - bunny_y = diff in pos(reference is center of each)
    def __sub__(self, other):
        if type(other) == type(self):
            return (self.center[0] - other.center[0], self.center[1] - other.center[1])

    # send command to move
    
    def move(self, vel: list or tuple, 
             time_step, 
             mode="sim",
             apply_scale=False, 
             callback=None, *args):
        """
        Moves the bunny widget on the canvas based on 
        the velocity, mode and dt:
        Call this function using Kivy.clock.schedule_(once|interval)
        if mode == "sim": updates the pos_hint
        elif mode == "real": sends the velocity cmd and updates its position
        """
        
        # hard coding the scale to be 5 m
        if self._radio is None and mode == "real":
            raise Exception("radio not provided!!")

        # send command 5 times
        count = 15
        num_errors = 0
        state = None
        battery_level = None
        actual_position = None

        print(vel)
        if mode == "real":
            for i in range(count): 
                state, battery_level, actual_position = self._radio.send_vel_cmd(addr=self.addr, velocity=vel)
                if state is None or battery_level is None or actual_position is None:
                    num_errors += 1
                else:
                    break

            # if num_errors == count:
            #     raise NoAckError

            if actual_position is not None:
                ## Assuming that the zero position is represented by the (0,0) position of the robot
                #self.pos_hint = {"center_x":actual_position[0] / self.scale, "center_y":actual_position[1] / self.scale}
                pass

            if battery_level is not None:
                self.battery_level = (100 / 16) *battery_level

            if state is not None:
                # state bit  0:3 :
                #             init_state = 0x0,
                #             magcalibration_state = 0x1,
                #             idle_state = 0x2,
                #             run_state = 0x3,
                #             gotocharge_state = 0x4,
                #             charging_state = 0x5,
                #             sleep_state = 0x6,
                #
                #             error_state = 0xE,
                #             debug_state = 0xF

                # state bit  4:7 : battery level in 16 levels
                state = state >> 4
                if state in (0x0, 0x1):
                    raise BunnyNotReadyError(state)

                elif state in (0x4, 0x5):
                    self._state = "charge"
                
                elif state in (0x6, 0x2):
                    self._state = "idle"
                
                else:
                    self._state = "formation"

        elif mode == "sim":
            diff_x = vel[0] * time_step
            diff_y = vel[1] * time_step
            self.pos_hint = {}
            if apply_scale:
                self.pos =  (self.x + diff_x / self.scale, self.y + diff_y / self.scale)
            else:
                self.pos =  (self.x + diff_x , self.y + diff_y)
            
            self.pos_hint = {"x": (self.x - self.parent.x) / self.parent.width,
                             "y": (self.y - self.parent.y) / self.parent.height}

        if callback:
            print("sending callback!!")
            callback(self.id)


    def stop(self, after: float or int =0):
        try:
            if after == 0:
                self._radio:Radio.send_vel_cmd(self.addr, [0,0,0])
            else:
                Clock.schedule_once(partial(self._radio.send_vel_cmd, self.addr, (0,0,0)), after)
        except Exception as e:
            raise e


    @property
    def id(self):
        return self._id

    @property
    def state(self):
        return self._state

    @property
    def radio(self):
        return self._radio


class RadioDongleWidget(BoxLayout, Widget, ButtonBehavior):
    _wifi_image = ObjectProperty()
    _spinner = ObjectProperty()
    _search_button = ObjectProperty()
    _connect_button = ObjectProperty()

    _radio_state = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._IMAGE_PATH = Path("custom_widgets/images/radio_dongle_widget")
        self._SPINNER_INITIAL_TEXT = "[b][i]Select radio dongle[/i][/b]"
        Clock.schedule_once(self._initialize_widgets, 1)
        self._connections_cls = None
        self._radio_handle = None
        self._selected_radio = None

    def on__radio_state(self, instance, value):
        """
        Use this function to notify other widgets down 
        the line when radio connection status changes
        """
        pass

    def on_pos(self, instance, pos):
        self.pos = pos

    def on_size(self, instance, size):
        self.size = size

    def update_property(self, property, value):
        setattr(self, property, value)


    def _initialize_widgets(self, *args):
        self._wifi_image.source = str(self._IMAGE_PATH / "wifi_not_connected.png")
        self._spinner.text = self._SPINNER_INITIAL_TEXT
        self._spinner.bind(text=self.update_on_spinner_selection)


    def set_state_to_connected(self, radio, radio_available: list):
        self._wifi_image.source = str(self._IMAGE_PATH / "wifi_connected.png")
        self._connect_button.text = "[b][i]Disonnect[i][/b]"
        self._connect_button.disabled = False
        self._spinner.values = radio_available
        self._spinner.text = radio_available[0]
        self._selected_radio = radio_available[0]
        self._radio_handle = radio

    def set_state_to_disconnected(self):
        self._wifi_image.source = str(self._IMAGE_PATH / "wifi_not_connected.png")
        InformationPopup("w", "Disconnected from Radio").open()
        self._connect_button.text = "[b][i]Connect[i][/b]"
        self._radio_handle.close() 
        self._radio_handle = None
        self._selected_radio = None

    def set_state_to_searching(self):
        self._wifi_image.source = str(self._IMAGE_PATH / "searching_wheel.gif")
        self._search_button.text = "[b][i]Searching[/i][/b]"
        self._search_button.disabled = True
        print("searching!!!")

    def update_on_spinner_selection(self, *args):
        if self._spinner.text == self._SPINNER_INITIAL_TEXT or self._selected_radio is None:
            self._connect_button.text = "[b][i]Connect[i][/b]"
            self._connect_button.disabled = True
        
        elif self._selected_radio != self._spinner.text:
            self._connect_button.text = "[b][i]Connect[i][/b]"
        
        elif self._selected_radio == self._spinner.text:
            self._connect_button.text = "[b][i]Disconnect[i][/b]"
            self._wifi_image.source = str(self._IMAGE_PATH / "wifi_connected.png")

    

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
    _border_width = NumericProperty(4)
    _draw_border = BooleanProperty(True)
    fill_color = ListProperty([1, 0, 1, 1])
    border_color = ListProperty([0, 0, 1, 1])
    _edit_mode = StringProperty("")
    
    def __init__(self, **kwargs):
        super(DragAndResizeRect, self).__init__(**kwargs)
        self.constrain_to_parent_window = True
        self.shape_settings = None
        self.mode = "Fill"
        self.lock_size = False
        self.lock_pos = False
        self._touch = None
        Window.bind(on_motion=self.on_window_motion)
        self._fixed = False
        self.canvas_manager = None

    def __del__(self):
        Window.unbind(on_motion=self.on_window_motion)
    
    def on_window_motion(self, *args):
        for arg in args:
            if type(arg).__name__ == "MouseMotionEvent":
                self._touch = arg

    def update_property(self, property, value):
        setattr(self, property, value)
    
    def set_fill_color(self, instance, value):
        if self.mode == "Border":
            print(self.mode)
            self.fill_color = [0, 0, 0, 0]
        else:
            self.fill_color = value

    def set_border_color(self, instance, value):
        self.border_color = value

    def set_lock_size(self, instance, value):
        if value:
            self.size_hint_x = self.size[0] / self.parent.width
            self.size_hint_y = self.size[1] / self.parent.height
        
        self.lock_size = value        

    def set_lock_pos(self, instance, value):
        if value:
            pos_hint_x = (self.x - self.parent.x) / self.parent.width
            pos_hint_y = (self.y - self.parent.y) / self.parent.height
            print(pos_hint_x, pos_hint_y)
            self.pos_hint = {"x": pos_hint_x, "y": pos_hint_y}
            self.drag_timeout = 0
        else:
            self.drag_timeout = 1000000
            self.pos_hint = {}
            self.pos = (self.x, self.y)
        self.lock_pos = value        

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

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if self._touch is None:
            return
        elif ("delete" or "backspace" in keycode) and self._fixed:
            diff = self._border_width * 2
            xx, yy = self.to_widget(*self._touch.pos, relative=True)
            if ((  0 < xx < diff or 
                   abs(self.width - xx) < diff or 
                    0 < yy < diff or 
                   abs(self.height - yy) < diff) and 
                self.mode == "Border") or (  (0 < xx < self.width and 0 < yy < self.height) and
                self.mode == "Fill"):
                self.canvas_manager.remove_widget(self)
        return True

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super(DragAndResizeRect, self).on_touch_up(touch)
        if self._fixed:
            return super(DragAndResizeRect, self).on_touch_up(touch)

        self.pos_hint = {}
        self.pos = (self.x, self.y)
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
            if self._edit_mode == "pos" and self.mode == "Border":
                self.drag_timeout = 0
                Window.set_system_cursor('arrow')
                return super().on_touch_up(touch)
            
        return super(DragAndResizeRect, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._fixed:
            return super(DragAndResizeRect, self).on_touch_move(touch)
        if 'size_node' in touch.ud.keys():
            xx, yy = self.to_widget(*touch.pos, relative=True)
            if "edit_mode" not in touch.ud.keys():
                return super(DragAndResizeRect, self).on_touch_move(touch)
            if self.lock_size:
                return super(DragAndResizeRect, self).on_touch_move(touch)

            self.pos_hint = {}
            self.pos = (self.x, self.y)
            self.size_hint = (None, None)
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
                if touch.x > self.parent.x:
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
        if self._fixed:
            return super(DragAndResizeRect, self).on_touch_up(touch)
        if self.lock_pos:
            self.drag_timeout = 0
        else:
            self.drag_timeout = 1000000
        Window.set_system_cursor('arrow')
        self.pos_hint = {"x": (self.x - self.parent.x) / self.parent.width,
                         "y": (self.y - self.parent.y) / self.parent.height}
        self.size_hint = (self.width/self.parent.width, self.height/self.parent.height)
        return super(DragAndResizeRect, self).on_touch_up(touch)


class DragAndResizePolygon(DragBehavior, Widget):
    fill_color = ListProperty([0, 1, 1, 1])
    border_color = ListProperty([1, 1, 1, 1])
    line_points = ListProperty([])
    segments = NumericProperty(100)
    border_width = NumericProperty(3)
    _touch_region = StringProperty("")

    def __init__(self, **kwargs):
        super(DragAndResizePolygon, self).__init__(**kwargs)
        self.constrain_to_parent_window = True
        self.segments = kwargs.get("segments", 100)
        self.size_hint = (None, None)
        self.mode = "Fill"
        Window.bind(on_motion=self.on_window_motion)
        self._touch = None
        self.lock_size = False
        self.lock_pos = False
        self._fixed = False
        self.canvas_manager = None
        Clock.schedule_once(partial(self.on_pos, self, self.pos), 0.1)
    

    def __del__(self):
        Window.unbind(on_motion=self.on_window_motion)
    
    def on_window_motion(self, *args):
        for arg in args:
            if type(arg).__name__ == "MouseMotionEvent":
                self._touch = arg

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if self._touch is None:
            return True
        elif ("delete" or "backspace" in keycode) and self._fixed:
            is_within_shape, is_within_border = self.check_relative_touch_pos(self._touch, in_border=True)
            if (is_within_border and self.mode == "Border") or (is_within_shape and self.mode == "Fill"):
                self.canvas_manager.remove_widget(self)
        return True
    
    def set_lock_pos(self, instance, value):
        if value:
            pos_hint_x = (self.x - self.parent.x) / self.parent.width
            pos_hint_y = (self.y - self.parent.y) / self.parent.height
            print(pos_hint_x, pos_hint_y)
            self.pos_hint = {"x": pos_hint_x, "y": pos_hint_y}
            self.drag_timeout = 0
        else:
            self.drag_timeout = 1000000
            self.pos_hint = {}
            self.pos = (self.x, self.y) 
        
        self.lock_pos = value        

    def set_lock_size(self, instance, value):
        if value:
            self.size_hint_x = self.size[0] / self.parent.width
            self.size_hint_y = self.size[1] / self.parent.height
        
        self.lock_size = value   

    def set_segments(self, instance, value):
        if value != '' and value != '0':
            if int(float(value)) <= 3:
                return
            self.segments = int(float(value))
            self.draw_border()

    def set_fill_color(self, instance, value):
        if self.mode != "Border":
            self.fill_color = value

    def set_border_color(self, instance, value):
        self.border_color = value


    def update_property(self, property, value):
        setattr(self, property, value)

    def on_pos(self, instance, value, *args):
        self.pos = value
        self.draw_border()

    def on_size(self, instance, value):
        self.size = value
        self.draw_border()


    def draw_border(self):
        points = []
        angle_step = (pi * 2) / float(self.segments)
        segments = int(self.segments)
        for i in range(segments) :
            x = self.x + (1 + cos((angle_step * i) + pi/2)) * (self.width/2)
            y = self.y + (1 + sin((angle_step * i) + pi/2)) * (self.height/2)
            points.extend([x, y])
        points.extend([points[0], points[1]])
        self.line_points = points

    def draw_ellipse(self, width, height):
        self.width = width
        self.height = height
        self.draw_border()
        self.drag_rectangle = [self.x+(self.width/4), 
                               self.y+(self.height/4), 
                               0.5*self.width, 
                               0.5*self.height]

    def check_relative_touch_pos(self, touch, in_border=False):
        """
        Checks whether touch.pos is inside the displayed shape
        touch.pos is reflected onto the first quadrant
        and checked        
        """
        x, y = self.to_widget(*touch.pos, relative=True)
        center = self.to_widget(*self.center, relative=True)

        touch_arr = np.array([x - center[0], y - center[1]])   # with respect to center
        quadrant = 1
        
        # find which quadrant the touch is
        if x >= center[0]:
            if y >= center[1]:
                pass
                # no reflection required
            else:
                # reflect on x-axis
                ref_arr = np.array([[1, 0], [0, -1]])
                touch_arr = np.matmul(touch_arr, ref_arr)

        elif y >= center[1]:
            ref_arr = np.array([[-1, 0], [0, 1]])
            touch_arr = np.matmul(touch_arr, ref_arr)

        else: 
            ref_arr = np.array([[0, -1], [-1, 0]])
            touch_arr = np.matmul(touch_arr, ref_arr)

        line_coords = list(zip(self.line_points[0::2], self.line_points[1::2]))

        # get the angle of the touch.
        touch_angle = math.atan(touch_arr[1] / touch_arr[0])

        # convert relative line coordinates 
        first_quadrant_coords = []
        
        for coord in line_coords:
            coord = self.to_widget(*coord, relative=True)
            coord = (round(coord[0] - center[0], 5), round(coord[1] - center[1], 5))
            
            # Cut down to first quadrant only
            if coord[0] >= 0 and coord[1] >= 0:
                try:
                    coord = coord + (math.atan(coord[1] / coord[0]), )
                except ZeroDivisionError:
                    coord = coord + (pi/2, )
                first_quadrant_coords.append(coord)    
        
        return_val = [False, False]
        
        # sort ascending angle
        sorted_first_quadrant_coords = sorted(first_quadrant_coords, key=lambda x:x[-1])
        for index, coord in enumerate(sorted_first_quadrant_coords):
            if index == len(sorted_first_quadrant_coords) - 1:
                break
            if coord[-1] <= touch_angle <= sorted_first_quadrant_coords[index+1][-1]:
                x1 = sorted_first_quadrant_coords[index+1][0]
                y1 = sorted_first_quadrant_coords[index+1][1]
                x2 = coord[0]
                y2 = coord[1]
                r = (x2*(y1-y2) - y2*(x1-x2)) / ( ( cos(touch_angle) * (y1-y2)  ) -  ( sin(touch_angle) * (x1-x2) ) )
                r_touch = touch_arr[0] / cos(touch_angle) 
                return_val = [False, False]

                if r_touch <= (r + self.border_width*3 ):
                    return_val[0] = True
                    if in_border and abs(r_touch - r) <= (self.border_width*3):
                        return_val[1] = True
                return return_val 
        return return_val

    def touch_relative_angle(self, touch):
        (x, y) = self.to_widget(*touch.pos, relative=True)
        center = self.to_widget(*self.center, relative=True)
        (x, y) = (x - center[0], y - center[1])
        if x >= 0:
            if y >= 0:
                return math.atan(y/x)
            elif y <= 0:
                return math.atan(y/x) + 2*pi
        elif y >= 0:
            return math.atan(y/x) + pi
        else:
            return math.atan(y/x) + pi

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos) or touch.button != "left":
            self.drag_timeout = 0
            return super(DragAndResizePolygon, self).on_touch_up(touch)
        if self._fixed:
            return super(DragAndResizePolygon, self).on_touch_up(touch)
        
        if touch.button == "left":
            self._touch_region = "undef"
        else:
            return super(DragAndResizePolygon, self).on_touch_up(touch)

        self.drag_timeout = 0
        self.pos_hint = {}
        self.pos = (self.x, self.y)
        self.size_hint = (None, None)
        is_within_shape, is_within_border = self.check_relative_touch_pos(touch, in_border=True)
        
        if (is_within_shape or is_within_border) and self.mode != "Border" and not self.lock_pos:
            self.drag_timeout = 10000000

        if is_within_border:
            touch_angle = self.touch_relative_angle(touch)
            if pi/4 <= touch_angle < 0.75*pi:
                self._touch_region = "n"
                Window.set_system_cursor('size_ns')

            elif 0.75*pi <= touch_angle < 1.25*pi:
                Window.set_system_cursor('size_we')
                self._touch_region = "w"

            elif 1.25*pi <= touch_angle < 1.75*pi:
                Window.set_system_cursor('size_ns')
                self._touch_region = "s"
            else: 
                Window.set_system_cursor('size_we')
                self._touch_region = "e"

        touch.ud["touch_region"] = self._touch_region
        
        if self._touch_region != "undef":
            touch.ud["size_node"] = self
            return True
        return super(DragAndResizePolygon, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._fixed:
            return super(DragAndResizePolygon, self).on_touch_up(touch)

        xx, yy = self.to_widget(*touch.pos, relative=True)
        if "size_node" in touch.ud.keys():
            if "touch_region" in touch.ud.keys():
                if touch.ud["touch_region"] == "undef":
                    return super(DragAndResizePolygon, self).on_touch_move(touch)
                if self.lock_size:
                    return super(DragAndResizePolygon, self).on_touch_move(touch)
                if touch.ud["touch_region"] == 'n':
                    if yy > 0:
                        if self.size_hint_y is None:
                            self.height = min(yy, self.parent.height)
                        else:
                            self.size_hint_y = yy / self.parent.height
                            if self.size_hint_y >= 1:
                                self.size_hint_y = 1
                
                elif touch.ud["touch_region"] == "e":
                    if xx > 0:
                        if self.size_hint_x is None:
                            self.width = xx
                        else:
                            self.size_hint_x = xx / self.parent.width
                            self.width = xx
                
                elif touch.ud["touch_region"] == "w":
                    if self.width - xx > 0:
                        if self.size_hint is None:
                            self.width -= xx
                            self.x += xx
                        else:
                            self.size_hint_x = min(1, (self.width - xx) / self.parent.width)
                            self.x += xx
                
                elif touch.ud["touch_region"] == "s":
                    if self.height - yy > 0:
                        if self.size_hint_y is None:
                            self.height -= yy
                            self.y += yy
                        else:
                            self.size_hint_y = (self.height - yy) / self.parent.height
                            self.y += yy
                return super(DragAndResizePolygon, self).on_touch_move(touch)
        return super(DragAndResizePolygon, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self._fixed:
            return super(DragAndResizePolygon, self).on_touch_up(touch)
        Window.set_system_cursor('arrow')
        if self.lock_pos:
            self.drag_timeout = 0
        else:
            self.drag_timeout = 10000000
        self.pos_hint = {"x": (self.x - self.parent.x) / self.parent.width,
                         "y": (self.y - self.parent.y) / self.parent.height}
        self.size_hint = (self.width/self.parent.width, self.height/self.parent.height)

        return super(DragAndResizePolygon, self).on_touch_up(touch)


class DragAndResizeTriangle(DragBehavior, Widget):
    fill_color = ListProperty([1, 0, 1, 0])
    triangle_points = ListProperty([])
    border_color = ListProperty([0, 0, 1, 1])
    border_width = NumericProperty(2)
    border_points = ListProperty([])
    _r_tol = NumericProperty(25)
    point_size = NumericProperty(5)

    def __init__(self, **kwargs):
        super(DragAndResizeTriangle, self).__init__(**kwargs)
        self.constrain_to_parent_window = True
        self._drag_active = True
        self._triangle_points_rel = [] # store relative points of triangle points
        self._index_num = None
        self.shape_settings = None
        self.mode = "Fill"
        self.lock_size = False
        self.lock_pos = False
        self._fixed = False
        self._touch = None

    def __del__(self):
        Window.unbind(on_motion=self.on_window_motion)
    
    def on_window_motion(self, *args):
        for arg in args:
            if type(arg).__name__ == "MouseMotionEvent":
                self._touch = arg

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if self._touch is None:
            return True
        elif ("delete" or "backspace" in keycode) and self._fixed:
            is_within_shape, is_within_border = self.check_relative_touch_pos(self._touch, in_border=True)
            if (is_within_border and self.mode == "Border") or (is_within_shape and self.mode == "Fill"):
                self.canvas_manager.remove_widget(self)
        return True


    def set_lock_pos(self, instance, value):
        if value:
            pos_hint_x = (self.x - self.parent.x) / self.parent.width
            pos_hint_y = (self.y - self.parent.y) / self.parent.height
            print(pos_hint_x, pos_hint_y)
            self.pos_hint = {"x": pos_hint_x, "y": pos_hint_y}
            self.drag_timeout = 0
        else:
            self.drag_timeout = 1000000
            self.pos_hint = {}
            self.pos = (self.x, self.y) 

    def set_lock_size(self, instance, value):
        if value:
            self.size_hint_x = self.size[0] / self.parent.width
            self.size_hint_y = self.size[1] / self.parent.height
        
        self.lock_size = value   

    def set_fill_color(self, instance, value):
        if self.mode != "Border":
            self.fill_color = value

    def set_border_color(self, instance, value):
        self.border_color = value


    def update_property(self, property, value):
        setattr(self, property, value)

    def on_pos(self, instance, value):
        self.pos = value
        self.draw_triangle()

    def on_size(self, instance, value):
        self.size = value
        self.draw_triangle()

    def draw_triangle(self):
        if self.triangle_points == []:
            self.triangle_points = [self.x, self.y, 
                                    self.x+self.width/2, self.y+self.height, 
                                    self.x+self.width, self.y]
            self.triangle_points = self.triangle_points
            self.triangle_points_rel = self.triangle_to_wid()

        elif self._drag_active:
            # get relative pos w.r.t previous position
            for index, point in enumerate(self.triangle_points):
                if index % 2 == 0:
                    self.triangle_points[index] = self.x + self.triangle_points_rel[index]
                else:
                    self.triangle_points[index] = self.y + self.triangle_points_rel[index]
            # force update
            self.triangle_points = self.triangle_points

        border_points = self.triangle_points + self.triangle_points[0:2]
        self.border_points = border_points


    def check_touch_pos(self, touch, check_is_within=False):
        """
        returns index of point that was touched!
        if check_is_wthin is True, checks whether touch.pos is inside triangle
        """
        is_within = False
        (x, y) = touch.pos
        [x0, y0] = self.triangle_points[0:2]
        [x1, y1] = self.triangle_points[2:4]
        [x2, y2] = self.triangle_points[4:6]
        if check_is_within:
            def area(x0, y0, x1, y1, x2, y2):
                return abs((x0*(y1-y2) + x1*(y2 - y0) + x2*(y0 - y1))/2.0)
            A0 = area(x, y, x1, y1, x2, y2)
            A1 = area(x0, y0, x, y, x2, y2)
            A2 = area(x0, y0, x1, y1, x, y)
            A = area(x0, y0, x1, y1, x2, y2)
            if 0.95*A  < A0 + A1 + A2 < 1.05*A:
                is_within = True
        
        tol_r = self._r_tol # tolerance radius
        (h, k) = touch.pos
        x_s = self.triangle_points[0::2]
        y_s = self.triangle_points[1::2]
        points = list(zip(x_s,y_s))
        for index, (x, y) in enumerate(points):
            touch_radius = math.sqrt((x-h)**2  + (y-k)**2)
            if  touch_radius <= tol_r:
                return [index, (x,y), is_within]

        return [None, None, is_within]

    def triangle_to_wid(self):
        """
        returns relative triangle points to widget
        """
        xs = self.triangle_points[0::2]
        ys = self.triangle_points[1::2]
        tri_points = list(zip(xs, ys))
        rel = []
        for coord in tri_points:
            rel.append(self.to_widget(*coord, relative=True))
        rel = [ point for coord in rel for point in coord]
        return rel
    
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos) or touch.button != "left":
            return super().on_touch_up(touch)
        if self._fixed:
            return super(DragAndResizeTriangle, self).on_touch_up(touch)

        else:
            self.pos_hint = {}
            self.pos = (self.x, self.y)
            self.size_hint = (None, None)
            if self.mode == "Fill":
                [corner_touched, _, is_within_tri] = self.check_touch_pos(touch, check_is_within=True)
                if corner_touched is None:
                    self._index_num = None
                    self._drag_active = True
                    if not self.lock_pos:
                        self.drag_timeout = 1000000
                    else:
                        self.drag_timeout = 0
                    
                    if is_within_tri:
                        return super().on_touch_down(touch)
                    else:
                        return super().on_touch_up(touch)
                else:
                    Window.set_system_cursor("crosshair")
                    self._index_num = corner_touched
                touch.ud["point_index"] = self._index_num
                if self._index_num is not None:
                    touch.ud["size_node"] = self
                return super().on_touch_down(touch)

            elif self.mode == "Border":
                self.drag_timeout = 0
                [corner_touched, _, is_within_tri] = self.check_touch_pos(touch)
                if corner_touched is not None:
                    if self.lock_pos and corner_touched == 0:
                        corner_touched = None
                    Window.set_system_cursor("crosshair")
                    self._index_num = corner_touched
                else:
                    self._index_num = None
                    return super().on_touch_up(touch)
                touch.ud["point_index"] = self._index_num
                if self._index_num is not None:
                    touch.ud["size_node"] = self

        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._fixed:
            return super(DragAndResizeTriangle, self).on_touch_up(touch)

        if self.lock_size:
            return super(DragAndResizeTriangle, self).on_touch_move(touch)

        if "size_node" in touch.ud.keys():
            if "point_index" in touch.ud.keys():
                index = touch.ud["point_index"]  # 0, 1, 2
                index_0 = self.to_widget(*self.triangle_points[0:2], relative=True)
                index_1 = self.to_widget(*self.triangle_points[2:4], relative=True)
                index_2 = self.to_widget(*self.triangle_points[4:6], relative=True)
                xx, yy = self.to_widget(*touch.pos, relative=True)
                if index is None or \
                    ((touch.pos[0] < self.parent.x or touch.pos[1] > (self.parent.x + self.parent.width)*0.99) or \
                    (touch.pos[1] < self.parent.y or touch.pos[1] > (self.parent.y + self.parent.height)*0.99)):
                    return super(DragAndResizeTriangle, self).on_touch_up(touch)

                elif index == 0:
                    self.triangle_points[1] = touch.pos[1]
                    self.triangle_points[0] = touch.pos[0]

                elif index == 1:
                    if yy > min(index_0[1], index_2[1]):
                        self.triangle_points[2] = touch.pos[0]
                        self.triangle_points[3] = touch.pos[1]

                elif index == 2:
                    self.triangle_points[4] = touch.pos[0]
                    self.triangle_points[5] = touch.pos[1]

                self.triangle_points = self.triangle_points                
                self.border_points = self.triangle_points + self.triangle_points[0:2]

                # update the widget's position and size
                [x0, y0] = self.triangle_points[0:2]
                [x1, y1] = self.triangle_points[2:4]
                [x2, y2] = self.triangle_points[4:6]
                self.width = max(x0, x1, x2) - min(x0, x1, x2)
                self.x = min(x0, x1, x2)
                self.height = max(y0, y1, y2) - min(y0, y1, y2)
                self.y = min(y0, y1, y2)

        self.triangle_points_rel = self.triangle_to_wid()        
        return super(DragAndResizeTriangle, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self._fixed:
            return super(DragAndResizeTriangle, self).on_touch_up(touch)
        if self.lock_pos:
            self.drag_timeout = 0
        Window.set_system_cursor('arrow')
        self._drag_active = False
        self.pos_hint = {"x": (self.x - self.parent.x) / self.parent.width,
                         "y": (self.y - self.parent.y) / self.parent.height}
        self.size_hint = (self.width/self.parent.width, self.height/self.parent.height)
        return super(DragAndResizeTriangle, self).on_touch_up(touch)


class GridWidget(Widget):
    grid_color = ListProperty( [0.7, 0.5, 0.3, 1])    #    [0.5, 0.2, 1, 1])
    grid_line_thickness = NumericProperty(1)
    SCALE_RATIO = 0.07
    SCALE = ObjectProperty([1, "m"])
    MAX_GRIDLINES = 15
    include_points = BooleanProperty(True)
    point_size = NumericProperty(2)
    point_color = ListProperty([1, 0, 1, 1])

    def __init__(self, **kwargs):
        super(GridWidget, self).__init__(**kwargs)
        self.horizontal_lines = []
        self.vertical_lines = []
        self.labels = []
        self.points_color = Color(*self.point_color)
        self.points = InstructionGroup()
        self.lines = InstructionGroup()
        self.draw_grid()


    def update_scale(self, *args):
        """
        this function is bound to Constant.CANVAS_SCALE
        """
        if len(args) == 1:
            self.scale = args[0]
        elif len(args) == 2:
            self.scale = args[1]

    def force_max_length(self, length: str or float, unit:str, *args):
        """
        Changes the max length of the label
        Recalculates the markings accordingly
        length: str or float . maximum length
        unit: "m" or "ft"
        """
        
        per_line = round(float(length) * self.SCALE_RATIO, 2)
        self.SCALE = [per_line, str(unit)]


    def on_SCALE(self, instance, value):
        """
        Whenever the scale changes,
         this function is called
        """
        self.update_grid()

    def on_pos(self, item, value):
        self.pos = value
        self.update_grid()

    def on_point_size(self, item, value):
        self.points.pointsize = value

    def on_grid_color(self, item, value):
        for (color, line) in self.horizontal_lines:
            color.rgba = value
        for (color, line) in self.vertical_lines:
            color.rgba = value

    def on_point_color(self, item, value):
        self.points_color.rgba = value


    def draw_grid(self, *args):
        
        # x axis
        # Adding 15 grid lines

        for x_pos in range(0, int(self.width), int(self.width*self.SCALE_RATIO)):
            if x_pos > self.height:
                continue
            color = Color(*self.grid_color)
            line = Line(points=(self.x+ x_pos, self.y, self.x + x_pos, self.y+self.height))
            self.vertical_lines.append((color, line))
            self.lines.add(color)
            self.lines.add(line)

        for y_pos in range(0, int(self.height), int(self.height*self.SCALE_RATIO)):
            if y_pos > self.height:
                continue
            color = Color(*self.grid_color)
            line = Line(points=(self.x, self.y+y_pos, self.x+self.width, self.y+y_pos))
            self.horizontal_lines.append((color, line))
            self.lines.add(color)
            self.lines.add(line)

        self.canvas.add(self.lines)
        self.add_scale_markings()

    def update_grid(self, *args):
        """
        Update the grid lines based on canvas 
        pos adjustment
        1 line represents 1 m
        """

        for line_num, (color, line) in enumerate(self.vertical_lines):
            if (line_num+1)*(self.width*self.SCALE_RATIO) > self.width:
                self.lines.remove(color)
                self.lines.remove(line)
                self.vertical_lines.remove((color, line))
                continue
            line.points = ((line_num+1)*(self.width*self.SCALE_RATIO) + self.x, 
                           self.y, 
                           (line_num+1)*(self.width*self.SCALE_RATIO) + self.x,
                           self.y+self.height)

        for line_num, (color, line) in enumerate(self.horizontal_lines):
            if (line_num+1)*(self.height*self.SCALE_RATIO) > self.height:
                self.lines.remove(color)
                self.lines.remove(line)
                self.horizontal_lines.remove((color, line))
                continue
            line.points = (self.x, 
                           self.y+(line_num+1)*(self.height*self.SCALE_RATIO), 
                           self.x+self.width,
                           self.y+(line_num+1)*(self.height*self.SCALE_RATIO))
        self.points.clear()
        
        if self.include_points:
            points = []

            for (color_x, line_x) in self.vertical_lines:
                for (color_y, line_y) in self.horizontal_lines:
                    points.append(line_x.points[0])
                    points.append(line_y.points[1])
            self.points.add(self.points_color)
            self.points.add(Point(points=points, pointsize=self.point_size))
            self.canvas.add(self.points)
        self.update_scale_markings()


    def add_scale_markings(self):
        """ 
        use Scale Markings
        
        """
        for pos, (color_x, line_x) in enumerate(self.vertical_lines):
            points = line_x.points[2::]
            label = Label(text=f"{round(self.SCALE[0] + (pos*float(self.SCALE[0])), 3)} {self.SCALE[1]}")
            label.size = (0, 0)
            label.pos = points
            self.add_widget(label)
            self.labels.append(label)

    def update_scale_markings(self):
        if self.labels == []:
            return
        else:
            
            while len(self.labels) != len(self.vertical_lines):
                self.remove_widget(self.labels[-1])
                self.labels.pop()
            for pos, label in enumerate(self.labels):
                label.pos = self.vertical_lines[pos][1].points[2::]
                label.text = f"{round(self.SCALE[0] + (pos*float(self.SCALE[0])), 3)} {self.SCALE[1]}"


class ColorDropDown(DropDown):
    red_slider = ObjectProperty()
    green_slider = ObjectProperty()
    blue_slider = ObjectProperty()
    transparency_slider = ObjectProperty()
    none_button = ObjectProperty()


class ShapeSettings(GridLayout):

    _root = ObjectProperty()
    _label_font_size = NumericProperty(15)

    _shape_fill_color = ListProperty([0, 0, 0, 1])
    _shape_border_color = ListProperty([1, 1, 1, 1])
    _bkg_color = ListProperty([0, 0, 0, 1])

    _shape_label = ObjectProperty()
    _shape_spinner = ObjectProperty()
    _type_label = ObjectProperty()
    _type_spinner = ObjectProperty()

    _fill_color_label = ObjectProperty()
    _fill_color_button = ObjectProperty()
    _fill_color_red_slider = ObjectProperty()
    _fill_color_green_slider = ObjectProperty()
    _fill_color_blue_slider = ObjectProperty()
    _fill_color_transparency = ObjectProperty()
    
    _border_color_label = ObjectProperty()
    _border_color_button = ObjectProperty()
    _border_color_red_slider = ObjectProperty()
    _border_color_green_slider = ObjectProperty()
    _border_color_blue_slider = ObjectProperty()
    _border_color_transparency = ObjectProperty()

    _lock_size_label = ObjectProperty()
    _lock_size_checkbox = ObjectProperty()

    _lock_position_label = ObjectProperty()
    _lock_position_checkbox = ObjectProperty()

    _segments_label = ObjectProperty(None, allownone=True)
    _segments_text_input = ObjectProperty(None, allownone=True)

    _place_button = ObjectProperty()
    _new_button = ObjectProperty()
    _remove_button = ObjectProperty()

    _segments_label_color = ObjectProperty(None, allownone=True)
    _segments_label = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._fill_color_dropdown = ColorDropDown()
        self._border_color_dropdown = ColorDropDown()
        Clock.schedule_once(self.initialize, 1)
        self.shape_properties = {}
        self.shape_canvas = None
        self._widget_placed = False
        self._active_widget = None

        # Slider references
        self._minimum_fill_slider_x = None

    def on_pos(self, instance, value):
        self.pos = value

    def on_size(self, instance, value):
        self.size = value

    def initialize(self, *args):
        self.shape_canvas = self._root.ids["robot_canvas"]

        self.shape_properties["lock_pos"] = False
        self.shape_properties["lock_size"] = False

        self._fill_color_button.bind(on_release=self._fill_color_dropdown.open)
        self._border_color_button.bind(on_release=self._border_color_dropdown.open)

        self._fill_color_dropdown.none_button.bind(on_release=self.set_fill_to_none)
        self._fill_color_dropdown.red_slider.bind(value=self.set_fill_red)
        self._fill_color_dropdown.green_slider.bind(value=self.set_fill_green)
        self._fill_color_dropdown.blue_slider.bind(value=self.set_fill_blue)
        self._fill_color_dropdown.transparency_slider.bind(value=self.set_fill_transparency)

        self._border_color_dropdown.none_button.bind(on_release=self.set_border_to_none)
        self._border_color_dropdown.red_slider.bind(value=self.set_border_red)
        self._border_color_dropdown.green_slider.bind(value=self.set_border_green)
        self._border_color_dropdown.blue_slider.bind(value=self.set_border_blue)
        self._border_color_dropdown.transparency_slider.bind(value=self.set_border_transparency)

        self._shape_spinner.bind(text=self.set_shape)
        self._type_spinner.bind(text=self.set_type)
        self._lock_position_checkbox.bind(active=self.set_lock_pos)
        self._lock_size_checkbox.bind(active=self.set_lock_size)
        self._place_button.bind(on_release=self.place_shape)
        self._new_button.bind(on_release=self.new_shape)

        self._shape_fill_color = [0, 0, 0, 0]
        self._shape_border_color = [0, 0, 0, 0]
        self.shape_properties["unit"] = 'm'
        self.shape_properties["type"] = "Border"
        self.shape_properties["shape"] = "Rectangle"
        self.shape_properties["segments"] = 0

        self._minimum_fill_slider_x = self._fill_color_dropdown.transparency_slider.value_pos[0]
        self._minimum_border_slider_x = self._border_color_dropdown.transparency_slider.value_pos[0]

    ## label color change
    def on__bkg_color(self, instance, value):
        if self._segments_label_color is not None:
            self._segments_label_color.color = value 
    
    ## font size change
    def on__label_font_size(self, instance, value):
        if self._segments_label.font_size is not None:
            self._segments_label.font_size = value  

    #+============= Fill Methods ==================#
    def set_fill_to_none(self, *args):
        self._fill_color_button.text = "[i]None[/i]"

        current_cursor_pos = list(self._fill_color_dropdown.red_slider.value_pos)
        current_cursor_pos[0] = self._minimum_fill_slider_x
        self._fill_color_dropdown.red_slider.value_pos = tuple(current_cursor_pos)

        current_cursor_pos = list(self._fill_color_dropdown.green_slider.value_pos)
        current_cursor_pos[0] = self._minimum_fill_slider_x
        self._fill_color_dropdown.green_slider.value_pos = tuple(current_cursor_pos)

        current_cursor_pos = list(self._fill_color_dropdown.blue_slider.value_pos)
        current_cursor_pos[0] = self._minimum_fill_slider_x
        self._fill_color_dropdown.blue_slider.value_pos = tuple(current_cursor_pos)

        current_cursor_pos = list(self._fill_color_dropdown.transparency_slider.value_pos)
        current_cursor_pos[0] = self._minimum_fill_slider_x
        self._fill_color_dropdown.transparency_slider.value_pos = tuple(current_cursor_pos)

        self._fill_color_dropdown.dismiss()
        self._shape_fill_color = [0, 0, 0, 0]        


    def set_fill_red(self, instance, value):
        self._shape_fill_color[0] = float(value)

    def set_fill_green(self, instance, value):
        self._shape_fill_color[1] = float(value)
        

    def set_fill_blue(self, instance, value):
        self._shape_fill_color[2] = float(value)

    def set_fill_transparency(self, instance, value):
        self._shape_fill_color[3] = float(value)

    def on__shape_fill_color(self, *args):
        if self._shape_fill_color == [0, 0, 0, 0] or self._shape_fill_color[-1] == 0:
            self._fill_color_button.text = "[i]None[/i]"
        else: 
            self._fill_color_button.text = ""
        self.shape_properties["fill_color"] = self._shape_fill_color

    #================================================#
    #================================================#


    #+============= Border Methods ==================#

    def set_border_to_none(self, *args):
        self._border_color_button.text = "[i]None[/i]"
        current_cursor_pos = list(self._border_color_dropdown.red_slider.value_pos)
        current_cursor_pos[0] = self._minimum_border_slider_x
        self._border_color_dropdown.red_slider.value_pos = tuple(current_cursor_pos)

        current_cursor_pos = list(self._border_color_dropdown.green_slider.value_pos)
        current_cursor_pos[0] = self._minimum_border_slider_x
        self._border_color_dropdown.green_slider.value_pos = tuple(current_cursor_pos)

        current_cursor_pos = list(self._border_color_dropdown.blue_slider.value_pos)
        current_cursor_pos[0] = self._minimum_border_slider_x
        self._border_color_dropdown.blue_slider.value_pos = tuple(current_cursor_pos)

        current_cursor_pos = list(self._border_color_dropdown.transparency_slider.value_pos)
        current_cursor_pos[0] = self._minimum_border_slider_x
        self._border_color_dropdown.transparency_slider.value_pos = tuple(current_cursor_pos)

        self._border_color_dropdown.dismiss()
        self._shape_border_color = [0, 0, 0, 0]  
    #===============================================#
    #===============================================#


    #============= Border Properties ===============#
    def set_border_red(self, instance, value):
        self._shape_border_color[0] = float(value)

    def set_border_green(self, instance, value):
        self._shape_border_color[1] = float(value)
        
    def set_border_blue(self, instance, value):
        self._shape_border_color[2] = float(value)

    def set_border_transparency(self, instance, value):
        self._shape_border_color[3] = float(value)

    def on__shape_border_color(self, *args):
        if self._shape_border_color == [0, 0, 0, 0] or self._shape_border_color[-1] == 0:
            self._border_color_button.text = "[i]None[/i]"
        else: 
            self._border_color_button.text = ""
        self.shape_properties["border_color"] = self._shape_border_color
    #===============================================#
    #===============================================#


    #============== Polygon segments ===============#
    def add_segments_section(self, *args):
        # Called when shape is set to "Polygon"  
        # Add the segments Label
        self._segments_label = Label()
        self._segments_label.font_size = self._label_font_size
        self._segments_label.text = "[i]Segments:[/i]"
        self._segments_label.markup = True
        self.add_widget(self._segments_label)

        def update_label_canvas(obj, label, bkg_color, *largs):
            _segments_label_rect = Rectangle()  
            _segments_label_rect.pos = label.pos 
            _segments_label_rect.size = label.size   
            obj._segments_label_color = Color(*bkg_color)    
            obj._segments_label.canvas.before.add(obj._segments_label_color) 
            obj._segments_label.canvas.before.add(_segments_label_rect)   

        Clock.schedule_once(partial(update_label_canvas,
                            self, 
                            self._segments_label, 
                            self._bkg_color), 
                            0.1)

        # Add the text input Label
        self._segments_text_input = TextInput()
        self._segments_text_input.multiline = False
        self._segments_text_input.background_color = [0, 0, 0, 1]
        self._segments_text_input.foreground_color = [1, 1, 1, 1]
        self._segments_text_input.input_filter = "float"
        self.add_widget(self._segments_text_input)
        self._segments_text_input.bind(text=self.add_num_segments)

    def remove_segments_section(self, *args):
        # called when shape is anything except Polygon
        if self._widget_placed:
            return
        if self._segments_label is not None and self._segments_text_input is not None:
            self.remove_widget(self._segments_text_input)
            self.remove_widget(self._segments_label)
            self._segments_label_color = None
    #===============================================#
    #===============================================#


    #=========== set Shape Properties =============#
    def set_shape(self, instance, value):
        self.shape_properties["shape"] = value
        if str(value).lower() == "Polygon".lower():
            self.add_segments_section()
        else:
            self.remove_segments_section()
            self.shape_properties["segments"] = 0

    def set_type(self, instance, value):
        self.shape_properties["type"] = str(value)

    def set_lock_pos(self, instance, value):
        self.shape_properties["lock_pos"] = bool(value)

    def set_lock_size(self, instance, value):
        value = bool(value)
        self.shape_properties["lock_size"] = value

    def add_num_segments(self, instance, value):
        self.shape_properties["segments"] = value

    def new_shape(self, instance):
        if self._active_widget is None:
            return
        if self.shape_canvas.canvas_manager.untrack_widget(self, self._active_widget):
            self._place_button.disabled = False
            self._widget_placed = False
            self._active_widget = None

    #======== Callbacks to Robot Canvas =======#

    def place_shape(self, instance):
        widget_placed = self.shape_canvas.canvas_manager.add_shape(self, self.shape_properties)
        if widget_placed:
            self._widget_placed = True
            self._place_button.disabled = True
            self._active_widget = widget_placed


class ScaleSettings(GridLayout):
    
    text_input_wid = ObjectProperty()
    max_length_label = ObjectProperty()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.canvas_manager = None
        Clock.schedule_once(self.initialize, 5)

    def on_pos(self, instance, value):
        self.pos = value

    def on_size(self, instance, value):
        self.size = value

    def initialize(self, *args):
        self.text_input_wid.bind(text=self.canvas_manager.update_canvas_scale)
        self.text_input_wid.disabled = True

    def update_property(self, property, value):
        setattr(self, property, value)



class SelectableBoxLayout(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    text = StringProperty("")
    line_pos_x = BoundedNumericProperty(0.1, min=0, max=1, errorvalue=0)
    border_color = ListProperty([1, 0.5, 0.5, 1])
    allow_edit = BooleanProperty(True)
    rv = ObjectProperty()
    values = DictProperty({})
    set_active_index = ObjectProperty()
    starting_x = BoundedNumericProperty(0, min=0, max=1, errorvalue=0)

    ## Custom attributes
    angle = BoundedNumericProperty(0, min=-360, max=360, errorvalue=0)
    duration = BoundedNumericProperty(0, min=0)
    expansion = NumericProperty(0)
    transition = StringProperty("")
    transition_type = StringProperty("")


    def on_values(self, instance, values):
        for (key, value) in values.items():
            setattr(self, key, value)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.rv = rv
        return super().refresh_view_attrs(rv, index, data)
    
    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)
    
        return super(SelectableBoxLayout, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos) and self.selected:
            if self.allow_edit:
                xx, yy = self.to_widget(*touch.pos, relative=True)
                new_line_pos_x = xx/self.width - self.starting_x
                if new_line_pos_x > 0:
                    self.line_pos_x = new_line_pos_x
        
        return super().on_touch_move(touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        if is_selected:
            ## delete an entry
            values = {'angle': self.angle, 'transition': self.transition, }

            self.set_active_index(self.index, {})
            ## How to add to the list!!!
            if len(rv.data) == 0:
                rv.data.append({'_text': '5'})
        else:
            self.rv.layout_manager.clear_selection()


class ChoreoBoard(BoxLayout):
    canvas_manager = ObjectProperty(allownone=True)
    animation_selection = ObjectProperty(allownone=True)
    requested_shape = StringProperty("")
    rectangle_btn = ObjectProperty()
    ellipse_btn = ObjectProperty()
    polygon_btn = ObjectProperty()
    triangle_btn = ObjectProperty()
    
    segments_layout = ObjectProperty()
    segments_layout_added = BooleanProperty(False)
    
    add_shape_to_choreography_btn = ObjectProperty()
    add_shape_to_canvas_btn = ObjectProperty()
    remove_from_canvas_btn = ObjectProperty()
    transition_choice_spn = ObjectProperty()
    lock_effect_btn = ObjectProperty()
    num_robots_spn = ObjectProperty()
    num_robots_input = ObjectProperty()
    
    start_delay_input = ObjectProperty()
    exit_delay_input = ObjectProperty()
    value_slider = ObjectProperty()
    value_2_slider = ObjectProperty()
    duration_input = ObjectProperty()
    preview_effect_btn = ObjectProperty()
    add_effect_to_shape_btn = ObjectProperty()
    animation_selection = ObjectProperty()
    simulate_btn = ObjectProperty()
    delete_btn = ObjectProperty()
    preview_shape_effects_btn = ObjectProperty()

    ## handlers
    segments_text_input = ObjectProperty(None, allownone=True)
    shape_added_to_canvas = BooleanProperty(False)
    shape_added_to_choreography = BooleanProperty(False)
    active_shape = ObjectProperty(None, allownone=True)    



    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        Clock.schedule_once(self.initialize, 1)
        self.shape_btn_pressed = None
        self.added_shapes = {}

    def on_canvas_manager(self, instance, value):
        if value is not None:
            self.animation_selection.canvas_manager = value

    def on_pos(self, instance, value):
        self.pos = value

    def on_size(self, instance, value):
        self.size = value

    def add_shape_to_canvas(self, btn, *args):
        shape = None
        if self.shape_btn_pressed is None:
            return
        
        elif self.shape_btn_pressed.text == "Rectangle":
            shape = ChoreoRect()
        elif self.shape_btn_pressed.text == "Ellipse":
            shape = ChoreoPolygon()
        elif self.shape_btn_pressed.text == "Polygon":
            if self.segments_text_input.text in ("0", ''):
                InformationPopup(_type='e', _message= "Segments not specified!!").open()
                return
            shape = ChoreoPolygon(segments=int(self.segments_text_input.text))
        elif self.shape_btn_pressed.text == "Triangle":
            shape = ChoreoTriangle()
        else:
            return
        self.active_shape = shape
        self.canvas_manager.parent.add_widget(shape)
        shape.pos_hint = {}
        shape.center = self.canvas_manager.parent.center
        shape.size_hint = (None, None)
        shape.size = (self.canvas_manager.parent.size[0] / 4, self.canvas_manager.parent.size[1] / 4)

        if self.added_shapes == {}:
            shape.index = 0
        else:
            shape.index = len(self.added_shapes) 
        self.added_shapes[str(shape.index)] = shape 
        
        ## Add rotation, angle functionalities to the shape
        self.value_slider.bind(value=shape.rotate)
        self.value_slider.bind(value=shape.expand)
        self.value_2_slider.bind(value=shape.rotate)
        self.value_2_slider.bind(value=shape.expand)
       

    def add_segments_layout(self):
        if self.segments_layout_added:
            return
        segments_lbl = Label()
        segments_lbl.markup = True
        segments_lbl.text = "[i]Segments:[/i]"
        self.segments_text_input = TextInput()
        self.segments_text_input.multiline = False
        self.segments_text_input.input_filter = "float"
        self.segments_layout.add_widget(segments_lbl)
        self.segments_layout.add_widget(self.segments_text_input)
        
        def update_canvas(self, *args):
            segments_lbl.canvas.before.add(Color(0,0,0,1))
            segments_lbl.canvas.before.add(Rectangle(pos=segments_lbl.pos, 
                                                     size=segments_lbl.size))
        Clock.schedule_once(update_canvas, 0.2)
        self.segments_layout_added = True

    def remove_segments_layout(self):
        self.segments_layout.clear_widgets()
        self.segments_layout_added = False
        self.segments_text_input = None

    def lock_effect(self, instance):
        if instance.text == "Lock Effect":
            self.active_shape.migrate_to_next_shape(effect_type=self.transition_choice_spn.text)
            self.transition_choice_spn.disabled = True
            instance.text = "Discard Effect"
        elif instance.text == "Discard Effect":
            self.active_shape.revert_to_previous_shape()
            self.transition_choice_spn.disabled = False
            instance.text = "Lock Effect"


    def on_shape_btn_pressed(self, btn):
        if self.shape_btn_pressed == btn:
            if btn.background_color == [0, 0.4, 0.5, 1]:
                btn.background_color = [0, 0.7, 0.4, 1]
                self.shape_btn_pressed = btn
            elif btn.background_color == [0, 0.7, 0.4, 1]:
                btn.background_color = [0, 0.4, 0.5, 1]
                self.shape_btn_pressed = None

        elif self.shape_btn_pressed is None:
            btn.background_color = [0, 0.7, 0.4, 1]
            self.shape_btn_pressed = btn
        
        else:
            btn.background_color = [0, 0.7, 0.4, 1]
            self.shape_btn_pressed.background_color = [0, 0.4, 0.5, 1]
            self.shape_btn_pressed = btn
        
        if btn.text == "Rectangle":
            pass
        elif btn.text == "Polygon":
            self.add_segments_layout()
        else:
            self.remove_segments_layout()


    def initialize(self, *args):
        self.rectangle_btn.bind(on_press=self.on_shape_btn_pressed)
        self.ellipse_btn.bind(on_press=self.on_shape_btn_pressed)
        self.polygon_btn.bind(on_press=self.on_shape_btn_pressed)
        self.triangle_btn.bind(on_press=self.on_shape_btn_pressed)
        self.add_shape_to_canvas_btn.bind(on_press=self.add_shape_to_canvas)
        self.lock_effect_btn.bind(on_release=self.lock_effect)


class ChoreoBase:
    c_border_color = ListProperty([1, 0.5, 1, 1])
    n_border_color = ListProperty([0.5, 1, 1, 1])
    border_width = NumericProperty(2)
    allow_edit = BooleanProperty(True)
    touch_tol = NumericProperty(10)
    angle = BoundedNumericProperty(0, min=0, max=360, errorvalue=0)
    c_border_points = ListProperty([])
    n_border_points = ListProperty([])
    is_expanding = BooleanProperty(False)
    shape_type = StringProperty("")
    scale_factor = ListProperty([1, 1])
    translate_factor = ListProperty([1,1])

    rotate_obj = ObjectProperty(None, allownone=True)
    scale = ObjectProperty(None, allownone=True)
    translate = ObjectProperty(None, allownone=True)
    def __init__(self, **kwargs) -> None:
        self.index = None
        self.rotation_angles = []
        self.previous_states = []
        ## prevent overscaling when Morph is selected
        self._first_morph_selection = True

    def on_angle(self, instance, value):
        if value >= 360:
            angle = 0

    def rotate(self, instance, value, *args):
        """
        Rotate the shape: angle is in degrees

        """
        if instance.mode =="Rotate":
            self._first_morph_selection = True
            self.angle = value
            if self.rotate_obj is not None:
                self.rotate_obj.angle = value
        else:
            return

    def expand(self, instance, ratio, *args):
        if instance.mode == "Morph":
            if self._first_morph_selection:
                ratio = 1
                self._first_morph_selection = False
            self.scale_factor = [ratio, ratio]
            if self.scale is not None:
                self.scale.x = ratio
                self.scale.y = ratio
        elif instance.mode == "Translate":
            self._first_morph_selection = True
            if instance.name == "slider_1":
                self.translate_factor[0] = ratio
                if self.translate is not None:
                    self.translate.x = ratio
            elif instance.name == "slider_2":
                self.translate_factor[1] = ratio
                if self.translate is not None:
                    self.translate.y = ratio

    def _draw_new_shape(self, angle, scale_factor, translate_factor, border_points):
        
        self.canvas.before.clear()
        self.canvas.after.clear()
        self.angle = angle
        self.scale_factor = scale_factor
        self.translate_factor = translate_factor
        self.n_border_points = border_points

        with self.canvas.before:
            PushMatrix()
            rotate = Rotate()
            rotate.origin = (self.center[0]-self.border_width, self.center[1] - self.border_width)
            rotate.angle = angle
            scale = Scale()
            scale.origin = (self.center[0]-self.border_width, self.center[1] - self.border_width)
            scale.x = scale_factor[0]
            scale.y = scale_factor[1]
            translate = Translate()
            translate.x = translate_factor[0]
            translate.y = translate_factor[1]
            color = Color(0,0,0,0)
            rect = Rectangle(pos=self.pos, size=self.size)
            color = Color(1, 0, 0.6)
            line = Line(points=border_points, width=self.border_width)
            ellipse = Ellipse(pos=self.pos, size=(self.size[0]/20, self.size[1]/20))
            self.rotate_obj = Rotate()
            self.rotate_obj.origin = (self.center[0]-self.border_width, self.center[1] - self.border_width)
            self.rotate_obj.angle = angle
            self.scale = Scale()
            self.scale.origin = (self.center[0]-self.border_width, self.center[1] - self.border_width)
            self.scale.x = self.scale_factor[0]
            self.scale.y = self.scale_factor[1]
            self.translate = Translate()
            self.translate.x = self.translate_factor[0]
            self.translate.y = self.translate_factor[1]
            color = Color(0,0,0,0)
            rect = Rectangle(pos=self.pos, size=self.size)
            color = Color(*self.n_border_color)
            ellipse = Ellipse(pos=self.pos, size=(self.size[0]/20, self.size[1]/20))
            line = Line(points=border_points, width=self.border_width)
            PopMatrix()    
  

    def migrate_to_next_shape(self, effect_type, *args):
        if effect_type not in ("Rotate", "Morph", "Translate", "Form Only"):
            raise Exception("effect type not registered!")
        self.previous_states.append([effect_type, sum(self.rotation_angles), self.scale_factor, self.translate_factor, self.n_border_points])

        self.rotation_angles.append(self.angle)
        next_angle = sum(self.rotation_angles)
        if next_angle >= 360:
            next_angle -= 360

        angle, scale_factor, translate_factor = next_angle, self.scale_factor, self.translate_factor
        target_border_points = self.n_border_points
        self._fixed = True
        self.check_shape_pos(1,1)
        self._draw_new_shape(angle, scale_factor, translate_factor, target_border_points)        


    def revert_to_previous_shape(self, *args):
        if len(self.previous_states) == 0:
            return
        previous_state = self.previous_states[-1]
        previous_state[-2] = (0,0)
        self.previous_states.pop()
        self.rotation_angles.pop()
        if len(self.previous_states) == 0:
            self._fixed = False
        self._draw_new_shape(*previous_state[1::])


    def check_shape_pos(self, effect_type, value):
        """
        Checks where the shape ends up, 
        if out of bounds, returns False
            else: returns True
        
        """
        print(self.pos)
        print(self.parent.width, self.parent.height)


class ChoreoRect(DragAndResizeRect, ChoreoBase):
    shape_type = StringProperty("Rectangle")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        Clock.schedule_once(self.initialize, 1)

    def on_pos(self, instance, value):
        self.redraw_n_line()
        self.redraw_c_line()
        self.pos = value
        self.expansion_ratio = 1

    def on_size(self, instance, value):
        self.redraw_n_line()
        self.redraw_c_line()
        self.size = value
        self.fill_color = [0,0,0,0]

    def initialize(self, *args):
        self.n_border_points = [self.x-self.border_width, self.y-self.border_width, 
                                self.x+self.width-self.border_width, self.y-self.border_width,
                                self.x+self.width-self.border_width, self.y+self.height-self.border_width,
                                self.x-self.border_width, self.y+self.height-self.border_width, 
                                self.x-self.border_width, self.y-self.border_width]
   
    def redraw_c_line(self, *args):
        self.c_border_points = [self.x-self.border_width, 
                                self.y-self.border_width, 
                                self.x-self.border_width + self.width, self.y-self.border_width, 
                                self.x+self.width-self.border_width, self.y + self.height-self.border_width, self.x-self.border_width, self.y + self.height-self.border_width, 
                                self.x-self.border_width, 
                                self.y-self.border_width]


    def redraw_n_line(self, *args):
        self.n_border_points = [self.x-self.border_width, self.y-self.border_width, 
                                self.x+self.width-self.border_width, self.y-self.border_width,
                                self.x+self.width-self.border_width, self.y+self.height-self.border_width,
                                self.x-self.border_width, self.y+self.height-self.border_width, 
                                self.x-self.border_width, self.y-self.border_width]
    

class ChoreoPolygon(DragAndResizePolygon, ChoreoBase):
    
    
    shape_type = StringProperty("Polygon")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pos(self, instance, value, *args):
        self.pos = value
        self.draw_border()
        if not self.is_expanding:
            self.draw_n_border()
        self.fill_color = [0,0,0,0]

    def on_size(self, instance, value):
        self.size = value
        self.draw_border()
        if not self.is_expanding:
            self.draw_n_border()

    def draw_n_border(self, *args):
        points = []
        angle_step = (pi * 2) / float(self.segments)
        segments = int(self.segments)
        for i in range(segments) :
            x = self.x + (1 + cos((angle_step * i) + pi/2)) * (self.width/2)
            y = self.y + (1 + sin((angle_step * i) + pi/2)) * (self.height/2)
            points.extend([x, y])
        points.extend([points[0], points[1]])
        self.n_border_points = points



class ChoreoTriangle(DragAndResizeTriangle, ChoreoBase):
    shape_type = StringProperty("Triangle")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_angle(self, instance, value):
        if value >= 360:
            self.angle = 0

    def on_pos(self, instance, value):
        self.pos = value
        self.draw_triangle()
        n_border_points = self.triangle_points + self.triangle_points[0:2]
        self.n_border_points = n_border_points

    def on_size(self, instance, value):
        self.size = value
        self.draw_triangle()
        n_border_points = self.triangle_points + self.triangle_points[0:2]
        self.n_border_points = n_border_points

 

class AnimationPanel(TreeView):

    """
    TreeView for Shapes and Effects
    
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_options = {'text': 'Choreography',
                              'font_size': 15}
        self.canvas_manager = None    
        Clock.schedule_once(partial(self.add_shape, "Rectangle", -1), 6)
        Clock.schedule_once(partial(self.add_effect, "Translate", -1), 6)
        Clock.schedule_once(partial(self.add_effect, "Morph", -1), 7)
        Clock.schedule_once(partial(self.add_effect, "Form Only", -1), 8)
        Clock.schedule_once(partial(self.add_effect, "Rotate", -1), 9)

        self.nodes = []
        self.selected_node_index_from_touch = None


    def add_shape(self, shape_type, *args):
        shape_node = ShapeNode()
        shape_node.shape_type = shape_type
        shape_node.text = shape_type
        self.add_node(shape_node) 
        self.nodes.append(shape_node)

    def add_effect(self, effect_type, *args):
        effect_node = EffectNode()
        effect_node.effect_type = effect_type
        node_index = self.selected_node_index_from_touch
        if node_index is None:
            node_index = -1
        node = self.nodes[node_index]

        self.add_node(effect_node, node)
        pass

    def on_selected_node(self, panel, instance):
        print(instance)
        for index, node in enumerate(self.nodes):
            if node == instance:
                self.selected_node_index_from_touch = index
                break


    def remove_node(self, node_index=-1):
        pass



class EffectNode(TreeViewNode, BoxLayout):
    EFFECT_TYPES = ("Rotate", "Morph", "Translate", "Form Only")

    effect_type = StringProperty("")
    start_delay = NumericProperty(2)
    effect_duration = NumericProperty(2)
    outline_color = [0, 0.5, 0.5, 1]
    bkg_color = [0, 0.3, 0.3]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def on_effect_type(self, instance, value):
        print("effect updated", value)
        if value not in self.EFFECT_TYPES:
            return
        elif value == "Rotate":
            self.bkg_color = [0, 0.6, 0.6]
            self.outline_color = [0, 0.5, 0.5, 1]
        elif value == "Morph":
            self.bkg_color = [0, 0.5, 0.5]
            self.outline_color = [0, 0.3, 0.3, 1]


    def on_effect_duration(self, instance, value):
        if value == '' or float(value) < 0:
            InformationPopup(_message="Value not valid!!", _type='e').open()

    def on_start_delay(self, instance, value):
        if value == '' or float(value) < 0:
            InformationPopup(_message="Value not valid!!", _type='e').open()

    def get_properties(self, *args):
        return { "type": self.effect_type, 
                 "start_delay": self.start_delay,
                 "duration": self.effect_duration
               }


class ShapeNode(TreeViewLabel):
    shape_type = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_properties(self, *args):
        return {"type": self._type}




