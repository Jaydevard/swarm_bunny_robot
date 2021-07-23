import numpy as np
import asyncio
from robot import Bunny
from Network.network import Network

if __name__ == "__main__":

    async def test():
        network = Network(_id="network1")
        bunny1 = Bunny(uri="bunny1")
        bunny2 = Bunny(uri="bunny2")
        bunny3 = Bunny(uri="bunny3")
        robot_transmitter1 = network.add_robot_to_network(bunny1)
        robot_transmitter2 = network.add_robot_to_network(bunny2)
        robot_transmitter3 = network.add_robot_to_network(bunny3)
        t1 = asyncio.create_task(robot_transmitter1.send_message({"velocity": np.array([0.1, 0.8, 0, 2])}))
        t1_a = asyncio.create_task(robot_transmitter1.send_message({"velocity": np.array([0.1, 0.8, 0, 2.01])}))
        t2 = asyncio.create_task(robot_transmitter2.send_message({"velocity": np.array([0.1, 0.8, 0, 1.5])}))
        t3 = asyncio.create_task(robot_transmitter3.send_message({"velocity": np.array([0.1, 0.8, 0, 1])}))
        await asyncio.gather(t1, t1_a, t2, t3)
        network.remove_robot_from_network(bunny1)
        network.remove_robot_from_network(bunny2)
        network.remove_robot_from_network(bunny3)

    asyncio.run(test())


