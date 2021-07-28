from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.graphics import Color, Ellipse, Line
from kivy.config import Config
from gui.simulation import BunnyShape
import math  

# Globals
widget_ids = None
simulation_live = False
popup_widget_ids = None
robot_canvas_ref = None
custom_mode_on = False
current_shape_points = []
floor_dimensions_meters = (10, 10) # Default
floor_dimensions_pixels = ()

class RobotVisualization(App):
    """
    RobotVisualization Class
    This is where we instatiate the GUI
    Main controls
    """
    popupWindow = Popup(title="Draw a new shape")
    initPopupWindow = Popup(title="Initialize GUI Dimensions", size_hint=(None, None), size=(600,400))

    def build(self):
        # Wait till the gui inits to pull in the IDs
        Config.set('graphics', 'resizable', False)
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
            # Return to initial position
            widget_ids['robots'].robot_pos1 = (267, 0)
            widget_ids['robots'].robot_pos2 = (267, 0)
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


class RobotCanvas(RobotVisualization, BoxLayout):
    """
    Class RobotCanvas
    Used to initalize and display the robots
    """

    terminate_execution = False # Termination flag
    robot_pos = ObjectProperty(None) # Property ref from kv file
    # Default values for sim
    v_1 = [0, 0]
    v_2 = [0, 0]
    left_margin = Window.width / 5

    def __init__(self, **kwargs):
        super(RobotCanvas, self).__init__(**kwargs)
        global robot_canvas_ref
        global floor_dimensions_pixels 
        robot_canvas_ref = self
        floor_dimensions_pixels = (Window.width - self.left_margin, Window.height)
        # Create a dict for bunny shapes

    def draw_shape_points(self):
        d = 30
        global current_shape_points
        with self.canvas:
            Color(1.,0,0)
            for i,p in enumerate(current_shape_points):
                Ellipse(pos=(p.pos[0] +  - d / 2 + self.left_margin/2, p.pos[1] - d / 2), size=(d, d))
                if(i == len(current_shape_points) - 1):
                    Line(points=((p.pos[0] + self.left_margin/2, p.pos[1]), (current_shape_points[0].pos[0] + self.left_margin/2, current_shape_points[0].pos[1])), width = 5)
                else:
                    Line(points=((p.pos[0] + self.left_margin/2, p.pos[1]), (current_shape_points[i + 1].pos[0] + self.left_margin/2, current_shape_points[i+1].pos[1])), width = 5)

    def update_robots(self):
        """
        Updates the robot prosition on the canvas
        """
        robots = widget_ids['robots'] # Reference to the robot widgits
        w = Window.width - self.width
        # Right now I'm manually doing the addition. Will need to improve 
        if(robots.robot_pos1[0] > Window.width - 50 or robots.robot_pos1[0] < w):
            self.v_1[0] *= -1
        if(robots.robot_pos1[1] > Window.height - 50 or robots.robot_pos1[1] < 0):
            self.v_1[1] *= -1

        robots.robot_pos1[0] += self.v_1[0]
        robots.robot_pos1[1] += self.v_1[1]

        if(robots.robot_pos2[0] > Window.width - 50 or robots.robot_pos2[0] < w):
            self.v_2[0] *= -1
        if(robots.robot_pos2[1] > Window.height - 50 or robots.robot_pos2[1] < 0):
            self.v_2[1] *= -1

        robots.robot_pos2[0] += self.v_2[0]
        robots.robot_pos2[1] += self.v_2[1]

    def init_robots(self, dt):
        """
        Sets up the robots velocities and bounds
        """
        robots = widget_ids['robots']
        w = Window.width - self.width
        self.v_1 = [7, -4]
        self.v_2 = [-5, 8]

        robots.robot_pos1 = [w, 0]
        robots.robot_pos2 = [w, 0]

        # Create a schedule to update the robots pos
        Clock.schedule_interval(self.update, 1.0 / 60.0)        

    def update(self, dt):
        """
        Calls the update robot function if the widgets are visible
        """
        if(simulation_live == False):
            return False# Kill this update thread
        if(widget_ids != None):
            self.update_robots()

    def call_my_name(self):
        print("RobotCanvas!")

class DrawPopup(RobotVisualization, GridLayout):
    shape_points = []
    shape_lines = []
    triangle = ((500,300), (1100, 300), (800, 900))
    square = ((500,300), (1100, 300), (1100, 900), (500, 900))

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
            Color(0,1,0)
            d=20
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


class InitializePopup(RobotVisualization, GridLayout):
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
    _root = ObjectProperty()

    def __init__(self, **kwargs):
        super(Toolbar, self).__init__(**kwargs)
        self.file_drop_down = DropDown()
        self.file_drop_down.add_widget(Button)

    def show_file_menu(self, file_button):
        canvas_pos = self._root.ids.robots.pos
        max_width = self._root.ids.robots.width
        max_height = self._root.ids.robots.height
        print(canvas_pos, max_width, max_height)

    def show_view_menu(self, view_button):
        print("View has been pressed")

    def show_bunny_menu(self, bunny_button):
        print("Bunny has been pressed")

    def show_simulation_menu(self, simulation_button):
        print("Simulation has been pressed")




