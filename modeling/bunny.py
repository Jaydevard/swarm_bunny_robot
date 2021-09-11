"""
Bunny Robot Class File:
    Class Bunny:
                Creates a bunny robot object
                Simulates the robot's response to a command
                sends data to the robot: Velocity in x and y direction
                methods run asynchronously
    States:
                Defines the different states for the robot
"""

import datetime
import math
import os
import random
import numpy as np
import time
from threading import Timer
from random import randint
from kivy.uix.widget import Widget
from kivy.graphics import Ellipse, Line, Bezier


class _NRF51:
    def __init__(self, callback_on_receiving):
        self._communication_channel = None
        self._state = "active"
        self._callback_on_receiving = callback_on_receiving
        self._transmission_frequency = 100000.0  # 1 MHz

    def receive_message(self, message):
        """
        Synchronous function to receive message
        :param message: A dict containing key and value
        :await processing of message
        """
        if self._state != "active":
            return
        self._callback_on_receiving(message)
        time.sleep(1.0 / self._transmission_frequency)

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
        self.pos = pos  # (angle from forward direction degree,# distance from center cm)
        self.wheel_radius = radius  # wheel radius cm
        self.max_forward_velocity = max_forward_velocity  # maximum velocity in cm/s


class Bunny:
    """
        Bunny Class:
        :param: : uri: Uniform Resource Identifier
                  log_data: default is False, creates a log for bunny when set to True
                  (OPTIONAL) pos_update_callback: callback when robot changes position
                  (OPTIONAL) state_update_callback: callback when robot changes state
        Define the different states that the robot can be in.
        REACHED_POSITION = "reached position"
        CHARGING = "charging"
        MOVING = "moving"
        IDLE = "idle"
        OFF = "off"
        ZERO_VELOCITY = np.array([0.0], [0.0], [0.0])
    """
    CHARGING = "charging"
    MOVING = "moving"
    IDLE = "idle"
    OFF = "off"
    ZERO_VELOCITY = np.array([[0.0],
                              [0.0],
                              [0.0]])

    def __init__(self, uri, log_data=False, **kwargs):
        self._uri = uri
        self._receiver = _NRF51(self._process_received_message)
        self._dimensions = {"width": 12.0,  # cm
                            "length": 12.0,
                            "surface_area": round(17.0 ** 2 * np.pi, 3),  # includes 5 cm safety margin
                            "height": 10.0
                            }
        self._wheels = {"front": _BunnyWheel((0.0, 6.0), 3.0, 36.79),
                        "left": _BunnyWheel((120.0, 6.0), 3.0, 36.79),
                        "right": _BunnyWheel((240.0, 6.0), 3.0, 36.79)
                        }
        self._log_data = log_data
        self._pos_update_callback = kwargs.get('pos_update_callback')
        self._state_update_callback = kwargs.get('state_update_callback')
        self._current_pos = np.array([[0.0], [0.0], [np.pi / 2.0]])  # Normalized x and y, theta
        self._current_pos = np.round(self._current_pos, 7)
        self._current_velocity = self.ZERO_VELOCITY  # Vx, Vy, Vth
        self._update_attributes_time_step = 1.0 / 1000.0
        self._state = self.IDLE
        self._battery = _BunnyBattery(self)
        self._battery_low_flag = False
        self._block_movement = False
        self._timers = {}
        self._current_time = datetime.datetime.now()
        self._logger = _BunnyLogger(self)
        if self._log_data:
            self._log_bunny_data()
        self._update_attributes()

    def _update_attributes(self):
        self._move()
        update_attributes_timer = Timer(interval=self._update_attributes_time_step, function=self._update_attributes)
        update_attributes_timer.name = "update_states_timer"
        self._timers[update_attributes_timer.name] = update_attributes_timer
        update_attributes_timer.setDaemon(True)
        self._current_time = datetime.datetime.now()
        update_attributes_timer.start()

    async def _async_update_attributes(self):
        pass

    def start_at_random_position(self, dimension: tuple):
        """
        starts the robot at a random position,
        :param dimension: tuple for (x, y) dimension in cm
        :return: None
        """
        random.seed()
        x_pos_multiplier = randint(2, 8) / 10.0 * dimension[0]
        y_pos_multiplier = randint(2, 8) / 10.0 * dimension[1]
        theta_multiplier = randint(1, 10) / 10.0
        self._current_pos = np.array([[x_pos_multiplier], [y_pos_multiplier], [np.pi * theta_multiplier]])
        self._current_pos = np.round(self._current_pos, 7)

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

    def _process_received_message(self, message: dict):
        for key, value in message.items():
            if key == "velocity":
                self._current_velocity = value
            elif key == "state":
                self._state = value

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

    def _send_updates_to_callbacks(self, _type="all"):
        if _type == "all":
            if self._pos_update_callback is not None:
                self._pos_update_callback(self._uri, self._current_pos)
            if self._state_update_callback is not None:
                self._state_update_callback(self._uri, self._state)
        elif _type == "pos":
            if self._pos_update_callback is not None:
                self._pos_update_callback(self._uri, self._current_pos)
        elif _type == "state":
            if self._state_update_callback is not None:
                self._state_update_callback(self._uri, self._state)

    def _move(self):
        if self._block_movement or self._state == self.OFF or self._state == self.CHARGING:
            return
        elif np.array_equal(self.ZERO_VELOCITY, self._current_velocity):
            self._state = self.IDLE
            return
        else:
            self._state = self.MOVING
            theta = self._current_pos[-1][0]
            r_matrix = np.array([[np.cos(theta), -1 * np.sin(theta), 0.0],
                                 [np.sin(theta), np.cos(theta), 0.0],
                                 [0.0, 0.0, 1.0]])
            t_diff = (datetime.datetime.now() - self._current_time).total_seconds()
            self._current_pos[-1][0] += self._current_velocity[-1][0] * self._update_attributes_time_step
            x_delta = np.matmul(r_matrix, np.array([[self._current_velocity[0][0] * t_diff],
                                                   [0.0],
                                                   [0.0]]))
            y_delta = np.matmul(r_matrix, np.array([[0],
                                                   [self._current_velocity[1][0] * t_diff],
                                                   [0.0]]))
            self._current_pos += x_delta + y_delta
            self._current_pos = np.round(self._current_pos, 7)

    def set_state_to_discharged(self):
        self._battery_low_flag = True

    def start_charging(self):
        """start the charge routine for the battery"""
        self._state = self.CHARGING
        self._current_velocity = self.ZERO_VELOCITY
        self._battery.start_charging()

    def stop_charging(self):
        """stops the charging process"""
        self._state = self.IDLE
        self._battery.stop_charging()

    def battery_level(self):
        """
        Returns bunny's current battery level
        :return: None
        """
        return self._battery.battery_level

    def stop_bunny_from_moving(self):
        """
        stops bunny from moving, sets its state to IDLE
        :return: None
        """
        self._block_movement = True
        self._current_velocity = self.ZERO_VELOCITY
        self._state = self.IDLE

    def _log_bunny_data(self):
        self._logger.log_data()
        log_data_timer = Timer(interval=0.01, function=self._log_bunny_data)
        log_data_timer.name = "log_data_timer"
        self._timers[log_data_timer.name] = log_data_timer
        log_data_timer.setDaemon(True)
        log_data_timer.start()

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
    def battery_low_flag(self):
        return self._battery_low_flag

    @property
    def current_velocity(self):
        return self._current_velocity


