import random

import kivy.clock
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.graphics import Color, Ellipse, Line
from kivy.config import Config
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.image import Image
from kivy.uix.spinner import Spinner
from kivy.lang import Builder
from utils import InformationPopup
from gui.simulation import BunnyShape
from communication.network import WirelessNetwork
from custom_widgets.status_bar_widget.status_bar_widget import StatusBarWidget
from custom_widgets.bunny_widget.bunny_widget import BunnyWidget
from custom_widgets.radio_dongle_widget.radio_dongle_widget import RadioDongleWidget
import math
from core.constants import Constants as c

# Globals
widget_ids = None
simulation_live = False
popup_widget_ids = None
robot_canvas_ref = None
custom_mode_on = False
current_shape_points = []
floor_dimensions_meters = (10, 10)  # Default
floor_dimensions_pixels = ()


def load_kv_files():
    Builder.load_file("custom_widgets\\status_bar_widget\\statusbarwidget.kv")
    Builder.load_file("custom_widgets\\bunny_widget\\bunnywidget.kv")
    Builder.load_file("custom_widgets\\radio_dongle_widget\\radiodonglewidget.kv")


load_kv_files()


class SwarmGUI(App):
    """
    RobotVisualization Class
    This is where we instantiate the GUI
    Main controls
    """
    popupWindow = Popup(title="Draw a new shape")
    initPopupWindow = Popup(title="Initialize GUI Dimensions", size_hint=(None, None), size=(300,200))

    def build(self):

        # Wait till the gui inits to pull in the IDs
        Window.size = (800, 600)
        Clock.schedule_once(self.finish_init, 1)


    def start_stop_execution(self): 
        global simulation_live
        if(simulation_live == False):
            widget_ids['start_stop_button'].text = "Stop Simulation"
            global robot_canvas_ref
            robot_canvas_ref.init_robots(robot_canvas_ref)
            simulation_live = True
        else: 
            widget_ids['start_stop_button'].text = "Start"
            # Return to initial position.. Need to automate creation of robots
            widget_ids['robots'].robot_pos1 = (133, 0)
            widget_ids['robots'].robot_pos2 = (133, 0)
            simulation_live = False

    def finish_init(self, dt):
        # Not ideal solution. Ids are out of scope from our RobotCanvas class so setting them global
        global widget_ids
        widget_ids = self.root.ids

    def show_draw_popup(self):
        self.show = DrawPopup()
        self.popupWindow.content = self.show
        self.popupWindow.size = floor_dimensions_pixels
        self.popupWindow.size_hint = (None, None)
        self.popupWindow.open()

    def show_initialize_popup(self):
        self.show = InitializePopup()
        self.initPopupWindow.content = self.show
        self.initPopupWindow.open()

    def close_draw_popup(self):
        self.popupWindow.dismiss()
    
    def close_initialize_popup(self):
        self.initPopupWindow.dismiss()


class RobotCanvas(BoxLayout):
    """
    Class RobotCanvas
    Used to initialize and display the robots
    """
    def __init__(self, **kwargs):
        super(RobotCanvas, self).__init__(**kwargs)
        self.bind(pos=self._update_pos, size=self._update_size)
        # Create a dict for bunny shapes

    def _update_pos(self, instance, pos):
        self.pos = pos

    def _update_size(self, instance, size):
        self.size = size

    def add_robot(self):
        print(c.GUI_REFRESH_RATE)



class DrawPopup(GridLayout):
    shape_points = []
    shape_lines = []
    triangle = ((250,150), (550, 150), (400, 450))
    square = ((250,150), (550, 150), (550, 450), (250, 450))

    def __init__(self):
        super(DrawPopup, self).__init__()
        global popup_widget_ids
        popup_widget_ids = self.ids

    def set_custom(self):
        self.ids['custom'].disabled = True
        global custom_mode_on
        custom_mode_on = True

    def cancel_drawing(self):
        self.clear_canvas()
        self.close_draw_popup()

    def export_shape(self):
        robot_canvas_ref.draw_shape_points()
        self.close_draw_popup()

    def set_current_shape(self):
        global current_shape_points
        current_shape_points = self.shape_points
        self.ids['custom'].disabled = True
        self.ids['square'].disabled = True
        self.ids['triangle'].disabled = True
        self.ids['export'].disabled = False
        self.ids['clear'].disabled = False

    def draw_premade_shape(self, name):
        if (name == "triangle"):
                shape = self.triangle
        elif(name == "square"):
                shape = self.square

        with self.canvas:
            Color(0, 1, 0)
            d = 20
            for i,p in enumerate(shape):
                e = Ellipse(pos=(p[0], p[1]), size=(d, d))
                self.shape_points.append(e)
                if(i == len(shape) - 1):
                    line = Line(points=((p[0] + d/2, p[1] + d/2), (shape[0][0] + d/2, shape[0][1] + d/2)))
                    self.shape_lines.append(line)
                else:
                    line = Line(points=((shape[i][0] + d/2, shape[i][1] + d/2), 
                                  (shape[i + 1][0] + d/2, shape[i + 1][1] + d/2)))
                    self.shape_lines.append(line)
        self.set_current_shape()

    def clear_canvas(self):
        global current_shape_points
        with self.canvas:
            for e in self.shape_points:
                self.canvas.remove(e)
                self.shape_points = []
            for l in self.shape_lines:
                self.canvas.remove(l)
                self.shape_lines = []
        current_shape_points = []
        self.ids['custom'].disabled = False
        self.ids['square'].disabled = False
        self.ids['triangle'].disabled = False
        self.ids['export'].disabled = True
        self.ids['clear'].disabled = True


