import numpy as np
from network import Network
from bunny import Bunny
import time


def send_velocity_command(transmitters, velocity: dict):
    if type(transmitters) is list:
        threads = [transmitter.request_message_thread(velocity) for transmitter in transmitters]
        [thread.start() for thread in threads]
    else:
        t1 = transmitters.request_message_thread(velocity)
        t1.start()


if __name__ == "__main__":
    bunnies = [Bunny(f"bunny{i}", log_data=True) for i in range(1, 4, 1)]
    nt1 = Network(_id="nt1")
    transmitters = nt1.add_robots_to_network(*bunnies)
    velocity = {"velocity": np.array([[5.0],
                                      [0.0],
                                      [0.0]])}    # Vx, Vy, omega (Robot Frame)
    send_velocity_command(transmitters, velocity)
    # moving forward
    time.sleep(3)
    velocity = {"velocity": np.array([[0.0],
                                      [0.0],
                                      [0.5]])}
    send_velocity_command(transmitters[0], velocity)
    # bunny1 makes an anticlockwise turn while other bunnies keep moving forward
    time.sleep(2)
    velocity = {"velocity": np.array([[0.0],
                                      [5.0],
                                      [0.0]])}
    send_velocity_command(transmitters, velocity)
    # all bunnies turn left
    time.sleep(6)
    velocity = {"velocity": np.array([[0.0],
                                      [0.0],
                                      [0.0]])}
    # bunnies stop moving for 10s
    send_velocity_command(transmitters, velocity)
    time.sleep(10)
    # charge the batteries of bunny for 5 seconds
    [bunny.start_charging() for bunny in bunnies]
    time.sleep(5)
    # let bunny stay idle for 5 s
    [bunny.stop_charging() for bunny in bunnies]
    time.sleep(5)
    # turn off the bunny
    [bunny.turn_off() for bunny in bunnies]