class _BunnyLogger:
    def __init__(self, robot):
        self._robot = robot
        self._file_path = os.getcwd() + f"//{self._robot.uri}.csv"

    def log_data(self):
        with open(self._file_path, "a") as log_file:
            log_file.write(f"{self._robot.current_pos[0][0]}, {self._robot.current_pos[1][0]}, "
                           f"{self._robot.current_pos[2][0]}, "
                           f"{self._robot.battery_level()}\n")
        log_file.close()


class _BunnyBattery:
    def __init__(self, bunny):
        self._bunny = bunny
        self._is_delivering_power = True
        self._minimum_battery_level = 0.2
        self._battery_level = 1.0
        self._battery_level_depletion_calculation_timer_interval = 1.0 / 10.0
        self._battery_level_depletion_calculation_timer = None
        self._previous_bunny_state = self._bunny.state
        self._is_charging = False
        self._charge_routine_start_time = None
        self._charge_timer_first_call = True
        self._initial_battery_level_charge_time_buffer = 0.0
        self._charge_timer = None
        self._calculate_depletion()

    def _calculate_depletion(self):
        current_bunny_state = self._bunny.state
        if not self._is_delivering_power:
            return
        # keep the battery level constant when battery is near zero or charging
        elif 0 <= self._battery_level <= 0.05 or self._is_charging:
            self._previous_bunny_state = current_bunny_state
            self._battery_level_update_timer = Timer(interval=self._battery_level_depletion_calculation_timer_interval,
                                                     function=self._calculate_depletion)
            self._battery_level_update_timer.setName("battery_level_update_timer")
            self._battery_level_update_timer.start()
            return
        else:
            # if bunny is still idle or changed state from IDLE to MOVING
            if self._previous_bunny_state == self._bunny.IDLE and current_bunny_state == self._bunny.IDLE or \
                    self._previous_bunny_state == self._bunny.IDLE and current_bunny_state == self._bunny.MOVING:
                self._down_time_evaluation_handle = True
                self._battery_level *= math.exp(-self._battery_level_depletion_calculation_timer_interval / 372.8)
                self._battery_level = round(self._battery_level, 5)
                self._down_time_evaluation_handle = False

            # if bunny was moving and now is idle or is still moving
            if self._previous_bunny_state == self._bunny.MOVING and self._bunny.state == self._bunny.IDLE or \
                    self._previous_bunny_state == self._bunny.MOVING and self._bunny.state == self._bunny.MOVING:
                self._down_time_evaluation_handle = True
                self._battery_level *= math.exp(-self._battery_level_depletion_calculation_timer_interval / 223.68)
                self._battery_level = round(self._battery_level, 5)
                self._down_time_evaluation_handle = False
            if self._battery_level <= self._minimum_battery_level:
                self._set_battery_discharged_flag()
            self._previous_bunny_state = current_bunny_state
            self._battery_level_update_timer = Timer(interval=self._battery_level_depletion_calculation_timer_interval,
                                                     function=self._calculate_depletion)
            self._battery_level_update_timer.setName("battery_level_update_timer")
            self._battery_level_update_timer.start()

    def cut_power_from_battery(self):
        """
        Keeps the battery percentage constant
        :return: None
        """
        self._is_delivering_power = False

    def turn_power_on(self):
        """
        Turns the power back on
        :return:
        """
        self._is_delivering_power = True
        self._calculate_depletion()

    def _set_battery_discharged_flag(self):
        self._bunny.battery_low_flag = True

    def start_charging(self):
        """
        starts charging the battery, battery level increases as per the charge time
        :return: None
        """
        if self._is_charging:
            return
        self._is_charging = True
        try:
            self._battery_level_depletion_calculation_timer.cancel()
            self._charge_timer.cancel()
        except Exception as e:
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
            t_diff = datetime.datetime.now() - self._charge_routine_start_time  # time elapsed
            t_diff = t_diff.total_seconds()  # time to seconds
            t_end = t_diff + self._initial_battery_level_charge_time_buffer
            self._initial_battery_level_charge_time_buffer = t_end
            self._battery_level = round((1 - math.exp(-0.00652 * t_end)), 5)
            self._charge_timer = Timer(interval=0.01, function=self._set_charge_routine)
            self._charge_timer.start()

    @property
    def battery_level(self):
        return self._battery_level




