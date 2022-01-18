from typing import List
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
from utils import InformationPopup
from pathlib import Path
from kivy.uix.behaviors import DragBehavior, button
from kivy.animation import Animation
from kivy.properties import ObjectProperty, StringProperty, BoundedNumericProperty, \
    ReferenceListProperty, ListProperty, NumericProperty, BooleanProperty, DictProperty
from kivy.uix.actionbar import ActionBar, ActionItem
from core.constants import Constants as Cons
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, InstructionGroup, Line, Point, Rectangle
from kivy.core.window import Window
from kivy.lang import Builder
import random
from math import pi, cos, sin
import numpy as np
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
    _angle = NumericProperty(0)

    def __init__(self, uid, **kwargs):
        super(BunnyWidget, self).__init__(**kwargs)
        self._IMAGE_PATH = "atlas://custom_widgets/images/bunny_widget/bunny_widget"
        self._id = uid

    # state callback
    def on__state(self, instance, value):
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
                self._state = value
        elif key == "angle":
            anim = Animation(_angle=value, duration=2)
            anim.start(self)
    
    def __sub__(self, other):
        if type(other) == type(self):
            return (self.pos[0] - other.pos[0], self.pos[1] - other.pos[1])
        



    @property
    def id(self):
        return self._id



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
    _border_width = NumericProperty(4)
    _draw_border = BooleanProperty(True)
    _fill_color = ListProperty([1, 0, 1, 1])
    _border_color = ListProperty([0, 0, 1, 1])
    _edit_mode = StringProperty("")
    
    def __init__(self, **kwargs):
        super(DragAndResizeRect, self).__init__(**kwargs)
        self.constrain_to_parent_window = True
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


