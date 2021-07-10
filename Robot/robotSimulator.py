from random import randint
import numpy as np
import warnings
import asyncio
import time


class BunnySim:
    def __init__(self, id, currentPos=None, **kwargs):
        self.id = id
        self.size = (12, 12)      # cm
        self.maxMotorSpeed = 120  # rpm
        self.batteryPower = 100   # percentage
        self.currentPos = np.array([0, 0, 0]) if currentPos == None else currentPos
        self.mode = 'idle'
        self.wheelRadius = 1.5/100 # m

        if kwargs.get('size') is not None:
            self.size = kwargs.get('radius')
        if kwargs.get('maxMotorSpeed') is not None:
            self.maxMotorSpeed = kwargs.get('maxMotorSpeed')
        if kwargs.get('batteryPower') is not None:
            self.batteryPower = kwargs.get('batteryPower')

    async def move(self, finalPos, speed, refreshTime = 60):
        if speed > self.maxMotorSpeed:
            warnings.warn("specified speed is greater than Robot's maximum speed\n Maximum Speed of Robot will be used")
            speed = self.maxMotorSpeed
            self.mode = 'moving'


    async def setTrajectory(self, trajectory):
        pass



    def scaleDimension(self, radius):
        pass


if __name__ == "__main__":
    pass
