import enum
import time
import random
import struct
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line
from kivy.graphics.instructions import InstructionGroup
from kivy.uix.button import Button
from kivy.lang import Builder
from control.PathPlanner import PathPlanner, VelocityHandler
from control.shape_formation import ShapeFormation
from utils import InformationPopup
from custom_widgets.custom_widgets import *
import math
from core.constants import Constants as Cons
from pathlib import Path
from functools import partial
from communication.network_manager import NetworkManager


class SwarmGUI(App):
    """
    RobotVisualization Class
    This is where we instantiate the GUI
    Main controls
    """
    constants = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def build(self):
        self.constants = Cons()

class CanvasManager(Widget):
    """
    Manages the widgets on the canvas
    """
    def __init__(self, widget, **kwargs) -> None:
        super().__init__(**kwargs)
        self._parent = widget
        self._canvas = widget.canvas
        self._shapes = []
        self._bunny_widgets = {}
        self._choreo_shapes = []
        self._active_widget = None
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        Window.bind(on_motion=self.on_window_motion)
        self._canvas_scale = None
        # Clock.schedule_once(partial(self.add_choreo_shape, "rect", self), 5)
        self.vel_handler = VelocityHandler()
        #Clock.schedule_once(self.add_bunny, 5)
        #Clock.schedule_once(self.rotate_robots, 7)

    def add_bunny(self, *args):
        # self.add_bunny_widget(bunny_uid="LGN02")
        # self.add_bunny_widget(bunny_uid="LGN03")
        # self.bunny_widgets["LGN01"].pos_hint = {"center_x": 0.5, "center_y": 0.5}
        # self.bunny_widgets["LGN02"].pos_hint = {"center_x": 0, "center_y": 0.5}
        # self.bunny_widgets["LGN03"].pos_hint = {"center_x": 0.5, "center_y": 0}

    # create a shape
        shape = {
            "type": "Rectangle",
            "segments": 6,
            "pos": (self.parent.pos[0] + self.parent.width/3, self.parent.pos[1] + self.parent.height/3),
            "size": (400,400),
            "num_robots": "Maximum"
        }
        targets = ShapeFormation.calc_target_points_from_shape(shape, 
                                                               (self.parent.size[0] * (0.2/5), self.parent.size[1] * (0.2/5)))

        for i, target in enumerate(targets):
            self.add_bunny_widget(bunny_uid=f"LGN0{i+1}")
            self.bunny_widgets[f"LGN0{i+1}"].pos_hint = {"center_x": (target[0]-self.parent.pos[0])/ self.parent.width, 
                                                         "center_y": (target[1]-self.parent.pos[1]) / self.parent.height} 
        self._parent._ids.connections.add_robots_status_bars()

    def _velocity_handler(self, bunny_uid, *args):
        print(bunny_uid + "done")

    # def rotate_robots(self, *args):
    #     if self.bunny_widgets == {}:
    #         return False
    #     current_robot_pos = np.array([robot.pos for robot in self.bunny_widgets.values()]).T
    #     #current_robot_pos = np.array([[50,0], [60,0], [60,120]])
    #     centroid = np.reshape(np.average(current_robot_pos, axis=1), (2,1))
    #     #centroid = np.array([[60],[60]])
    #     #centroid = [[self.parent.pos[0]], [self.parent.pos[1]]]
    #     current_robot_pos = current_robot_pos.T
    #     sampling_time = 0.1
    #     velocities = PathPlanner.compile_rotational_velocities(current_pos=current_robot_pos, 
    #                                                            centroid=centroid, 
    #                                                            angle=2*math.pi, 
    #                                                            rot_vel=0.12, 
    #                                                            sampling_time=sampling_time)
    #     velocities = velocities.tolist()
    #     for i, (bunny_uid, bunny) in enumerate(self.bunny_widgets.items()):
    #         self.vel_handler.add_velocity(bunny=bunny,
    #                                       velocities=velocities[i], 
    #                                       timestep=sampling_time,
    #                                       mode="sim",
    #                                       callback=self._velocity_handler)
    #         self.vel_handler.start(bunny_uid)

    #     Clock.schedule_once(partial(self.expand_robots, 1.5), 15)
    #     Clock.schedule_once(partial(self.expand_robots, 1/1.5), 25)
    #     Clock.schedule_once(partial(self.translate_robots, 200, 0), 35)
    #     Clock.schedule_once(partial(self.translate_robots, 0, -200), 45)


    # def expand_robots(self, factor, *args):
    #     current_robot_pos = np.array([robot.pos for robot in self.bunny_widgets.values()]).T
    #     centroid = np.reshape(np.average(current_robot_pos, axis=1), (2,1))
    #     final_points = ShapeFormation._apply_scale_matrix(current_robot_pos.T, factor)
    #     sampling_time = 0.01
    #     velocities = PathPlanner.compile_linear_velocities(current_robot_pos.T, final_points, 8, sampling_time)
    #     velocities = velocities.tolist()
    #     self.vel_handler.clear()
    #     for i, (bunny_uid, bunny) in enumerate(self.bunny_widgets.items()):
    #         self.vel_handler.add_velocity(bunny=bunny,
    #                                       velocities=velocities[i], 
    #                                       timestep=sampling_time,
    #                                       mode="sim",
    #                                       callback=self._velocity_handler)
    #         self.vel_handler.start(bunny_uid)

    # def translate_robots(self, x, y, *args):
    #     current_robot_pos = np.array([robot.pos for robot in self.bunny_widgets.values()]).T
    #     centroid = np.reshape(np.average(current_robot_pos, axis=1), (2,1))
    #     final_points = ShapeFormation._apply_translate_matrix(current_robot_pos.T, x, y)
    #     sampling_time = 0.01
    #     velocities = PathPlanner.compile_linear_velocities(current_robot_pos.T, final_points, 10, sampling_time)
    #     velocities = velocities.tolist()
    #     self.vel_handler.clear()
    #     for i, (bunny_uid, bunny) in enumerate(self.bunny_widgets.items()):
    #         self.vel_handler.add_velocity(bunny=bunny,
    #                                       velocities=velocities[i], 
    #                                       timestep=sampling_time,
    #                                       mode="sim",
    #                                       callback=self._velocity_handler)
    #         self.vel_handler.start(bunny_uid)


        #Clock.schedule_once(self.check_bunny_movement, 2)

    # def check_bunny_movement(self, *args):
    #     self.add_bunny_widget(bunny_uid="LGN01")
    #     self.add_bunny_widget(bunny_uid="LGN02")
    #     self.add_bunny_widget(bunny_uid="LGN03")

    #     self.bunny_widgets["LGN01"].pos_hint = {"center_x": 0.2, "center_y": 0.5}
    #     self.bunny_widgets["LGN02"].pos_hint = {"center_x": 0.7, "center_y": 0.5}
    #     self.bunny_widgets["LGN03"].pos_hint = {"center_x": 0.1, "center_y": 0.3}

    #     self.bunny_widgets["LGN01"].v = [100, 0, 100]
    #     self.bunny_widgets["LGN02"].v = [-100, 0, 100]
    #     self.bunny_widgets["LGN03"].v = [-100, -100, 100]
    #     Clock.schedule_interval(self.update_bunny_movement, 0.01)

    # def update_bunny_movement(self, *args):
    #     for bunny in self.bunny_widgets:
    #         for other_bunny in self.bunny_widgets:
    #             if(bunny == other_bunny):
    #                 continue
    #             else:
    #                 b1 = self.bunny_widgets[bunny]
    #                 b2 = self.bunny_widgets[other_bunny]
    #                 dist = math.hypot(b2.pos[0] - b1.pos[0], b2.pos[1] - b1.pos[1])
    #                 if(dist < 100):
    #                     self.bunny_widgets[bunny].v[0] *= -1
    #                     self.bunny_widgets[bunny].v[1] *= -1
        
    #     for x in self.bunny_widgets:
    #         self.bunny_widgets[x].move(self.bunny_widgets[x].v, "sim", args[0])


    def update_canvas_scale(self, instance, value):
        """
        Feature not completely working for now!!
        """
        if value == '' or float(value) == 0.0:
            return True
        
    def notify_property_change(self, func, *args):
        for wid in self._shapes:
            try:
                getattr(wid["widget"], func)(*args)
            except Exception as e:
                print( wid, e)
                pass

        for bunny_uid, bunny in self._bunny_widgets.items():
            try:
                getattr(bunny, func)(*args)
            except Exception as e:
                print( bunny_uid, e)
                pass

    def on_window_motion(self, *args):

        """"
        this function helps to keep track of
        whether mouse is on the canvas.
        in that way, the keyboard is requested 
        to perform delete operations
        """
        if self._keyboard is not None:
            return
        for arg in args:
            if type(arg).__name__ == "MouseMotionEvent":
                pos_x = arg.pos[0]
                pos_y = arg.pos[1]
                if ((self._parent.x < pos_x < self._parent.width + self._parent.x) and
                    (self._parent.y < pos_y < self._parent.height + self._parent.y)):
                    if self._keyboard is None:
                        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
                        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        if self._keyboard is not None:
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        for wid in self._shapes:
            try:
                wid["widget"]._on_keyboard_down(keyboard, keycode, text, modifiers)
            except Exception as e:
                print( wid, e)
                pass
        return True

    def add_shape(self, shape_settings, shape_properties):
        widget_ref = None
        try:
            if shape_properties["border_color"][-1] == 0.0 and \
                shape_properties["fill_color"][-1] == 0.0:
                InformationPopup(_type='e', 
                                 _message="Both Border Color and Fill Color are fully transparent").open()
                return False
            elif shape_properties["border_color"][-1] == 0.0 and shape_properties["type"] == "Border":
                InformationPopup(_type="e", 
                                 _message="Border has no color!").open()
                return False
            elif shape_properties["fill_color"][-1] == 0.0 and shape_properties["type"] == "Obstacle":
                InformationPopup(_type="e", 
                                 _message="Obstacle has no fill_color!!").open()
                return False
            elif shape_properties["shape"] == "Polygon" and shape_properties["segments"] == 0:
                InformationPopup(_type="e", 
                                 _message="Number of segments unspecified for Polygon").open()
                return False
        except Exception as e:
            print(e)
            return False    

        if self._active_widget is not None:
            return
        
        widget_properties = {}
        widget = None
        mode = "Fill"
        if shape_properties["type"] == "Border":
            shape_properties["fill_color"] = [0, 0, 0, 0]
            print("Border detected!!")
            mode = "Border"
        if shape_properties["shape"] == "Rectangle":
            widget = DragAndResizeRect()
        elif shape_properties["shape"] == "Ellipse":
            widget = DragAndResizePolygon()
        elif shape_properties["shape"] == "Polygon":
            widget = DragAndResizePolygon()
            widget.update_property("segments", shape_properties["segments"])
            shape_settings._segments_text_input.bind(text=widget.set_segments)            
        elif shape_properties["shape"] == "Triangle":
            return False
        widget.update_property("fill_color", shape_properties["fill_color"])
        widget.update_property("border_color", shape_properties["border_color"])
        widget.update_property("mode", mode )
        widget.update_property("canvas_manager", self)
        shape_settings.bind(_shape_fill_color=widget.set_fill_color)
        shape_settings.bind(_shape_border_color=widget.set_border_color)
        shape_settings._lock_size_checkbox.bind(active=widget.set_lock_size)
        shape_settings._lock_position_checkbox.bind(active=widget.set_lock_pos)
            
        widget_properties["widget"] = widget
        widget_properties["type"] = shape_properties["type"]
        widget_properties["pos"] = self._parent.center
        self._parent.add_widget(widget)
        widget.pos = widget.parent.pos
        widget.size = (widget.parent.size[0]/3, widget.parent.size[1]/3)
        self._active_widget = widget
        self._shapes.append(widget_properties)
        return widget

    def untrack_widget(self, shape_settings, widget):
        widget.update_property("_fixed", True)
        shape_settings.unbind(_shape_fill_color=widget.set_fill_color)
        shape_settings.unbind(_shape_border_color=widget.set_border_color)
        shape_settings._lock_size_checkbox.unbind(active=widget.set_lock_size)
        shape_settings._lock_position_checkbox.unbind(active=widget.set_lock_pos)
        try:
            shape_settings._segments_text_input.unbind(text=widget.set_segments)
        except Exception as e:
            print("untrack_widget", e)
            pass
        self._active_widget = None
        return True

    def remove_widget(self, widget):
        for index, wid in enumerate(self._shapes):
            for value in wid.values():
                if value == widget:
                    self._parent.remove_widget(widget)
                    del self._shapes[index]
        return True

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
        bunny.Cons = self._parent.app.constants
        bunny.size_hint = kwargs.get("size_hint", (0.05, 0.05))
        bunny.pos = kwargs.get("pos", self.parent.pos)
        bunny.pos_hint = kwargs.get("pos_hint", {"center_x": 0.0, "center_y": 0.0})
        bunny["state"] = kwargs.get("state", "charge")
        bunny["angle"] = kwargs.get("angle", 0)
        self._parent.add_widget(bunny)

    def remove_bunny_widget(self, bunny_uid, *args):
        """
        removes the bunny widget!
        """
        try:
            self.parent.remove_widget(self.bunny_widgets[bunny_uid])
        except Exception as e:
            print(e)
    #----------------------------- ++++ ------------------------------#

    def add_choreo_shape(self, shape, choreboard, *args):
        if shape == "rect":
            shape = ChoreoRect()
            self.choreo_shapes.append(shape)
            self.parent.add_widget(shape)
            shape.size_hint = (0.1, 0.1)
            shape.pos_hint = {"x": 0.5, "y": 0.5}

    def remove_choreo_shape(self, index):
        self.parent.remove_widget(self.choreo_shapes[index])

    #---------------------------- ++++ ------------------------------#

    @property
    def bunny_widgets(self):
        return self._bunny_widgets

    @property
    def parent(self):
        return self._parent

    @property
    def shapes(self):
        return self._shapes

    @property
    def choreo_shapes(self):
        return self._choreo_shapes


