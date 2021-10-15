import usb
from cflib.drivers import crazyradio
from cflib.drivers import cfusb

""" Code from Nushen to communicate with the robot
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
#import argparse

#import matplotlib.pyplot as plt
#import numpy as np

import drivers.crazyradio as crazyradio

radio = crazyradio.Crazyradio()

channel = 40
TRY = 11
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


uri='radio://0/30/2M/E7E7E7E711'
address='54321'

radio.set_address(address)

for i in range(TRY):
    pk = radio.send_packet((0xf1, )) #this message will be received by the robot.
    if pk.ack:
        count += 1
        #print(pk.data)
        print(str(pk.data,'UTF-8'))


ack_rate = count / TRY


print('Channel', channel, 'ack_rate:', ack_rate)
     # 'rssi average:', rssi_avg, 'rssi std:', std)
     
"""


if __name__ == "__main__":
    cfusb.CfUsb()
