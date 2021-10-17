import random
import time
from kivy.clock import Clock

_all_ = ["SwarmBunnyManager"]


class Bunny:
    def __init__(self, number):
        self.id = f"bunny{number}"


class SwarmBunnyManager:
    """
    :param canvas: (BoxLayout) where Bunny Widget appears
    :param wnm, WirelessNetworkManager,
    Manages the Bunny position\n
    --> sends update about the positions of the robot to RobotCanvas\n
    --> keeps track of attributes of each robot
        1) bunny battery\n
        2) bunny position\n
        3) bunny state:\n
            --> 1) charging\n
            --> 2) moving \n
            --> 3) idle

    --> sends command to WirelessNetworkManager
        to stop the robot, change its position, or go for charging
        based upon the USER's command(NOT the path planning or collision avoidance)
        --> this is a master control to allow the user to control the robot
            since instruction has to go through gui to get to the robot

    """

    def __init__(self, canvas=None, wnm=None):
        self._bunny_refs = {}
        self._canvas_update_lock = False
        self.wnm = wnm
        self.canvas = canvas

    def add_bunny_to_list(self, *args):
        bunny_num = random.randint(0, 100)
        bunny = Bunny(bunny_num)
        try:
            self["bunny"] = bunny
        except KeyError:
            pass

    def send_control_command_to_robot(self, bunny):
        if self.wnm is None:
            return False
        else:
            # send command
            pass

    @property
    def bunny_refs(self):
        return self._bunny_refs

    def __setitem__(self, key, value):
        if key == "bunny":
            self._bunny_refs[value.id] = {"object": value,
                                          "id": value.id,
                                          "on_canvas": False}
        # Add more keys


if __name__ == "__main__":
    pass

