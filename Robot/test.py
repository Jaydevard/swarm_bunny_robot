import numpy as np
import asyncio
from robot import Bunny
from network import Network

if __name__ == "__main__":

    async def test():
        network = Network()
        bunny1 = Bunny(uri="bunny1")
        bunny2 = Bunny(uri="bunny2")
        bunny3 = Bunny(uri="bunny3")
        robot_transmitter1 = network.add_robot_to_network(bunny1)
        robot_transmitter2 = network.add_robot_to_network(bunny2)
        robot_transmitter3 = network.add_robot_to_network(bunny3)
        t1 = asyncio.create_task(robot_transmitter1.send_message({"velocity": np.array([0.1, 0.8, 1.6, 2])}))
        t1_a = asyncio.create_task(robot_transmitter1.send_message({"velocity": np.array([0.1, 0.8, 1.6, 2.01])}))
        t2 = asyncio.create_task(robot_transmitter2.send_message({"velocity": np.array([0.1, 0.8, 1.6, 1.5])}))
        t3 = asyncio.create_task(robot_transmitter3.send_message({"velocity": np.array([0.1, 0.8, 1.6, 1])}))
        await asyncio.gather(t1, t1_a, t2, t3)

    asyncio.run(test())


