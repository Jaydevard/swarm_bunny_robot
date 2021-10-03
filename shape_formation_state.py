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
        velocity_x = 0            #initial x-velocity
        velocity_y = 0            #initial y-velocity

        #calculate the distance bw current location and target location
        delta_x = self.final_x-self.current_x
        delta_y = self.final_y-self.current_x
        dis= math.sqrt(abs(delta_x * delta_x + delta_y * delta_y))

        #calculate the angle of the distance with the reference frame
        zetha = math.atan((self.y1 - self.y) / (self.x1 - self.x))

        #rotate the robot until the angle of the robot in the reference frame (theta) equals to angle (zetha)
        alpha = self.theta_robot - zetha         #difference bw the two angles
        step = 20
        delta_alpha = alpha/step
        for i in range (step):                   #until theta_robot is not equal to zetha, the robot will rotate on itself
            self.theta_robot -= delta_alpha
            rot_vel = 0.1
            velocity_x = 0
            velocity_y = 0

        #Defining PID Gains
        kp = 2.0
        ki = 160.9605
        kd = 0.00000005

        #Initialization of PID
        e = 0
        nu = 0
        ts = 1 / 150
        e1 = 0
        error = 1  # dummy error

        #Creating PID controller using velocity algorithm
        while error != 0:
            e2 = e1
            e1 = e
            e = round(ref - nu * ts, 2)
            error = e
            ou = nu
            nu = ou + kp * (e - e1) + ki * e * ts + kd * (e - 2 * e1 + e2) / ts  # PID controller
            distance = nu * ts

            if (self.current_x == self.final_x) and (self.current_y == self.final_y):
                velocity_x = 0
                velocity_y = 0
                rot_vel = 0

            elif (self.current_x > self.final_x) and (self.current_y < self.current_y):
                self.current_x -=  distance * math.cos(zetha)
                self.current_y -= distance * math.sin(zetha)

                velocity_x = velocity * math.cos(zetha)
                velocity_y = velocity * math.sin(zetha)
                rot_vel = 0

            elif (self.current_x < self.final_x) and (self.current_y < self.final_y):
                self.current_x += distance * math.cos(zetha)
                self.current_y += distance * math.sin(zetha)
                velocity_x = velocity * math.cos(zetha)
                velocity_y = velocity * math.sin(zetha)
                rot_vel = 0


            elif (self.current_x > self.final_x) and (self.current_y > self.final_y):
                self.current_x -= distance * math.cos(zetha)
                self.current_y -= distance * math.sin(zetha)
                velocity_x = velocity * math.cos(zetha)
                velocity_y = velocity * math.sin(zetha)
                rot_vel = 0

        velocity_x = 0
        velocity_y = 0
        rot_vel = 0