class DragAndResizePolygon(DragBehavior, Widget):
    fill_color = ListProperty([0, 1, 1, 1])
    border_color = ListProperty([1, 1, 1, 1])
    line_points = ListProperty([])
    segments = NumericProperty(100)
    rot_angle = BoundedNumericProperty(0, min=0, max=360, errorvalue=0)

    def __init__(self, **kwargs):
        super(DragAndResizePolygon, self).__init__(**kwargs)
        self.constrain_to_parent_window = True
        self.segments = kwargs.get("segments", 100)
        self.size_hint = (None, None)
        self.shape_settings = None

    def update_property(self, property, value):
        setattr(self, property, value)

    def on_pos(self, instance, value):
        self.pos = value
        self.draw_border()

    def on_size(self, instance, value):
        self.size = value
        self.draw_border()


    def draw_border(self):
        points = []
        angle_step = (pi * 2) / float(self.segments)
        for i in range(self.segments):
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

    def check_touch_pos(self, touch):
        "not completed!!"
        """
        Checks whether touch.pos is inside the displayed shape
        touch.pos is reflected onto the first quadrant
        """
        xs = self.line_points[0:len(self.line_points)//4:2]
        ys = self.line_points[1:len(self.line_points)//4:2]
        touch_pos_array = np.array([*touch.pos])
        if touch.x >= self.width/2 and touch.y >= self.height/2:
            if touch.x < max(xs) and touch.y < max(ys):
                return True
            else:
                return False
        if touch.x < self.width/2 and touch.y >= self.height/2:
            pass

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super(DragAndResizePolygon, self).on_touch_up(touch)
        else:
            self.check_touch_pos(touch)
        return super().on_touch_down(touch)


class GridWidget(Widget):
    grid_color = ListProperty([0.5, 0.2, 1, 1])
    grid_line_thickness = NumericProperty(1)
    grid_scale = DictProperty({"1m": 100})            # 1m represented by 100 pixels     
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
        
        min_pixel = self.grid_scale["1m"]
        # x axis
        # Adding 15 grid lines
        line_wp_distance = self.width  //self.MAX_GRIDLINES
        line_hp_distance = self.height //self.MAX_GRIDLINES
        

        for x_pos in range(0, int(self.width), line_wp_distance):
            if x_pos > self.height:
                continue
            color = Color(*self.grid_color)
            line = Line(points=(self.x+ x_pos, self.y, self.x + x_pos, self.y+self.height))
            self.vertical_lines.append((color, line))
            self.lines.add(color)
            self.lines.add(line)

        for y_pos in range(0, int(self.height), line_hp_distance):
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
        SET GRIDLINES TO always show 15m i.e 15 lines on one axis
        1 line represents 1 m
        """
        line_wp_distance = self.width //self.MAX_GRIDLINES
        line_hp_distance = (self.height) // self.MAX_GRIDLINES

        for line_num, (color, line) in enumerate(self.vertical_lines):
            if (line_num+1)*line_wp_distance > self.width:
                self.lines.remove(color)
                self.lines.remove(line)
                self.vertical_lines.remove((color, line))
                continue
            line.points = ((line_num+1)*line_wp_distance + self.x, 
                           self.y, 
                           (line_num+1)*line_wp_distance + self.x,
                           self.y+self.height)


        for line_num, (color, line) in enumerate(self.horizontal_lines):
            if (line_num+1)*line_hp_distance > self.height:
                self.lines.remove(color)
                self.lines.remove(line)
                self.horizontal_lines.remove((color, line))
                continue
            line.points = (self.x, 
                           self.y+(line_num+1)*line_hp_distance, 
                           self.x+self.width,
                           self.y+(line_num+1)*line_hp_distance)
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
        for pos, (color_x, line_x) in enumerate(self.vertical_lines):
            points = line_x.points[2::]
            label = Label(text=f"{(pos+1)} m")
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

    _width_label = ObjectProperty()
    _width_text_input = ObjectProperty()
    _height_label = ObjectProperty()
    _height_text_input = ObjectProperty()
    _unit_label = ObjectProperty()
    _unit_spinner = ObjectProperty()
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
        Clock.schedule_once(self.initialize, 0.1)
        self.shape_properties = {}
        self.shape_canvas = None

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
        self._unit_spinner.bind(text=self.set_unit)
        self._width_text_input.bind(text=self.set_width)
        self._height_text_input.bind(text=self.set_height)
        self._lock_position_checkbox.bind(active=self.set_lock_pos)
        self._lock_size_checkbox.bind(active=self.set_lock_size)
        self._place_button.bind(on_release=self.place_shape)
        self._new_button.bind(on_release=self.new_shape)
        self._remove_button.bind(on_release=self.remove_shape)


        self._shape_fill_color = [0, 0, 0, 0]
        self._shape_border_color = [0, 0, 0, 0]
        self.shape_properties["width"] = 0
        self.shape_properties["height"] = 0
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

    def set_width(self, instance, value):
        if value == '':
            value = 0
        self.shape_properties["width"] = float(value)

    def set_height(self, instance, value):
        if value == '':
            value = 0
        self.shape_properties["height"] = float(value)

    def set_unit(self, instance, value):
        self.shape_properties["unit"] = str(value)

    def set_type(self, instance, value):
        self.shape_properties["type"] = str(value)

    def set_lock_pos(self, instance, value):
        self.shape_properties["lock_pos"] = bool(value)

    def set_lock_size(self, instance, value):
        value = bool(value)
        self._width_text_input.readonly = value
        self._height_text_input.readonly = value
        self.shape_properties["lock_size"] = value

    def add_num_segments(self, instance, value):
        self.shape_properties["segments"] = value

    def new_shape(self, instance):
        print(self.shape_properties)

    #======== Callbacks to Robot Canvas =======#

    def place_shape(self, instance):
        if self.shape_canvas.add_shape(self.shape_properties):
            self._place_button.disabled = True
            
    def remove_shape(self, instance):
        if not self._place_button.disabled:
            InformationPopup(_type="e", _message="Shape has not been placed!").open()

    def update_property(self, property, value):
        if property.lower() == "height":
            self._height_text_input.text = value

        elif property.lower() == "width":
            self._width_text_input.text = value

    #===============================================#
    #===============================================#




    







    




