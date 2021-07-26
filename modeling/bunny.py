"""
Bunny Robot Class File:
    Class Bunny:
                Creates a bunny robot object
                Simulates the robot's response to a command
                sends data to the robot: Velocity in x and y direction
                methods run asynchronously
    Class State:
                Defines the different states for the robot

"""
import datetime
import math
import random
import numpy as np
import time
from threading import Timer
from random import randint


class _NRF51:
    def __init__(self,callback_on_receiving):
        self._communication_channel = None
        self._state = "active"
        self._callback_on_receiving = callback_on_receiving
        self._transmission_frequency = 1000000           # 1 MHz

    def receive_message(self, message):
        """
        Synchronous function to receive message
        :param message: A dict containing key and value
        :await processing of message
        """
        if self._state != "active":
            return
        self._callback_on_receiving(message)
        time.sleep(1/self._transmission_frequency)

    def stop_transmission(self):
        self._state = "inactive"

    def start_transmission(self):
        self._state = "active"

    @property
    def communication_channel(self):
        return self._communication_channel

    @communication_channel.setter
    def communication_channel(self, channel):
        self._communication_channel = channel

    @property
    def transmission_frequency(self):
        return self._transmission_frequency


class _BunnyWheel:
    """
    Class for Robot Wheel: control each wheel using this class
        :
    """
    def __init__(self, pos, radius, max_forward_velocity):
        self.pos = pos                                 # (angle from forward direction degree,# distance from center cm)
        self.wheel_radius = radius                          # wheel radius cm
        self.max_forward_velocity = max_forward_velocity    # maximum velocity in cm/s


