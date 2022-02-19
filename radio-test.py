
from time import sleep
import keyboard
from struct import *

import drivers.crazyradio as crazyradio


def send_velocity_command(radio, addr, velocity):
    header = b'\x30'  # velocity command header as CRTP
    velocity_command = header + pack('fff', velocity[0], velocity[1], velocity[2])
    radio.set_address(addr)
    response = radio.send_packet(velocity_command)  # this message will be received by the robot.
    if response.ack:
        state = response.data[0]
        actual_position = unpack('fff', response.data[1:])
        # print(actual_position)
        # print(str(response.data, 'UTF-8'))
    else:
        actual_position = (float('nan'), float('nan'), float('nan'))
        state = 0x00
    return state,actual_position

    # state bit  0:1 :    0=idle/ready
    #                     1=running
    #                     2=charging
    #                     3=error

    # state bit  2:4 : battery level in 8 levels

    # state bit  5:7 : error status
    #                     0=no error
    #                     1=battery low
    #                     2=localization filter unstable
    #                     3=motor driver communication failed
    #                     4=compass communication failed
    #                     5=uwb communication failed
    #                     6=
    #                     7=


if __name__ == "__main__":
    radio = crazyradio.Crazyradio()
    channel = 40
    data_rate = 2  # 2 mbps
    radio.set_channel(channel)
    radio.set_data_rate(data_rate)
    SET_RADIO_CHANNEL = 1
    rssi_std = []
    rssi = []
    ack = []
    radio.set_arc(0)

    count = 0
    temp = []

    uri = 'radio://0/30/2M/E7E7E7E711'
    address = ['54321', '54322', '54323']


    while (1):
        vx = 0
        vy = 0
        vth = 0
        if keyboard.is_pressed("w"):
            vx = vx + 10
            # print("up arrow")
        if keyboard.is_pressed("s"):
            vx = vx - 10
            # print("down arrow")
        if keyboard.is_pressed("a"):
            vy = vy + 10
            # print("left arrow")
        if keyboard.is_pressed("d"):
            vy = vy - 10
            # print("right arrow")
        if keyboard.is_pressed("q"):
            vth = vth + 1
            # print("ccw")
        if keyboard.is_pressed("e"):
            vth = vth - 1
            # print("cw")
        if keyboard.is_pressed("space"):
            print("space")
            break

        for addr in address:
            velocity = (vx, vy, vth)
            state, actual_position = send_velocity_command(radio, addr, velocity)
            print(state)
            print(actual_position)

            # state bit  0:1 :    0=idle/ready
            #                     1=running
            #                     2=charging
            #                     3=error

            # state bit  2:4 : battery level in 8 levels

            # state bit  5:7 : error status
            #                     0=no error
            #                     1=battery low
            #                     2=localization filter unstable
            #                     3=motor driver communication failed
            #                     4=compass communication failed
            #                     5=uwb communication failed
            #                     6=
            #                     7=




        # sleep(0.01)
        sleep(0.5)