class RobotCanvas(FloatLayout):
    """
    Class RobotCanvas
    Used to initalize and display the robots
    """  
    background_color = ListProperty([1, 1, 0, 0])
    app = ObjectProperty()
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
        self._bunny_widgets = {}
        self.pos = (0 ,0)
        self._ids = None
        self.gridline_widget = None
        self.canvas_manager = None
        Clock.schedule_once(self.initialize, 0.5)


    def initialize(self, *args):
        self._ids = self.app.root.ids
        self.gridline_widget = self.add_gridlines()  
        self.canvas_manager = CanvasManager(self)
        self._ids.environment.scale_settings.update_property("canvas_manager", self.canvas_manager)
        self._ids.choreography.update_property("canvas_manager", self.canvas_manager)
        self._ids.connections.update_property("canvas_manager", self.canvas_manager)
        Clock.schedule_once(partial(self.gridline_widget.force_max_length, 5, "m"), 2)


    def _update_pos(self, instance, pos):
        try:
            self.pos = pos
            if self.gridline_widget is not None:
                self.gridline_widget.update_grid()
        except AttributeError:
            return

    def _update_size(self, instance, size):
        self.size = size

    ## Gridlines methods
    def add_gridlines(self):
        grid_line_widget = GridWidget()
        self.app.constants.bind(CANVAS_SCALE=grid_line_widget.update_scale)
        grid_line_widget.pos_hint = {"x":0, "y":0}
        grid_line_widget.size_hint = (1, 1)
        self.add_widget(grid_line_widget)
        return grid_line_widget

    def remove_gridlines(self):
        self.remove_widget(self.gridline_widget)

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
        return super(RobotCanvas, self).on_touch_down(touch)

    def on_touch_up(self, touch):
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
    choreoboard = ObjectProperty()
    canvas_manager = ObjectProperty(allownone=True)
    def __init__(self, **kwargs):
        super(Choreography, self).__init__(**kwargs)
        self.dance_moves = []

    def update_property(self, property, value):
        setattr(self, property, value)

    def add_rotation_step(self, current_pos, angle, rotational_vel, sampling_time, *args):
        velocities = PathPlanner.compile_rotational_velocities()

    def add_transition_step(self, 
                            current_pos, 
                            final_pos, 
                            duration, 
                            sampling_time, 
                            index=-1, *args):
        velocities = PathPlanner.compile_linear_velocities(current_pos, final_pos, duration, sampling_time)
        if index == -1:
            self.dance_moves.append(["transit", velocities, duration, sampling_time])
        else:
            self.dance_moves.insert(["transit", velocities, duration, sampling_time], index)

    def remove_step_move(self, index):
        del self.dance_moves[index]

    def on_canvas_manager(self, instance, value):
        if value is None:
            return
        self.choreoboard.canvas_manager = value

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