class Bunny:
    """
        Bunny Class:
        :param: channel: Assigned channel to communicate with the robot, "int"
                         uri: Uniform Resource Identifier
                              pos_update_callback: callback when robot changes position
                              state_update_callback: callback when robot changes state
        Define the different states that the robot can be in.
        REACHED_POSITION = "reached position"
        CHARGING = "charging"
        MOVING = "moving"
        IDLE = "idle"
        OFF = "off"
    """
    CHARGING = "charging"
    MOVING = "moving"
    IDLE = "idle"
    DISCHARGED = "discharged"
    OFF = "off"

    def __init__(self, uri, log_data=False):
        self._uri = uri
        self._receiver = _NRF51(self._process_received_message)
        self._dimensions = {"width": 0.12,
                            "length": 0.12,
                            "surface_area": round(0.17**2*np.pi, 3),  # includes 5 cm safety margin
                            "height": 0.10
                            }
        self._wheels = {"front": _BunnyWheel((0, 6), 3, 36.79),
                        "left":  _BunnyWheel((120, 6), 3, 36.79),
                        "right": _BunnyWheel((240, 6), 3, 36.79)
                        }
        self._log_data = log_data
        if self._log_data:
            self._logger = _BunnyLogger(self)
        self._pos_update_callback = None
        self._state_update_callback = None
        self._current_pos = np.array([[0.0], [0.0], [0.0]])       # Normalized x and y, theta
        self._current_velocity = np.array([[0.0], [0.0], [0.0]])  # Vx, Vy, Vth
        self._received_message = None
        self._pos_update_time_step = 1 / self._receiver.transmission_frequency
        self._state = self.IDLE
        self._battery = _BunnyBattery(self)
        self._block_movement = False
        self._timers = None

    def _calculate_pos(self):
        self._move()
        pos_update_timer = Timer(interval=self._pos_update_time_step, function=self._calculate_pos)
        pos_update_timer.name = "pos_update_timer"
        self._timers[pos_update_timer.name] = pos_update_timer
        pos_update_timer.setDaemon(True)
        pos_update_timer.start()

    def start_at_random_position(self):
        """
        starts the robot at a random position
        :return: None
        """
        random.seed()
        x_pos_multiplier = randint(1, 10) / 10.0
        y_pos_multiplier = randint(1, 10) / 10.0
        theta_multiplier = randint(1, 10) / 10.0
        self._current_pos = np.array([[x_pos_multiplier], [y_pos_multiplier], [np.pi*theta_multiplier]])

    def set_callbacks(self, pos_callback, state_callback):
        """
        Set the position callback and state callback
        :param pos_callback: function that is called by bunny when its position changes, the function call is executed
        with two arguments given to the callback(bunny's uri-> str, bunny's position -> np.array)
        :param state_callback: function that is called by bunny when its state changes, the function call is executed
        with two arguments given to the callback(bunny's uri-> str, bunny's state -> str)
        :return: None
        """
        self._pos_update_callback = pos_callback
        self._state_update_callback = state_callback

    def _process_received_message(self, message):
        for key, value in message.items():
            if key == "velocity":
                self._current_velocity = value

    def turn_off_receiver(self):
        """
        Stops the NRF51 from receiving data
        :return: None
        """
        self._receiver.stop_transmission()

    def turn_on_receiver(self):
        """
        turns the NRF51 back on
        :return:
        """
        self._receiver.start_transmission()

    def turn_off(self):
        """
        Turn off the bunny, i.e bunny does not move and
        battery level stays constant
        :return: None
        """
        self._battery.cut_power_from_battery()
        self._block_movement = True
        self._state = self.OFF

    def _send_updates(self, _type="all"):
        if _type == "all":
            if self._log_data:
                self._logger.register_pos_change()
                self._logger.register_state_change()
            self._battery.calculate_depletion()
            if self._pos_update_callback is not None:
                self._pos_update_callback(self._uri, self._current_pos)
            if self._state_update_callback is not None:
                self._state_update_callback(self._uri, self._state)
        elif _type == "pos":
            if self._log_data:
                self._logger.register_pos_change()
            if self._pos_update_callback is not None:
                self._pos_update_callback(self._uri, self._current_pos)
        elif _type == "state":
            if self._log_data:
                self._logger.register_state_change()
            self._battery.calculate_depletion()
            if self._state_update_callback is not None:
                self._state_update_callback(self._uri, self._state)

    def _move(self):
        if self._state == self.DISCHARGED or self._block_movement or self._state == self.OFF:
            return
        theta = self._current_pos[-1][0]
        r_matrix = np.array([[np.cos(theta), -1*np.sin(theta), 0],
                             [np.sin(theta), np.cos(theta), 0],
                             [0, 0, 1]])
        self._current_pos[-1][0] += self._current_velocity[-1][0] * self._pos_update_time_step  # update omega
        x_delta = np.matmul(r_matrix, np.array([[self._current_velocity[0][0]*self._pos_update_time_step], [0], [0]]))
        y_delta = np.matmul(r_matrix, np.array([[0], [self._current_velocity[1][0]*self._pos_update_time_step], [0]]))
        theta_delta = np.array([0, 0, self._current_pos[-1][0]])
        self._current_pos += x_delta + y_delta + theta_delta

    def set_state_to_discharged(self):
        self._state = self.DISCHARGED
        self._send_updates(_type="state")

    def start_charging(self):
        """start the charge routine for the battery"""
        self._state = self.CHARGING
        self._battery.start_charging()

    def stop_charging(self):
        """stops the charging process"""
        self._state = self.IDLE
        self._battery.stop_charging()

    def battery_level(self):
        """
        Returns bunny's current battery status
        :return: None
        """
        return self._battery.battery_level

    @property
    def receiver(self):
        return self._receiver

    @property
    def current_pos(self):
        return self._current_pos

    @property
    def state(self):
        return self._state

    @property
    def uri(self):
        return self._uri

    @property
    def current_velocity(self):
        return self._current_velocity


class _BunnyLogger:
    def __init__(self, robot):
        self._robot = robot

    def register_pos_change(self):
        robot_pos = self._robot.current_pos
        if self._robot.state == self._robot.IDLE:
            print(f"{self._robot.uri} changed position, {robot_pos} {time.strftime('%H:%M:%S')}")

    def register_state_change(self):
        robot_state = self._robot.state
        print(f"{self._robot.uri} changed state, state is now: {robot_state} {time.strftime('%H:%M:%S')}")


