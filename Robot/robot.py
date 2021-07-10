"""
Bunny Robot Class File:
    Class Bunny:
                Creates a bunny robot object
                Simulates the robot's response to a command
                sends back data from sensors: odometry
"""

import numpy as np
import time


class RobotTransceiver:
    def __init__(self, channel):
        self.channel = channel
        pass
    def receive_message(self, message):
        self.channel.receive()

class RobotWheel:
    """
    Class for Robot Wheel: control each wheel using this class
        :
    """
    def __init__(self, pos, radius, max_speed_of_rotation):
        self.pos = pos
        self.wheel_radius = radius
        self.max_speed_of_rotation = max_speed_of_rotation

class PathPlanner:
    pass



class Bunny:
    def __init__(self, channel, reference, **kwargs):
        self.reference = reference
        self.transceiver = RobotTransceiver(channel=channel)
        self.dimensions = {
            "width": 0.12,
            "length" : 0.12,
            "surface_area": round(0.17**2*np.pi, 3),  # includes 5 cm safety margin
            "height": 0.10
            }
        self.wheels = {
            "front": RobotWheel("top", 0.10, 3),
            "right": RobotWheel("right", 0.10, 3),
            "left": RobotWheel("left", 0.10, 3)
        }

    async def start_random_position(self):
        self.leftmotor = -1
        self.rightmotor = -1
        pass

    async def move(self, x1, y1, theta):
        """
        Motion relative to the robot
        :param x1: positive x-axis in the east direction of robot
        :param y1: positive y-axis to the north of robot
        :return: Nothing
        """
    async def stop(self, delay=None):
        """
        stops the robot from moving
        optional: add delay: stop after certain delay in milliseconds
        :return:
        """
        pass
    async def update_pos(self):
        pass

    async def path_planner(self):
        pass





if __name__ == "__main__":
   pass