class Connections(BoxLayout):
    app = ObjectProperty()
    # Handles connections 
    radio_dongle_wid = ObjectProperty()
    status_board_wid = ObjectProperty()
    _radio_connected = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # create an automated connection attempt
        self.canvas_manager = None
        self.nm = None
        # Set the radio dongle widget state to searching
        # once GUI has been initialized!
        Clock.schedule_once(self.initialize, 1)

    def update_property(self, property, value):
        setattr(self, property, value)

    def initialize(self, *args):
        self.radio_dongle_wid.set_state_to_searching()
        self.nm = NetworkManager(self)

    # Functions to be called from Network Manager
    # +==================================================+
    def radio_connected(self, nm):
        self.radio_dongle_wid.set_state_to_connected()

    def radio_disconnected(self, nm):
        InformationPopup("w", "Disconnected from Radio").open()
        self.radio_dongle_wid.set_state_to_searching()

    # +===================================================+

    #========= Address Address Issues =======#
    def assign_address(self, bunny, reserve=True):
        """
        Request an address for communication
        if reserve: reserve the address, else do not reserve
        """
        for (addr, active) in self._address:
            if not active:
                active = True
                bunny.addr = addr

class Environment(BoxLayout):
    scale_settings = ObjectProperty()
    app = ObjectProperty()

    def __init__(self, **kwargs):
        super(Environment, self).__init__(**kwargs)
        Clock.schedule_once(self.initialize, 0.5)

    def initialize(self, *args):
        # Label Background color
        pass    
    
    def on_pos(self, instance, value):
        self.pos = value

    def on_size(self, instance, value):
        self.size = value

class StatusBoard(BoxLayout):
    scroll_view = ObjectProperty()
    
    def __init__(self, **kwargs):
        super(StatusBoard, self).__init__(**kwargs)

    def update_board(self, children):
        pass

    def remove_widget(self, uid: str):
        pass

    def add_bunny_action_bar(self, bunny):
        _bunny = BunnyActionBar(bunny)
        self.scroll_view.add_widget(_bunny)