class _BunnyBattery:
    def __init__(self, bunny):
        self._bunny = bunny
        self._is_working = True
        self._idle_down_time_timer = None
        self._minimum_battery_level = 0.2
        self._battery_level = 1.0
        self._previous_bunny_state = self._bunny.state
        self._start_time_in_moving_state = None
        self._start_time_in_idle_state = datetime.datetime.now()
        self._down_time_evaluation_handle = False
        self._idle_timer_first_call = True
        self._charge_timer_first_call = True
        self._is_charging = False
        self._charge_timer = None
        self._charge_routine_start_time = None
        self._initial_battery_level_charge_time_buffer = 0.0
        self._evaluate_idle_down_time()

    def calculate_depletion(self):
        """
        Calculates the battery percentage based upon the mode the bunny was, for example if it changed from moving to /
        idle, the battery has a higher depletion rate for that period of time between the two states
        :return: None if battery is near 0.0 and if battery is not connected to bunny
        """
        if self._is_charging:
            return
        elif 0 < self._battery_level < 0.05 or not self._is_working:
            return
        elif self._bunny.state == self._bunny.MOVING and self._previous_bunny_state == self._bunny.IDLE:
            self._start_time_in_moving_state = datetime.datetime.now()
            depletion_rate = 372.8  # battery goes to 0.2 in 6 minutes when moving
            idle_state_end_time = self._start_time_in_moving_state
            t_diff = self._start_time_in_idle_state - idle_state_end_time
            t_diff_in_s = t_diff.total_seconds()
            while self._down_time_evaluation_handle:
                time.sleep(1e-6)
            self._battery_level *= round(math.exp(-t_diff_in_s/depletion_rate), 5)
            self._previous_bunny_state = self._bunny.state
            if self._battery_level <= 0.2:
                self._send_battery_discharged_alert()

        elif self._bunny.state == self._bunny.IDLE and self._previous_bunny_state == self._bunny.MOVING:
            self._start_time_in_idle_state = datetime.datetime.now()
            depletion_rate = 223.68   # battery goes to 0.2 in 10 minutes when idle
            t_diff = self._start_time_in_idle_state - self._start_time_in_moving_state
            t_diff_in_s = t_diff.total_seconds()
            self._battery_level *= round(math.exp(-t_diff_in_s/depletion_rate), 5)
            self._idle_timer_first_call = True
            self._evaluate_idle_down_time()
            self._previous_bunny_state = self._bunny.state
            if self._battery_level <= 0.2:
                self._send_battery_discharged_alert()

    def _evaluate_idle_down_time(self):
        interval = 0.01
        if self._is_charging or (0 < self._battery_level < 0.05 or not self._is_working):
            return
        if self._battery_level <= 0.2:
            self._send_battery_discharged_alert()
        if self._idle_timer_first_call:
            self._idle_down_time_timer = Timer(interval=interval, function=self._evaluate_idle_down_time)
            self._idle_down_time_timer.start()
            self._idle_timer_first_call = False
            return
        self._down_time_evaluation_handle = True
        self._battery_level *= round(math.exp(-interval/ 372.8), 5)
        self._down_time_evaluation_handle = False
        if self._bunny.state == self._bunny.IDLE and self._battery_level > 0.2:
            self._idle_down_time_timer = Timer(interval=interval, function=self._evaluate_idle_down_time)
            self._idle_down_time_timer.start()

    def cut_power_from_battery(self):
        """
        Keeps the battery percentage constant
        :return:
        """
        self._is_working = False

    def _send_battery_discharged_alert(self):
        try:
            self._idle_down_time_timer.cancel()
        except Exception as e:
            pass
        self._bunny.set_state_to_discharged()

    def start_charging(self):
        """
        starts charging the battery, battery level increases as per the charge time
        :return: None
        """
        if self._is_charging:
            return
        self._is_charging = True
        try:
            self._idle_down_time_timer.cancel()
            self._charge_timer.cancel()
        except Exception:
            pass
        self._set_charge_routine()
        self._charge_timer_first_call = True

    def stop_charging(self):
        """
        stops the battery from charging
        :return: None
        """
        if self._is_charging:
            self._is_charging = False
            self._idle_timer_first_call = True
            self._evaluate_idle_down_time()

    def _set_charge_routine(self):
        if self._battery_level >= 0.98:
            return
        elif self._charge_timer_first_call:
            self._charge_routine_start_time = datetime.datetime.now()
            self._initial_battery_level_charge_time_buffer = -1 * math.log(1.0 - self._battery_level) / 0.00652
            self._charge_timer = Timer(interval=0.01, function=self._set_charge_routine)
            self._charge_timer.start()
            self._charge_timer_first_call = False
            return
        elif self._is_charging:
            t_diff = datetime.datetime.now() - self._charge_routine_start_time    # time elapsed
            t_diff = t_diff.total_seconds()                                       # time to seconds
            t_end = t_diff + self._initial_battery_level_charge_time_buffer
            self._initial_battery_level_charge_time_buffer = t_end
            self._battery_level = round((1 - math.exp(-0.00652*t_end)), 5)
            self._charge_timer = Timer(interval=0.01, function=self._set_charge_routine)
            self._charge_timer.start()

    @property
    def battery_level(self):
        return self._battery_level


