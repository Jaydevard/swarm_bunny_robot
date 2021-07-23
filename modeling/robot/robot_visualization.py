from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from robot_simulation import BunnySim
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivy.core.window import Window

# Globals
widget_ids = None
robot_canvas_ref = None

class RobotCanvas(BoxLayout):
    """
    Class RobotCanvas
    Used to initalize and display the robots
    """
    terminate_execution = False # Termination flag
    robot_pos = ObjectProperty(None) # Property ref from kv file
    # Default values for sim
    floor_width = 0
    floor_height = 0
    v_1 = [0, 0]
    v_2 = [0, 0]


    def __init__(self, **kwargs):
        super(RobotCanvas, self).__init__(**kwargs)
        global robot_canvas_ref
        robot_canvas_ref = self
        self.robots = {}

    def create_robots(self, num_robots):
        for i in range(num_robots):
            self.robots[f'Robot{i}'] = BunnySim(id=i)

    def define_environment(self, dimension, *args):
        pass

    def update_robots(self):
        """
        Updates the robot prosition on the canvas
        """
        if(self.terminate_execution): # Kill it
            return False

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
        if(widget_ids != None):
            self.update_robots()


class RobotVisualization(App):
    """
    RobotVisualization Class
    This is where we instatiate the GUI
    """
    def build(self):
        # Wait till the gui inits to pull in the IDs
        Clock.schedule_once(self.finish_init, 1)
        pass

    def start_execution(self):
        widget_ids['start_button'].disabled = True
        global robot_canvas_ref
        robot_canvas_ref.init_robots(robot_canvas_ref)

    def finish_init(self, dt):
        # Not ideal solution. Ids are out of scope from our RobotCanvas class so setting them global
        global widget_ids
        widget_ids = self.root.ids

if __name__ == "__main__":
    RobotVisualization().run()