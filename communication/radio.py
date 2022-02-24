# should be built on top of Crazyradi
from distutils import core
from os import stat
from cflib.drivers.crazyradio import Crazyradio
import cflib.drivers.crazyradio as CR
from kivy.clock import Clock
from struct import pack, unpack
from core.constants import Constants as C

class Radio(Crazyradio):
    
    def __init__(self, device=None, devid=0, serial=None):
        super().__init__(device, devid, serial)

    def get_serial_nums(self):
        """
        return the serial numbers
        """
        return CR.get_serials()

    def _find_devices(self):
        """
        finds the radio dongles
        """
        return CR._find_devices()

    def send_vel_cmd(self, addr, velocity, *args):
        header = b'\x30'  # velocity command header as CRTP
        velocity_command = header + pack('fff', velocity[0], velocity[1], velocity[2])
        self.set_address(addr)
        response = self.send_packet(velocity_command)  # this message will be received by the robot.
        if response.ack and len(response.data)==13:
            state = response.data[0] & 0xF0
            battery_level = response.data[0] & 0x0F
            actual_position = unpack('fff', response.data[1:])
        else:
            actual_position = (None, None, None)
            state = None
            battery_level = None
        print(state, battery_level, actual_position)

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
    pass
        

        
        