class ShapeCanvas(BoxLayout):
    all_points = []
    current_point = None
    last_point = None
    can_draw_more = True

    def on_touch_down(self, touch):
        global custom_mode_on
        if(self.can_draw_more and custom_mode_on and touch.y < 995): # Don't like this being hardcoded. Fix
            with self.canvas:
                d = 15
                # Connect the start if we are close enough
                if(len(self.all_points) > 2 and math.isclose(touch.x, self.all_points[0].pos[0], abs_tol = 100) and math.isclose(touch.y, self.all_points[0].pos[1], abs_tol = 100)):
                        Line(points=((self.current_point.pos[0] + d / 2, self.current_point.pos[1] + d / 2),
                            (self.all_points[0].pos[0] + d / 2, self.all_points[0].pos[1] + d / 2)))
                        self.can_draw_more = False
                        global popup_widget_ids
                        popup_widget_ids['export'].disabled = False
                        global current_shape_points
                        current_shape_points = self.all_points
                else:
                # Draw a new point
                    e = Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
                    self.all_points.append(e)
                    self.last_point = self.current_point
                    self.current_point = e

                    # If we have more than two. Connect to the last point.
                    if(len(self.all_points) >= 2):
                        Line(points=((self.last_point.pos[0] + d / 2, self.last_point.pos[1] + d / 2),
                        (self.current_point.pos[0] + d / 2, self.current_point.pos[1] + d / 2)))


class InitializePopup(GridLayout):
    def __init__(self):
        super(InitializePopup, self).__init__()

    def set_new_dimensions(self):
        x = self.ids['x_input'].text
        y = self.ids['y_input'].text
        if(x and y):
            global floor_dimensions_meters
            floor_dimensions_meters = (x, y)
            self.close_initialize_popup()
        else:
            print("Invalid Dimensions")


class Toolbar(BoxLayout):
    """
    Toolbar Layout: needs to be completed
    left as a template for now
    """
    _root = ObjectProperty()

    def __init__(self, **kwargs):
        super(Toolbar, self).__init__(**kwargs)
        self._drop_down_buttons = {}
        # Create 4 drop down menus
        self._file_drop_down = DropDown()
        self._view_drop_down = DropDown()
        self._bunny_drop_down = DropDown()
        self._simulation_drop_down = DropDown()
        # Create the file menu buttons and add callback
        # leaving this blank for now

        # Create the view menu buttons and add callback
        # show bunny logs button
        show_bunny_logs_button = Button(text='show bunny logs',
                                        size_hint=(1, 1),
                                        height=50)
        show_bunny_logs_button.bind(on_release=self._show_bunny_logs)
        self._drop_down_buttons['show_bunny_logs'] = show_bunny_logs_button
        # add buttons to dropdown
        self._view_drop_down.add_widget(show_bunny_logs_button)

        # Create the bunny menu buttons and add callback
        # add bunny to simulation
        add_bunny_button = Button(text='add bunny',
                                  size_hint=(1, 1),
                                  height=50)
        add_bunny_button.bind(on_release=self._add_bunny_to_canvas)
        self._drop_down_buttons['add_bunny'] = add_bunny_button
        # add buttons to the dropdown menu
        self._bunny_drop_down.add_widget(add_bunny_button)

        # Create the simulation menu buttons and add callback
        # start simulation
        start_simulation_button = Button(text='Start Simulation',
                                         size_hint=(1, 1),
                                         height=50)
        start_simulation_button.bind(on_release=self._start_simulation)
        self._drop_down_buttons['start_simulation'] = start_simulation_button
        # add buttons to dropdown menu
        self._simulation_drop_down.add_widget(start_simulation_button)

    def _show_bunny_logs(self):
        """
        called when 'show bunny logs' button is pressed
        :return: None
        """
        pass

    def _add_bunny_to_canvas(self):
        """
        called when 'add bunny' button is pressed
        :return: None
        """
    def _start_simulation(self):
        """
        Starts the simulation
        :return:None
        """
        pass

    def show_file_menu(self, file_button):
        canvas_pos = self._root.ids.robots.pos
        max_width = self._root.ids.robots.width
        max_height = self._root.ids.robots.height
        print("canvas pos:",
              canvas_pos, "width:",
              max_width, "height:",
              max_height)

    def show_view_menu(self, view_button):
        # keep it blank for now
        pass

    def show_bunny_menu(self, bunny_button):
        # keep it blank for now
        pass

    def show_simulation_menu(self, simulation_button):
        # keep it blank for now
        pass


class Connections(BoxLayout, WirelessNetwork):
    connect_button = ObjectProperty()
    search_button = ObjectProperty()
    wifi_image = ObjectProperty()
    search_and_connect_box = ObjectProperty()
    radio_selection = ObjectProperty()

    def __init__(self, **kwargs):
        super(Connections, self).__init__(**kwargs)
        self._radio_dongle = self.search_for_radio_dongle()
        self._wifi_image_sources = {"on": "images\\wifi\\wifi_on.png",
                                    "off": "images\\wifi\\wifi_off.png"}
        self._selected_radio_dongle = None

    def search_button_press(self):
        self.search_button.text = "[b][i]Searching...[/i][/b]"

    def update_radio_dongle_selection(self, selected_radio):
        print(selected_radio)
        self._selected_radio_dongle = selected_radio

    def connect_button_press(self):
        if self._selected_radio_dongle is None:
            InformationPopup(_type="e",
                             _message="No radio selected or available").open()
            return
        self.wifi_image.source = self._wifi_image_sources["on"]

