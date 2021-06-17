"""
Bunny Robot Class File:
    Class Bunny:
                Creates a bunny robot object
                Simulates the robot's response to a command
                sends back data from sensors: odometry
"""

import numpy as np
import time


class Bunny:
    def __init__(self, **kwargs):
        self._ipaddress = None
        self.leftmotor = 0
        self.rightmotor = 0
        self.position = (kwargs.get("x0"), kwargs.get("y0"))

    @staticmethod
    def start_random_position():
        pass

    def move(self, x1, y1):
        """
        Motion relative to the robot
        :param x1: positive x-axis in the east direction of robot
        :param y1: positive y-axis to the north of robot
        :return: Nothing
        """
    def stop(self, delay=None):
        """
        stops the robot from moving
        optional: add delay: stop after certain delay in milliseconds
        :return:
        """
        if delay is None:
            self.leftmotor = 0
            self.rightmotor = 0
        else:
            time.sleep(delay/1000)
            self.leftmotor = 0
            self.rightmotor = 0




