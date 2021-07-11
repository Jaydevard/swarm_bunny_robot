from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from robotSimulator import BunnySim
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivy.core.window import Window


WidgetIds = None
R_Canvas = None

class RobotCanvas(BoxLayout):
    terminate_execution = False
    robot_pos = ObjectProperty(None)
    floor_width = 0
    floor_height = 0
    # Init velocitys for 2 robots
    v_1 = [0, 0]
    v_2 = [0, 0]


    def __init__(self, **kwargs):
        super(RobotCanvas, self).__init__(**kwargs)
        #Clock.schedule_once(self.init_robots, 3)
        global R_Canvas
        R_Canvas = self

        self.robots = {}

    def createRobots(self, numRobots):
        for i in range(numRobots):
            self.robots[f'Robot{i}'] = BunnySim(id=i)

    def defineEnvironment(self, dimension, *args):
        pass

    def update_robots(self):
        if(self.terminate_execution):
            self.v_1=[0, 0]
            self.v_2=[0, 0]
            return False

        robots = WidgetIds['robots']
        w = Window.width - self.width

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
        robots = WidgetIds['robots']
        w = Window.width - self.width
        self.v_1 = [7, -4]
        self.v_2 = [-5, 8]

        robots.robot_pos1 = [w, 0]
        robots.robot_pos2 = [w, 0]

        Clock.schedule_interval(self.update, 1.0 / 60.0)        

    def update(self, dt):
        if(WidgetIds != None):
            self.update_robots()

class RobotVisualization(App):
    def build(self):
        # Wait till the gui inits to pull in the IDs
        Clock.schedule_once(self.finish_init)
        pass

    def start_execution(self): 
        WidgetIds['start_button'].disabled = True
        global R_Canvas
        R_Canvas.init_robots(R_Canvas)

    def finish_init(self, dt):
        # Not ideal solution. Ids are out of scope from our RobotCanvas class so setting them global
        global WidgetIds
        WidgetIds = self.root.ids

if __name__ == "__main__":
    RobotVisualization().run()