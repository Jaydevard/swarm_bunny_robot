"""
Author: Jaydev Madub
Date: 9/9/21
User is responsible for the script
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.animation import Animation
from kivy.graphics import Line, Rectangle, Ellipse
from kivy.graphics import Color
from kivy.graphics.instructions import InstructionGroup
from kivy.core.image import Image
import random


class ColorfulBox(BoxLayout):
    rectangle_size = ObjectProperty()

    def __init__(self, **kwargs):
        super(ColorfulBox, self).__init__(**kwargs)
        self.robots_dict = {}
        self.robot_size = (50, 50)

        # Create the background InstructionGroup
        self.environment_background = InstructionGroup()
        self.environment_background_rectangle = Rectangle(pos=self.pos,
                                                          size=self.size)

        self.environment_background_color = Color(1, 1, 0, 1)
        self.environment_background.add(self.environment_background_color)
        self.environment_background.add(self.environment_background_rectangle)
        self.canvas.add(self.environment_background)
        self.bind(pos=self.update_pos, size=self.update_pos)

        # Create the robots group on the canvas
        # Keep it empty at instantiation
        # --> always add the required shape and a Color object
        # --> first add the Color and if necessary reference it
        # --> then add the shape, if necessary reference it

        self.robots_instruction_group = InstructionGroup()
        self.canvas.add(self.robots_instruction_group)

        Clock.schedule_interval(self.add_a_robot, 0.015)
        Clock.schedule_interval(self.reset_box, 10)

    def update_pos(self, *args):
        self.environment_background_rectangle.pos = self.pos
        self.environment_background_rectangle.size = self.size

    def change_background_color(self, *args, **kwargs):
        self.environment_background_color.r = kwargs.get('r')
        self.environment_background_color.g = kwargs.get('b')
        self.environment_background_color.b = kwargs.get('g')
        self.environment_background_color.a = kwargs.get('a')

    def add_a_robot(self, *args):
        self.add_robot(robot_id=1, robot=self, pos=(random.uniform(0, 1),
                                                    random.uniform(0, 1)),
                       color=(random.uniform(0, 1),
                              random.uniform(0, 1),
                              random.uniform(0, 1),
                              1))

    def add_robot(self, *args, robot_id: int, robot: object, pos: tuple, color=(1, 1, 1, 1)):
        """
        Adds a robot to the canvas, default shape is an Ellipse
        :param args: handles extra arguments
        :param robot_id: identification number of the robot
        :param robot: the reference object to the real robot
        :param pos: the relative position: should be bet 0 and 1, eg. (0.5, 0.5)-->center
        :param color: tuple of four values rgba format bet 0 and 1
        :return: None
        """
        _ = {'id': robot_id,
             'object': robot,
             'robot_shape': Ellipse(pos=(self.pos[0]+self.width*pos[0],
                                         self.pos[1]+self.height*pos[1]),
                                    size=self.robot_size),
             'color': Color(*color)}
        self.robots_dict[f'robot{robot_id}'] = _
        self.robots_instruction_group.add(_['color'])
        self.robots_instruction_group.add(_['robot_shape'])

    def reset_box(self, *args):
        self.canvas.remove(self.robots_instruction_group)
        self.robots_dict.clear()
        self.change_background_color(r=random.uniform(0, 1),
                                     g=random.uniform(0, 1),
                                     b=random.uniform(0, 1),
                                     a=1)
        self.robots_instruction_group = InstructionGroup()
        self.canvas.add(self.robots_instruction_group)


class MyColorfulBox(App):
    def __init__(self, **kwargs):
        super(MyColorfulBox, self).__init__(**kwargs)
        self.ids = None

    def build(self):
        self.ids = self.root.ids


if __name__ == "__main__":
    colorful_box = MyColorfulBox()
    colorful_box.run()