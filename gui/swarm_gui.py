import random
from keyboard import on_press
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line
from kivy.graphics.instructions import InstructionGroup
from kivy.uix.button import Button
from kivy.lang import Builder
from utils import InformationPopup
from communication.network import WirelessNetwork
from custom_widgets.custom_widgets import *
import math
from core.constants import Constants as Cons
from pathlib import Path
from functools import partial


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
    background_color = ListProperty([1, 1, 0, 0])

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
        self.drop_down = None
        # force a pos update
        self.pos = (0 ,0)
        # for testing purposes
        # add a Bunny
        self.add_bunny_widget(bunny_uid="bunny_1")
        # change the formation of the bunny to charge
        #Clock.schedule_once(partial(self.update_bunny_state, "bunny_1", "charge"), 1)
        # rotate the bunny to 270 degrees
        Clock.schedule_interval(partial(self.update_bunny_rotation, 
                                        "bunny_1", 
                                         45), 25)
        Clock.schedule_once(self.add_draggable_and_resizable_rect, 4)

        
        # grids
        self.add_grid = True
        self.gridline_widget = self.add_gridlines() if self.add_grid else None 

    def _update_pos(self, instance, pos):
        self.pos = pos
        self._minimum_coord = self.pos
        self._maximum_coord = (self.pos[0]+self.width, self.pos[1]+self.height)
        if self.gridline_widget is not None:
            self.gridline_widget.update_grid()


    def _update_size(self, instance, size):
        self.size = size


    def add_drop_down_menu(self, *args) -> DropDown:
        # create a dropdown
        dropdown = DropDownWidget()
        
        # add buttons to it
        grid_settings_button = Button(text="Grid Settings")        
        grid_settings_button.bind(on_press=self.show_grid_settings)
        dropdown.add_widget(grid_settings_button)

        scale_settings_button = Button(text="Scale Settings")
        scale_settings_button.bind(on_press=self.show_scale_settings)
        dropdown.add_widget(scale_settings_button)


        self.add_widget(dropdown)
        self.drop_down = dropdown
        return dropdown

    def show_scale_settings(self, *args):
        pass


    ## Gridlines methods
    def add_gridlines(self):
        grid_line_widget = GridWidget()
        grid_line_widget.pos_hint = {"x":0, "y":0}
        grid_line_widget.size_hint = (1, 1)
        self.add_widget(grid_line_widget)
        return grid_line_widget

    def remove_gridlines(self):
        self.remove_widget(self.gridline_widget)


    def show_grid_settings(self, *args):
        # working on it!!
        print("Hello") 


    ## Bunny methods
    
    def add_bunny_widget(self, bunny_uid, **kwargs):
        """
        Add a Bunny Widget 
        (Optional)
        :param - "size_hint" : size_hint for widget, 
                               default (0.05, 0.05)
        "param - "pos_hint"  : pos_hint for widget, default  
                               {"center_x:0.5", "center_y:0.5"}
        :param - "state"     : state for widget (taken for CONSTANT.STATES) 
                               default idle
        :param - "angle"     : angle for widget,
                               default 0
        """
        bunny = BunnyWidget(uid=bunny_uid)
        self._bunny_widgets[bunny_uid] = bunny
        bunny.size_hint = kwargs.get("size_hint", (0.05, 0.05))
        bunny.pos_hint = kwargs.get("pos_hint", {"center_x": 0.99, "center_y": 0.99 })
        bunny["state"] = kwargs.get("state", "idle")
        bunny["angle"] = kwargs.get("angle", 0)
        self.add_widget(bunny)

   
    def update_bunny_position(self, bunny_uid, position: dict, *args):
        """
        :param  bunny_uid: id of bunny, e.g "bunny_1"
                position: a dict containing pos_hint: e.g position = {"x": 0.5, "y": 1}
        raises KeyError if bunny is not present
        """
        bunny = self._bunny_widgets[bunny_uid]
        bunny.pos_hint = position
   

    def update_bunny_state(self, bunny_uid, state: str, *args):
        """
        :param  bunny_uid: id of bunny, e.g "bunny_2"
                state - should be from {"idle", "formation", "charge", "roam"}
        raises KeyError if bunny state is not right
        """
        self._bunny_widgets[bunny_uid]["state"] = state

    def update_bunny_rotation(self, bunny_uid: str, rotation_angle: float or int, *args):
        """
        :param bunny_uid: unique id of bunny
               rotation_angle: angle that bunny rotates to
        """
        self._bunny_widgets[bunny_uid]["angle"] = rotation_angle

    def add_draggable_and_resizable_rect(self, *args):
        """
        Adds a draggable and resizable rectangle widget to
        the canvas 
        """
        self.draggable_and_resizable_rect = DragAndResizeRect()
        self.draggable_and_resizable_rect.pos = self.pos
        self.draggable_and_resizable_rect.size = (0.5*self.size[0], 0.5*self.size[1])
        self.add_widget(self.draggable_and_resizable_rect)


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

        # sense a right click and keep track of the number of touches
        if self.collide_point(*touch.pos) and touch.button == 'right':
            if self.drop_down is None:
                touch.ud['robot_canvas_drop_down_touch'] = 'first_touch'
        elif self.drop_down is not None:
            touch.ud['robot_canvas_drop_down_touch'] = 'second_touch'

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
        return super(RobotCanvas, self).on_touch_down(touch)


    def on_touch_up(self, touch):
        
        if 'robot_canvas_drop_down_touch' in touch.ud.keys():
            if touch.ud['robot_canvas_drop_down_touch'] == 'first_touch':
                touch.ud["drop_down_widget"] = self.add_drop_down_menu()
                self.drop_down.size_hint = (0.1, 0.1)
                xx, yy = self.to_widget(*touch.pos, relative=True)
                self.drop_down.pos = (touch.pos[0], touch.pos[1] - self.drop_down.size[1])
                if self.width - xx < self.drop_down.width:
                    self.drop_down.x -= self.drop_down.width
                if yy - self.drop_down.height < 0:
                    self.drop_down.y += self.drop_down.height 
            elif touch.ud['robot_canvas_drop_down_touch'] == 'second_touch':
                self.remove_widget(self.drop_down)
                # del touch.ud["drop_down_widget"]
                self.drop_down = None
    
        return super().on_touch_up(touch)


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

class Environment(BoxLayout):
    scale_settings_boxlayout = ObjectProperty()
    scale_settings_label = ObjectProperty()
    scale_settings_gridlayout = ObjectProperty()
    
    def __init__(self, **kwargs):
        super(Environment, self).__init__(**kwargs)
        Clock.schedule_once(self.initialize, 0.5)

    def initialize(self, *args):
        # Label Background color
        self.scale_settings_gridlayout.bkg_color = [0.1, 0.1, 0.1, 1]



    def on_pos(self, instance, value):
        self.pos = value

    def on_size(self, instance, value):
        self.size = value

    

class StatusBoard(BoxLayout):
    scroll_view = ObjectProperty()
    
    def __init__(self, **kwargs):
        super(StatusBoard, self).__init__(**kwargs)
        Clock.schedule_once(partial(self.initialize_status_board), 2)


    def initialize_status_board(self, *args):
        self.add_bunny_action_bar("bunny_1")

    def update_board(self, children):
        pass

    def remove_widget(self, uid: str):
        pass

    def add_bunny_action_bar(self, bunny_uid: str):
        bunny = BunnyActionBar(uid=bunny_uid)
        self.scroll_view.add_widget(bunny)

    
    
    
