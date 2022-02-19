import math
from kivy.clock import Clock
from communication.radio import Radio 
from core.constants import Constants as C
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty
from functools import partial
import random
import numpy as np
from kivy.event import EventDispatcher


class Move(EventDispatcher):

    """
    Moves the robot from A(x,y,th) to B(x,y,th)
    using different path types: linear or circular
    
    """
    def __init__(self, bunny, **kwargs) -> None:
        super(Move, self).__init__(**kwargs)
        self.velocities = []
        self._bunny = bunny
        self._radio: Radio = None
        self._stop_requested = False

    def start(self, callback=None):
        self.run(callback=callback)

    def stop_moving(self):
        self._stop()

    def set_radio(self, radio):
        self._radio = radio
  
    def set_max_speed(self, max_speed):
        self._max_speed = max_speed

    def set_mode(self, mode:str = "real"):
        """
        Either simulation or real
        """
        self._mode = mode

    def set_linear_trajectory(self, 
                              current_pos, 
                              final_pos, 
                              relative_speed
                              ):
        self._velocities = self._sample_linear_velocities(current_pos=current_pos, 
                                                          final_pos=final_pos, 
                                                          relative_speed=relative_speed)
        
    def set_circular_trajectory(self,
                                current_pos,
                                relative_speed,
                                rotation,
                                centroid,
                                sampling_points = 1000,
                                ):
        self._velocities = self._sample_circular_velocities(current_pos=current_pos,
                                                            rotation=rotation,
                                                            sampling_points=sampling_points,
                                                            relative_speed=relative_speed,
                                                            centroid=centroid)

    def _find_start_relative_angle(self, 
                                   pos: list or tuple or np.ndarray, 
                                   center: list or tuple or np.ndarray ): 
                        
        """
        Finds the angle that the specified position
        makes with the centroid specified. 
        This function is used for calculating the offset angle
        required for the rotation( either clockwise or anticlockwise)
        """

        [x, y] = [pos[0] - center[0], pos[1] - center[1]]
        angle = 0
        if float(x) == 0.0 and float(y) == 0.0:
            angle = 0.0

        elif float(x) == 0.0 and float(y) > 0.0:
            angle = math.pi /2

        elif float(x) == 0.0 and float(y) < 0.0:
            angle = 3/2*math.pi 

        else:
            if x > 0:
                if y < 0:
                    angle = 2*math.pi - math.atan(abs(y / x))
                else:
                    angle = math.atan(abs(y / x))
            elif y >= 0:
                    angle = math.pi - math.atan(abs(y / x))

            else:
                angle = math.pi + math.atan(abs(y / x))

        return angle

    def _sample_circular_velocities(self, 
                                    current_pos: np.ndarray or list or tuple, 
                                    sampling_points: int = 1000,
                                    relative_speed: float = 1.0,
                                    rotation: float  = 0.0,
                                    centroid: np.ndarray = None,
                                    ):
        """
        :param
        current_pos: np. array [x, y, th]
        relative_speed: from 0 to 1 (relative to max_speed)
        rotation: in radians
        sampling_points: default(1000) else specified
        centroid: center for circular rotation, 
                  set to None for linear
        returns a generator                

        """
        omega = min(self._max_speed, relative_speed*self._max_speed)
        if omega == 0.0:
            return [0, 0, 0, 0]

        N = sampling_points
        n_end = abs(int(rotation * N / (2*math.pi)))
        r = math.sqrt((current_pos[0] - centroid[0])**2 + (current_pos[1] - centroid[1])**2)
        start_angle = self._find_start_relative_angle(pos=current_pos, center=centroid)
        delta_t = rotation / (n_end*omega)

        # determine rotation direction
        for n in range(0, n_end, 1):
            vx = round(-r*omega*math.sin(  (2*math.pi/N*n) + start_angle), 5)
            if rotation < 0:
                vx *= -1
            vy =  round(r*omega*math.cos( (2*math.pi/N*n) + start_angle), 5)
            yield [vx, vy, 0, delta_t]


    def _sample_linear_velocities(self,
                                  relative_speed: float or int,
                                  current_pos: np.ndarray or list or tuple,
                                  final_pos: np.ndarray or list or tuple,
                                  sampling_time: float = 1/1000,
                                  ):
        """
        Samples the relative velocities:
        relative_speed: 0 to 1,
        current_pos: current position of robot
        final_pos: final_position of robot
        sampling_time: time between each velocities cmd
        """
        if relative_speed == 0:
            yield [0, 0, 0, sampling_time]
            return
        trajectory_angle = self._find_start_relative_angle(center=current_pos, pos=final_pos)
        distance = math.sqrt((final_pos[0] - current_pos[0])**2 + (final_pos[1] - current_pos[1])**2)
        n_velocities = int((distance/(self._max_speed*relative_speed)) / sampling_time)
        print(n_velocities)
        for n in range(n_velocities):
            yield [relative_speed*self._max_speed*math.cos(trajectory_angle), 
                   relative_speed*self._max_speed*math.sin(trajectory_angle), 
                   0, 
                   sampling_time]

    def _send_vel_cmd(self, 
                      bunny: str, 
                      velocity: list or tuple,
                      callback,
                      callback_args,
                      *args):
        self._radio.send_vel_cmd(addr=bunny.addr,
                                velocity=velocity)
        callback(callback_args)

    def _start_moving_in_real(self, callback, *args):
        if self._radio is None:
            return
        try:
            [vx, vy, vth, delta_t] = next(self.velocities)
        except StopIteration:
            callback()
            return
        
        if self._stop_requested:
            self._stop_requested = False
            return

        Clock.schedule_once(partial(self._send_vel_cmd,
                                    self._bunny,
                                    (vx, vy, vth),
                                    self._start_moving_in_real,
                                    callback),delta_t)

    def _change_bunny_pos(self, 
                          bunny,
                          velocity,
                          delta_t,
                          callback,
                          callback_args, 
                          *args):
        diff_x = velocity[0] * delta_t
        diff_y = velocity[1] * delta_t
        bunny.pos_hint = {}
        bunny.pos[0] += diff_x
        bunny.pos[1] += diff_y
        callback(callback_args)

    def _start_moving_in_sim(self, callback, *args):
        try:
            [vx, vy, vth, delta_t] = next(self._velocities)
        except StopIteration:
            if callback:
                callback()
            return

        if self._stop_requested:
            self._stop_requested = False
            return
        
        Clock.schedule_once(partial(self._change_bunny_pos,
                                    self._bunny,
                                    (vx, vy, vth),
                                    delta_t,
                                    self._start_moving_in_sim,
                                    callback), delta_t)

    def run(self, callback):
        if self._velocities is None:
            return
        if self._mode == "simulation":
            self._start_moving_in_sim(callback)
        elif self._mode == "real":
            self._start_moving_in_real(callback)
        else:
            raise Exception("Mode not set!!")

    def _stop(self):
        self._stop_requested = True



