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
import asyncio
import numpy as np
import time


class NRF10:
    def __init__(self,callback_on_receiving):
        self._communication_channel = None
        self._state = "active"
        self._callback_on_receiving = callback_on_receiving
        self.transmission_frequency = 100                   # 100 Hz

    async def receive_message(self, message):
        """
        asynchronous function to receive message
        :param message: A dict containing key and value
        :await processing of message
        """
        if self._state != "active":
            return
        await self._callback_on_receiving(message)
        await asyncio.sleep(1/self.transmission_frequency)

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


class RobotWheel:
    """
    Class for Robot Wheel: control each wheel using this class
        :
    """
    def __init__(self, pos, radius, max_forward_velocity):
        self.pos = pos                                      #( angle from forward direction degree,
                                                            # distance from center cm)
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
    """
    REACHED_POSITION = "reached position"
    CHARGING = "charging"
    MOVING = "moving"
    IDLE = "idle"

    def __init__(self, uri, log_data=True):
        self._uri = uri
        self._receiver = NRF10(self._process_received_message)
        self._dimensions = {"width": 0.12,
                            "length": 0.12,
                            "surface_area": round(0.17**2*np.pi, 3),  # includes 5 cm safety margin
                            "height": 0.10
        }
        self._wheels = {"front": RobotWheel((0, 6), 3, 36.79),
                        "left":  RobotWheel((120, 6), 3, 36.79),
                        "right": RobotWheel((240, 6), 3, 36.79)
        }
        self._logger = RobotLogger(self)
        self._pos_update_callback = None
        self._status_update_callback = None
        self._current_pos = np.array([0.0, 0.0, 30.0])     # Normalized x and y, theta
        self._current_velocity = np.array([0.0, 0.0, 0.0]) # Vx, Vy, Vth
        self._received_message = None
        self._time_step = 1 / self._receiver.transmission_frequency
        self._state = self.IDLE

    def start_at_random_position(self):
        """
        Asynchronous function
        starts the robot at a random position
        :return: None
        """
    def set_gui_callbacks(self, pos_change_callback, state_change_callback):
        self._pos_update_callback = pos_change_callback
        self._status_update_callback = state_change_callback

    async def _process_received_message(self, message):
        for key, value in message.items():
            if key == "velocity":
                await self._move(value)

    def turn_off_receiver(self):
        """
        Stops the UWB from receiving data
        :return: None
        """
        self._receiver.stop_transmission()

    def turn_on_receiver(self):
        self._receiver.start_transmission()

    async def _send_pos_update(self):
        await self._logger.register_pos_change()
        if self._pos_update_callback is None:
            return
        self._pos_update_callback(self._current_pos)

    async def _send_status_update(self):
        await self._logger.register_state_change()
        if self._status_update_callback is None:
            return
        self._status_update_callback(self._state)

    async def _move(self, velocity_and_time):
        self._state = self.MOVING
        await self._send_status_update()
        self._current_velocity = velocity_and_time[:-1]
        await asyncio.sleep(velocity_and_time[-1])
        self._current_pos += self._current_velocity*velocity_and_time[-1]
        self._state = self.REACHED_POSITION
        await self._send_pos_update()
        await self._send_status_update()

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

# TO DO:
# Transmission frequency is different from motion frequency
# Find a way to model this


class RobotLogger:
    def __init__(self, robot):
        self._robot = robot

    async def register_pos_change(self):
        robot_pos = self._robot.current_pos
        print(f"{self._robot.uri} changed position, {robot_pos} {time.strftime('%H:%M:%S')}")

    async def register_state_change(self):
        robot_state = self._robot.state
        print(f"{self._robot.uri} changed state, state is now: {robot_state} {time.strftime('%H:%M:%S')}")





