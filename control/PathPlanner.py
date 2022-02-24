import math
import numpy as np
from kivy.clock import Clock
from kivy.event import EventDispatcher


class PathPlanner(EventDispatcher):
    def __init__(self, **kw):
        super().__init__(**kw)

    @staticmethod
    def compile_linear_velocities(current_pos, final_pos, duration, sampling_time):
        """
        :param
            current_pos: current position 
            final_pos:   final position
            duration:    time of travel(s)
            sampling time: timestep(s)
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
        centroid:    center of rotation
        angle:       angle to rotate (radians)
        rot_vel:     omega, rotational velocity(rad/s)
        sampling_time:  timestep:
                            (optional)
                            default ==> 0.001 s
        
        """
        duration = angle/rot_vel
        N_points = int(duration / sampling_time)
        delta_omega = angle / N_points
        print(centroid.shape, current_pos.shape)
        rel_current_pos = current_pos.T - np.vstack(centroid)
        print(current_pos, rel_current_pos)
        delta_x = rel_current_pos[0,:]
        delta_y = rel_current_pos[1,:]
        theta = np.arctan2(delta_y, delta_x)
        r = np.sqrt(delta_x ** 2 + delta_y ** 2)
        r_w = r * rot_vel
        current_pos = current_pos.T
        print(r_w, delta_x, delta_y)
        print(r_w.shape, delta_x.shape, delta_y.shape)
        final_matrix = np.zeros((*current_pos.shape, N_points))
        for i in range (N_points):
            angle -=delta_omega
            R_ = np.array([[-math.sin(angle),-math.cos(angle)],[math.cos(angle),-math.sin(angle)]])
            vel = np.round( R_.dot(current_pos),3)
            vel = vel *r_w
            final_matrix[:, :, i] = vel
        return final_matrix




if __name__ == '__main__':
    pass



















