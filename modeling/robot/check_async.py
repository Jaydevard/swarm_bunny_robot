__all__ = ['create_robot_positions']

import datetime
from robot_simulation import BunnySim
import asyncio
import os
import random
import numpy as np


FILE_PATH = os.getcwd()+"//robot_positions.csv"


async def create_robot_positions(num_robots):
    with open(FILE_PATH, 'w') as robot_positions:
        for robot_index in range(num_robots):
            x_pos = random.randint(0, 50)
            y_pos = random.randint(0, 50)
            robot_positions.write(f"Robot{robot_index+1}:{x_pos},{y_pos}\n")


async def read_robot_positions():
    robot_positions = {}
    with open(FILE_PATH, 'r') as robot_positions_file:
        for robot_position in robot_positions_file:
            robot, pos = robot_position.strip().split(":")
            robot_positions[robot] = {"x_pos": pos.split(",")[0],
                                      "y_pos": pos.split(",")[1]}
    return robot_positions


async def print_something():
    i = datetime.datetime.now()
    print(f"what{i}")
    await asyncio.sleep(1)


async def write_and_read(bunny, num_robots=50):
    await create_robot_positions(num_robots)
    robot_positions = await read_robot_positions()
    for pos in robot_positions.values():
        await asyncio.create_task(bunny.update_bunny_position(np.array([pos['x_pos'], pos['y_pos']])))


if __name__ == "__main__":
    async def main():
        bunnies = []
        bunny_pos_tasks = []
        for bunny_index in range(300):
            bunnies.append(BunnySim(id=f'Bunny{bunny_index+1}', current_pos=np.array([0,0])))
        for bunny in bunnies:
            bunny_pos_tasks.append(asyncio.create_task(write_and_read(bunny, 30)))
            await bunny_pos_tasks[-1]
        for bunny in bunnies:
            print(bunny.id, bunny.current_pos)

    asyncio.run(main())
