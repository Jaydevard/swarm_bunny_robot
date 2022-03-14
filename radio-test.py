
from time import sleep
import keyboard
from struct import *
import drivers.crazyradio as crazyradio


def send_velocity_command(radio, addr, velocity):
    header = b'\x30'  # velocity command header as CRTP
    velocity_command = header + pack('fff', velocity[0], velocity[1], velocity[2])
    radio.set_address(addr)
    response = radio.send_packet(velocity_command)  # this message will be received by the robot.
    if response.ack and len(response.data)==13:
        state = response.data[0] & 0xF0
        state = state >> 4
        battery_level = response.data[0] & 0x0F
        actual_position = unpack('fff', response.data[1:])
    else:
        actual_position = (float('nan'), float('nan'), float('nan'))
        state = 'nan'
        battery_level ='nan'
    return state,battery_level,actual_position

    # state bit  0:3 :
    #             init_state = 0x0,
    #             magcalibration_state = 0x1,
    #             idle_state = 0x2,
    #             run_state = 0x3,
    #             gotocharge_state = 0x4,
    #             charging_state = 0x5,
    #             sleep_state = 0x6,
    #
    #             error_state = 0xE,
    #             debug_state = 0xF

    # state bit  4:7 : battery level in 16 levels



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
    address = ["LGN01"]
    # while (1):
    #     vx = 0
    #     vy = 0
    #     vth = 0
    #     if keyboard.is_pressed("w"):
    #         vx = vx + 10
    #         # print("up arrow")
    #     if keyboard.is_pressed("s"):
    #         vx = vx - 10
    #         # print("down arrow")
    #     if keyboard.is_pressed("a"):
    #         vy = vy + 10
    #         # print("left arrow")
    #     if keyboard.is_pressed("d"):
    #         vy = vy - 10
    #         # print("right arrow")
    #     if keyboard.is_pressed("q"):
    #         vth = vth + 1
    #         # print("ccw")
    #     if keyboard.is_pressed("e"):
    #         vth = vth - 1
    #         # print("cw")
    #     if keyboard.is_pressed("space"):
    #         print("space")
    #         break


    while True:

        for addr in address:
            print(addr)
            for i in range(1000):
                velocity = (-10, 0, 00) #cm/s, cm/s, deg/s
                #velocity = (-1.0, 0.0, 0.0)
                state,battery_level, actual_position = send_velocity_command(radio, addr, velocity)
                print(state)
                print(actual_position)
                print(battery_level)
                sleep(0.01)
            sleep(5)
            for i in range(1000):
                velocity = (10, 0, 00) #cm/s, cm/s, deg/s
                #velocity = (-1.0, 0.0, 0.0)
                state,battery_level, actual_position = send_velocity_command(radio, addr, velocity)
                print(state)
                print(actual_position)
                print(battery_level)
                sleep(0.01)
            break
        break
            
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









