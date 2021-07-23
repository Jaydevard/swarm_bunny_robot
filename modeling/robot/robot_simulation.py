from random import randint
import numpy as np
import warnings
import asyncio
import time


class BunnySim:
    def __init__(self, id, current_pos=None, **kwargs):
        self.id = id
        self.size = (12, 12)      # cm
        self.max_motor_speed = 120  # rpm
        self.battery_power = 100   # percentage
        self.current_pos = current_pos
        self.mode = 'idle'
        self.wheel_radius = 1.5/100 # m

        if self.current_pos.all() == None:
            self.current_pos = np.array([0,0])

        if kwargs.get('size') is not None:
            self.size = kwargs.get('radius')
        if kwargs.get('max_motor_speed') is not None:
            self.max_motor_speed = kwargs.get('max_motor_speed')
        if kwargs.get('battery_power') is not None:
            self.batteryPower = kwargs.get('battery_power')

    async def move(self, final_pos, speed, refresh_time = 60):
        if speed > self.max_motor_speed:
            warnings.warn("specified speed is greater than Robot's maximum speed\n Maximum Speed of Robot will be used")
            speed = self.max_motor_speed
            self.mode = 'moving'

    async def update_bunny_position(self, pos):
        self.current_pos = pos


    async def set_trajectory(self, trajectory):
        pass



if __name__ == "__main__":
    pass
