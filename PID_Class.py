import math
import numpy as np
from bunny import Bunny

class PID:
    def __init__(self,x,y,theta_robot,x1,y1):
        """
        :param x:
        :param y:
        :param theta_robot:
        :param x1:
        :param y1:
        """
        self.x = x
        self.y = y
        self.theta_robot = theta_robot
        self.x1 = x1
        self.y1 = y1

    def PID_CONTROL(self):
        omega = np.empty(0)
        trajectory_x = np.empty(0)
        trajectory_y = np.empty(0)
        velocity_x = np.empty(0)
        velocity_y = np.empty(0)
        velocity = 20

        if self.x == self.x1 or self.y == self.y1:
            theta = 0
        else:
            theta = math.atan((self.y1 - self.y) / (self.x1 - self.x))


        #align robot to path angle
        alpha = self.theta_robot - theta
        delta_alpha = alpha/20
        for i in range(20):
            self.theta_robot -= delta_alpha
            velocity_x = 0
            velocity_y = 0
            rotational_speed = 0.1
            omega = np.append(omega,rotational_speed)
            velocity_x= np.append(velocity_x,0)
            velocity_y = np.append(velocity_y,0)
            print(velocity_x,velocity_y,rotational_speed)
        delta_x = self.x1 - self.x
        delta_y = self.y1 - self.y

        ref = math.sqrt(abs(delta_x * delta_x + delta_y * delta_y))

        #PID GAINS
        kp = 2.0  # 9.6266
        ki = 160.9605  #16.9205
        kd =  0.00000005   #0.16740

        #PID INITIALIZATION
        e = 0
        nu = 0
        ts = 1 / 150
        e1 = 0
        error = 1  # dummy error

        #PID LOOP
        while error != 0:
            e2 = e1
            e1 = e
            e = round(ref - nu * ts, 2)
            error = e
            ou = nu
            nu = ou + kp * (e - e1) + ki * e * ts + kd * (e - 2 * e1 + e2) / ts  # PID controller
            distance = nu * ts
            if (self.x == self.x1) and (self.y == self.y1):
                trajectory_x = np.append(trajectory_x,self.x)
                trajectory_y= np.append(trajectory_y,self.y)
                print(self.x, self.y)
            elif (self.x > self.x1) and (self.y < self.y1):
                trajectory_x = np.append(trajectory_x,self.x - distance * math.cos(theta))
                trajectory_y = np.append(trajectory_y,self.y - distance * math.sin(theta))
                print(self.x - distance * math.cos(theta), self.y - distance * math.sin(theta), theta)
            if (self.x < self.x1) and (self.y < self.y1):
                trajectory_x = np.append(trajectory_x,round(self.x + distance * math.cos(theta),2))
                trajectory_y = np.append(trajectory_y,round(self.y + distance * math.sin(theta),2))
                velocity_x = 10
                velocity_y = 10
                rotational_speed = 0
                print(velocity_x, velocity_y, rotational_speed)
                #print(trajectory_x,trajectory_y, theta)
            elif (self.x > self.x1) and (self.y > self.y1):
                trajectory_x = np.append(trajectory_x,self.x - distance * math.cos(theta))
                trajectory_y = np.append(trajectory_y,self.y - distance * math.sin(theta))
                print(self.x - distance * math.cos(theta), self.y - distance * math.sin(theta),theta)
            velocity_x = np.append(velocity_x,(round(velocity*math.cos(theta),2)))
            velocity_y = np.append(velocity_y,(round(velocity* math.sin(theta),2)))
            omega = np.append(omega, 0)

        velocity_x = np.append(velocity_x, 0)
        velocity_y = np.append(velocity_y, 0)
        omega = np.append(omega,0)
        #print(trajectory_x[100])