
import random

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line
from kivy.uix.button import Button
from kivy.lang import Builder
from utils import InformationPopup
from communication.network import WirelessNetwork
from custom_widgets.status_bar_widget.status_bar_widget import StatusBarWidget
from custom_widgets.bunny_widget.bunny_widget import BunnyWidget
from custom_widgets.radio_dongle_widget.radio_dongle_widget import RadioDongleWidget
import math
from core.constants import Constants as Cons
from pathlib import Path
from functools import partial


def load_kv_files():
    custom_widgets_dir_path = Path("custom_widgets")
    
    Builder.load_file(str(custom_widgets_dir_path / "bunny_widget" / "bunnywidget.kv"))
    Builder.load_file(str(custom_widgets_dir_path / "status_bar_widget" / "statusbarwidget.kv"))
    Builder.load_file(str(custom_widgets_dir_path / "radio_dongle_widget" / "radiodonglewidget.kv"))


load_kv_files()


class SwarmGUI(App):
    """
    RobotVisualization Class
    This is where we instantiate the GUI
    Main controls
    """


class RobotCanvas(FloatLayout):
    """
    Class RobotCanvas
    Used to initalize and display the robots
    """  
    # Default values for sim
    current_point = None
    last_point = None
    shape_points = []
    shape_lines = []
    can_draw_more = True
    custom_mode_on = False
    triangle_custom_mode_on = False

    triangle = ((500, 150), (800, 150), (650, 450))
    square = ((250, 150), (550, 150), (550, 450), (250, 450))

    def __init__(self, **kwargs):
        super(RobotCanvas, self).__init__(**kwargs)
        self.bind(pos=self._update_pos, size=self._update_size)
        self._minimum_coord = self.pos
        self._maximum_coord = (self.pos[0]+self.width, self.pos[1]+self.height)
        self._bunny_widgets = {}
        # force a pos update
        self.pos = (0 ,0)
        
        # for testing purposes
        Clock.schedule_once(partial(self.update_bunny_position, "bunny_1", {"x": 0.9, "y": 0.9}), 2)
        
        # add a Bunny
        self.add_bunny_widget(uid="bunny_1")
        # change the formation of the bunny to charge
        Clock.schedule_once(partial(self.update_bunny_state, "bunny_1", "charge"), 5)
        # rotate the bunny to 270 degrees
        Clock.schedule_once(partial(self.update_bunny_position, "bunny_1", {"theta": 270}), 7)


    def transmitter_position(self, pos):
        """
        sets the transmitter's position
        """
        pass
        


    def add_bunny_widget(self, uid):
        self._bunny_widgets[uid] = BunnyWidget(uid=uid)
        self.add_widget(self._bunny_widgets[uid])

    def update_bunny_position(self, bunny_uid, position: dict, *args):
        """
        :param  bunny_uid: id of bunny, e.g "bunny_1"
                position: a dict containing pos: e.g position = {"x": 500, "y": 760, "theta":45}
        raises KeyError if bunny is not present
        """
        bunny = self._bunny_widgets[bunny_uid]
        for key in position.keys():
            pass

    def update_bunny_state(self, bunny_uid, state: str, *args):
        """
        :param  bunny_uid: id of bunny, e.g "bunny_2"
                state - should be from {"idle", "formation", "charge", "roam"}
        raises KeyError if bunny is not present
        """
        self._bunny_widgets[bunny_uid]["state"] = state

    def _update_pos(self, instance, pos):
        self.pos = pos
        self._minimum_coord = self.pos
        self._maximum_coord = (self.pos[0]+self.width, self.pos[1]+self.height)
        for bunny in self._bunny_widgets.values():
            bunny.pos_hint = {"center_x": 1.0, "center_y": 1.0}

    def _update_size(self, instance, size):
        self.size = size

    def draw_premade_shape(self, name, root):
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
        root.ids["choreography"].reverse_menu_state(root)

    def custom_mode(self, root):
        root.ids["custom"].disabled = True
        root.ids["square"].disabled = True
        root.ids["triangle"].disabled = True
        root.ids["custom_triangle"].disabled = True
        root.ids["clear"].disabled = False
        self.custom_mode_on = True

    def triangle_custom_mode(self,root):
        root.ids["custom"].disabled = True
        root.ids["square"].disabled = True
        root.ids["triangle"].disabled = True
        root.ids["custom_triangle"].disabled = True
        root.ids["clear"].disabled = False
        self.triangle_custom_mode_on = True
        self.custom_mode_on = True

    def clear_canvas(self,root):
        with self.canvas:
            for e in self.shape_points:
                self.canvas.remove(e)
                self.shape_points = []
            for l in self.shape_lines:
                self.canvas.remove(l)
                self.shape_lines = []
        root.ids["choreography"].reverse_menu_state(root)
        self.custom_mode_on = False
        self.triangle_custom_mode_on = False
        self.can_draw_more = True

    def on_touch_down(self, touch):
        if(self.can_draw_more and self.custom_mode_on and touch.y < 995): # Don't like this being hardcoded. Fix
            with self.canvas:
                Color(1, 0 ,1)
                d = 15
                # Connect the start if we are close enough
                if(len(self.shape_points) > 2 and math.isclose(touch.x, self.shape_points[0].pos[0], abs_tol = 100) and math.isclose(touch.y, self.shape_points[0].pos[1], abs_tol = 100)):
                        l = Line(points=((self.current_point.pos[0] + d / 2, self.current_point.pos[1] + d / 2),
                            (self.shape_points[0].pos[0] + d / 2, self.shape_points[0].pos[1] + d / 2)))
                        self.shape_lines.append(l)
                        self.can_draw_more = False
                        if(self.triangle_custom_mode_on):
                            area = self.calculate_triangle_area()
                            if(area <= 20000):
                                self.notify_bad_shape()
                else:
                # Draw a new point
                    if(self.triangle_custom_mode_on and len(self.shape_points) == 3):
                            return
                    else:
                        e = Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
                        self.shape_points.append(e)
                        self.last_point = self.current_point
                        self.current_point = e

                        # If we have more than two. Connect to the last point.
                        if(len(self.shape_points) >= 2):
                            l = Line(points=((self.last_point.pos[0] + d / 2, self.last_point.pos[1] + d / 2),
                            (self.current_point.pos[0] + d / 2, self.current_point.pos[1] + d / 2)))
                            self.shape_lines.append(l)   
    
    def calculate_triangle_area(self):
        p1 = self.shape_points[0].pos
        p2 = self.shape_points[1].pos
        p3 = self.shape_points[2].pos
        area = (1/2) * abs((p1[0]*(p2[1]-p3[1])) + (p2[0]*(p3[1]-p1[1])) + (p3[0]*(p1[1]-p2[1])))
        return area
    
    def notify_bad_shape(self):
        #self.clear_canvas(self.parent.root)
        InformationPopup(_type="e", _message="Triangle size too small").open()


class Choreography(BoxLayout):
    def __init__(self, **kwargs):
        super(Choreography, self).__init__(**kwargs)

    def reverse_menu_state(self, root):
        root.ids['custom'].disabled = not root.ids['custom'].disabled
        root.ids['custom_triangle'].disabled = not root.ids['custom_triangle'].disabled
        root.ids['square'].disabled = not root.ids['square'].disabled
        root.ids['triangle'].disabled = not root.ids['triangle'].disabled
        root.ids['clear'].disabled = not root.ids['clear'].disabled


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
    pass
