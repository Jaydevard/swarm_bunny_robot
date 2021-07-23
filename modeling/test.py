from bunny import Bunny
import time
if __name__ == "__main__":

    bunny1 = Bunny(uri="bunny1")
    print(bunny1.battery_status())
    time.sleep(200)
    print("Have remained idle for 200s")
    print(bunny1.battery_status())
    print("Let's charge battery for 2 minutes!")
    bunny1.start_charging()
    time.sleep(120)
    bunny1.stop_charging()
    print("Battery has been charged")
    print(bunny1.battery_status())
    print("let's stay idle again for 2 minutes!")
    time.sleep(120)
    print(bunny1.battery_status())
    print("turning off")
    bunny1.turn_off()




    # bunnies = [Bunny(uri=f"bunny{index}", log_data=True) for index in range(1, 5, 1)]
    # space = Space()
    # space.add_robot_to_space(*bunnies)
    # nt1 = Network(_id="network1")
    # space.add_network_to_space(nt1)
    # transmitters = nt1.add_robots_to_network(*bunnies)
    # message = {"velocity": np.array([0.5, 0.5, 0.785, 0.2])}
    # threads = [transmitter.request_message_thread(message) for transmitter in transmitters]