class FormationControl:
    
    def __init__(self, **kwargs):
        self._targets = []
        self._pos_buffer = {}

    def on__robot_pos(self, instance, value):
        pass

    def set_radio(self, radio: Radio):
        self.radio = radio


    def _orient_robot_to_target(self, 
                                addr, 
                                current_pos, 
                                final_pos, vtheta=0.8):
        """
        Recalculate using these values
        """

        (x0, y0, th0) = current_pos
        (x1, y1, th1) = final_pos

        velocity = 10
        rot_vel = 0.8
        velocity_x = 0
        velocity_y = 0
        self.final_x = 0
        self.final_y = 0
        self.final_omega = 0

        delta_x = self.final_x-self.current_x
        delta_y = self.final_y-self.current_x
        dis= math.sqrt(abs(delta_x * delta_x + delta_y * delta_y))

        zetha = math.atan((self.y1 - self.y) / (self.x1 - self.x))
        alpha = self.theta_robot - zetha
        t_omega = alpha/rot_vel
        self.final_x = 0
        self.final_y = 0
        self.final_omega = rot_vel
        velocity_x = 0
        velocity_y = 0
        print(velocity_x,velocity_y,rot_vel)

    def _get_robot_velocity(self, current_pos, final_pos):
        """
        Returns (Vx, Vy, vth, interval) for robot

        """
        (x0, y0, th0) = current_pos
        (x1, y1, th1) = final_pos
        delta_x = x1 - x0
        delta_y = y1 - y0
        dis= math.sqrt(abs(delta_x * delta_x + delta_y * delta_y))
        alpha = th0 - th1
        pass

    def _verify_target_reached(self, addr, callback, *args):
        """
        Target Reached Check!
        """
        for index, target in enumerate(self._targets):
            if target[0] == addr:
                if target[1] == False:
                    callback(False)
                    target[4].cancel()
                    del self._targets[index]
                else:
                    del self._targets[index]

    def move_robot_to_target(self, 
                            addr: str, 
                            final_pos: list,
                            callback_on_reached: __module__,
                            timeout: int =0):
        """
        Schedule this function to run 
        using Kivy.Clock
        
        """
        # Check whether robot is still moving to target
        if self.radio is None:
            callback_on_reached(False)
            return

        self._pos_buffer[addr] = []
        
        # get initial pos of robot
        robot_status = self.radio.send_vel_cmd(addr, 0, 0, 0)
        initial_pos = robot_status[-1]

        vel_event =  Clock.schedule_interva(partial(self._send_velocity_cmd, len(self._targets)),
                                            1)
        self._targets.append([addr,         # addr
                              initial_pos,  
                              final_pos,
                              [0, 0, 0],    # velocity
                              vel_event,    
                              False,
                              callback_on_reached])       # target_reached

        self._orient_robot_to_target(len(self._targets)-1)
        vel_event()


        if timeout != 0:
            Clock.schedule_once(partial(self._verify_target_reached, addr, 
                                        callback_on_reached), timeout)


    def _send_velocity_cmd(self, index, *args):
        if self.radio is None:
            return False

       
        addr = self._targets[index][0]
        [Vx, Vy, Vth] = self._targets[index][3]
        final_pos = self._targets[2]

        # send same velocity to get current pos
        return_status = self.radio.send_vel_cmd(addr, [Vx, Vy, Vth])
        current_pos = return_status[-1]

        reached = self._verify_final_pos_reached(index)
        if reached:
           self._targets[-1](True)
           self._targets[5] = True
           return False

        # calculate next velocity required
        [Vx, Vy, Vth, interval] = self._get_robot_velocity(current_pos, final_pos)
        self._targets[index][3] = [Vx, Vy, Vth]
        # send next velocity 
        self.radio.send_vel_cmd(addr, [Vx, Vy, Vth])
        self._targets[index][4].cancel()
        vel_event =  Clock.schedule_interval(partial(self._send_velocity_cmd, 
                                                    index), interval)
        self._targets[index][4] = vel_event
        vel_event()


    def check_velocity_cmd(self, test_size, final_pos):
        count = 0
        while count < test_size:
            random.seed(0)
            x = random.randrange(0, 5000, 1)
            y = random.randrange(0, 5000, 1)
            theta = random.randrange(0, 2*math.pi, math.pi/180)
            current_pos = (x, y, theta)
            [Vx, Vy, Vtheta, interval] = self._get_robot_velocity(current_pos,
                                                                  final_pos)
            print(f"current_pos is: {current_pos}  final_pos is: {final_pos}", end="")
            print(f"velocities recieved are: Vx:{Vx}, Vy:{Vy}, Vtheta:{Vtheta}, interval:{interval}") 
            count += 1

    

    def test_algo(self,test_size=10):

        velocities = self.sample_velocity(current_pos=current_pos,
                                          rotation=(2*math.pi),
                                          duration = 20,
                                          path_type="circular",
                                          centroid=(0,0))
        return velocities



if __name__ == "__main__":
    f_control = FormationControl()














