import math
import numpy as np
from kivy.clock import Clock
from kivy.event import EventDispatcher
from functools import partial


class PathPlanner(EventDispatcher):
    def __init__(self, **kw):
        super().__init__(**kw)

    @staticmethod
    def compile_linear_velocities(current_pos: list or np.ndarray, 
                                  final_pos: list or np.ndarray, 
                                  duration: int or float, 
                                  sampling_time: int or float):
        """
        :param
            current_pos and final_pos: current position 
            [ [x1 y1 th1],
              [x2 y2, th2], 
              [x3 y3 th3]...]
            duration: time of travel(s)
            sampling time: timestep(s)
        :return
            Returns an array of velocities for each robot
            in the form:
                robot_1 : [[0.1, 0.2], [50, 60], [75, 50],......,[]]
        
        """
        delta_x = np.array(final_pos[:, 0] - current_pos[:, 0])
        delta_y = np.array(final_pos[:, 1] - current_pos[:, 1])
        theta = np.arctan2(delta_y,delta_x)
        print(theta)
        r = np.sqrt(delta_x**2 + delta_y**2)
        delta_t = duration
        Vx = np.round(r * np.cos(theta) / delta_t, 4)
        Vx = np.reshape(Vx, (-1, 1))
        Vy = np.round(r * np.sin(theta) / delta_t, 4)
        Vy = np.reshape(Vy, (-1, 1))
        vel = np.concatenate((Vx, Vy), axis=1)
        N = int(round(delta_t / sampling_time))
        vel_3d = np.repeat(vel[:, :, np.newaxis], N, axis=2)
        print(vel_3d.shape)
        return vel_3d

    @staticmethod
    def compile_rotational_velocities(current_pos, centroid, angle, rot_vel, sampling_time=0.001):
        """
        :param
        current_pos: current position of robots
        [
           [x y], 
           [x y],
           [x y]
        ]

        centroid:    center of rotation
        [ 
            [x],
            [y]

        ]

        angle:       angle to rotate (radians)
        rot_vel:     omega, rotational velocity(rad/s)
        sampling_time:  timestep:
                            (optional)
                            default ==> 0.001 s
        
        Returns a 3D array in the form (num_robots, time_step_n, 2:"x and y")
                                    
        """
        duration = angle/rot_vel
        N_points = int(duration / sampling_time)
        delta_omega = angle / N_points
        rel_current_pos = current_pos.T - np.vstack(centroid)
        delta_x = rel_current_pos[0,:]
        delta_y = rel_current_pos[1,:]
        # theta = np.arctan2(delta_y, delta_x)
        r = np.sqrt(delta_x ** 2 + delta_y ** 2)
        r = np.reshape(r, (1, -1))
        final_matrix = np.zeros((current_pos.shape[0], N_points, current_pos.shape[1]))
        delta_angle = 0
        for i in range (N_points):
            R = np.array([[-math.sin(delta_angle),-math.cos(delta_angle)],[math.cos(delta_angle),-math.sin(delta_angle)]])
            vel = np.round(np.matmul(R, rel_current_pos),5)
            vel = vel * rot_vel 
            vel = vel.T
            final_matrix[:, i, :] = vel
            delta_angle += delta_omega
        return final_matrix


    @staticmethod
    def assign_target_points(current_robot_pos, target_pos):
        """
        Assign each robot to a target:
        Num of robots is determined by the number of points 
        present in target_pos
        Alogrithm is based on 
            : the minimum distance between robots and the target points        
            : looping is carried out for each robot
        :return
            target_posm chosen_robots(their position)
        """
        # num of target points 
        num_robots = current_robot_pos.shape[0]
        num_target_points = target_pos.shape[0]

        # create an empty array to hold average distance from 
        # each target points

        distance = np.zeros((num_robots,num_target_points))

        for index_r, robot_pos in enumerate(current_robot_pos):
            for index_c, target_pos in enumerate(target_pos):
                distance[index_r, index_c] = np.linalg.norm(target_pos - robot_pos)
                
        # find the robots that are closest to each target point
        # make a copy of distance
        distance_copy = np.copy(distance)


        ## Assign the robot closest to each target 
        chosen_robots = np.zeros((num_target_points, 2))

        for index_c in range(num_target_points):
                index_min = distance_copy[:, index_c].argmin()
                chosen_robots[index_c, :] = current_robot_pos[index_min, :]
                ## mask the chosen row to exclude from search
                distance_copy = np.ma.array(distance_copy, mask=False)
                distance_copy.mask[index_min, :] = True
                print("argmin is", index_min)
        return target_pos, chosen_robots


class VelocityHandler(EventDispatcher):
    """
    Handles sending velocity cmds to the bunny
    Ensures that next velocity is sent after previous one has been sent
    Serializes the velocity cmds, and callback can be added when all the 
    velocities have been sent
   
    """



    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.velocity_gen = {}

    def _velocity_callback(self, bunny_uid):
        self.send_cmd(bunny_uid)

    
    def add_velocity(self, bunny, velocities, timestep, callback, *args):
        self.velocity_gen[bunny.id] = [bunny, callback, timestep, (vel for vel in velocities)]

    def send_cmd(self, bunny_uid, mode="real"):
        if self.velocity_gen[bunny_uid] is not None:
            try:
                bunny = self.velocity_gen[bunny_uid][0]
                timestep = self.velocity_gen[bunny_uid][-2]
                vel = next(self.velocity_gen[bunny_uid][-1])
                Clock.schedule_once(partial(bunny.move, 
                                            vel, 
                                            timestep, 
                                            mode, 
                                            False, 
                                            self._velocity_callback), timestep)
            except StopIteration:
                if self.velocity_gen[bunny_uid][1] is not None:
                    self.velocity_gen[bunny_uid][1](bunny_uid)    
            
    def start(self, bunny_uid):
        try:
            self.send_cmd(bunny_uid)
        except:
            return



if __name__ == '__main__':
    # current_pos = np.array([[ 100, 200]])
    # centroid = np.array([[100], [100]])
    # angle = np.pi/2
    # rot_vel = 0.5
    # sampling_time = 0.1745

    # velocities = PathPlanner.compile_rotational_velocities(current_pos, centroid, angle, rot_vel, sampling_time=0.1745)
    # velocities = velocities.tolist()
    # print(velocities[0])

    ## check assign target velocities
    pass
















