import numpy as np
import math

class Shape_Formation:

    #initialize the starting position, the angle of the robot with the reference frame,and the final position
    def __init__(self,current_x,current_y,theta_robot,final_x,final_y):
        self.current_x = current_x
        self.current_y = current_y
        self.theta_robot = theta_robot
        self.final_x = final_x
        self.final_y = final_y

    def move_to_target(self):
        velocity = 20             #20 cm/s
        rot_vel  = 0.1            #rotational velocity in rad/s

        #calculate the distance bw current location and target location
        delta_x = self.final_x-self.current_x
        delta_y = self.final_y-self.current_x
        distance= math.sqrt(abs(delta_x * delta_x + delta_y * delta_y))

        #calculate the angle of the distance with the reference frame
        zetha = math.atan((self.y1 - self.y) / (self.x1 - self.x))

        #rotate the robot until the angle of the robot in the reference frame (theta) equals to angle (zetha)
