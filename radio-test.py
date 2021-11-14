# Eric Yihan Chen
# The Automatic Coordination of Teams (ACT) Lab
# University of Southern California
# ericyihc@usc.edu
'''
    Simple example that connects to the first Crazyflie found, triggers
    reading of rssi data and acknowledgement rate for every channel (0 to 125).
    It finally sets the Crazyflie channel back to default, plots link
    quality data, and offers good channel suggestion.

    This script should be used on a Crazyflie with bluetooth disabled and RSSI
    ack packet enabled to get RSSI feedback. To configure the Crazyflie in this
    mode build the crazyflie2-nrf-firmware with
    ```make BLE=0 CONFIG=-DRSSI_ACK_PACKET```.
    See https://github.com/bitcraze/crazyflie-lib-python/issues/131 for more
    informations.
'''
# import argparse

# import matplotlib.pyplot as plt
# import numpy as np

# from pynput.keyboard import Key, Listener

from time import sleep
import keyboard
from struct import *

import drivers.crazyradio as crazyradio

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
address = ['54321', '54322','54323']


# for i in range(TRY):
#     responce = radio.send_packet((0xf1, )) #this message will be received by the robot.
#     if responce.ack:
#         count += 1
#         #print(responce.data)
#         print(str(responce.data,'UTF-8'))
# ack_rate = count / TRY
# print('Channel', channel, 'ack_rate:', ack_rate)
#      # 'rssi average:', rssi_avg, 'rssi std:', std)

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
    header = b'\xF0'
    velocity_command = header+pack('fff', vx, vy, vth)
    #print(velocity_command)
    for addr in address:
        radio.set_address(addr)
        responce = radio.send_packet(velocity_command)  # this message will be received by the robot.
        if responce.ack:
            print(str(responce.data, 'UTF-8'))

    sleep(0.01)
