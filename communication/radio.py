# should be built on top of Crazyradi
from cflib.drivers.crazyradio import Crazyradio
from kivy.clock import Clock

class Radio(Crazyradio):
    
    def __init__(self, device=None, devid=0, serial=None):
        super().__init__(device, devid, serial)


    def set_channel(self, channel):
        return super().set_channel(channel)

    def set_data_rate(self, datarate):
        return super().set_data_rate(datarate)

    def scan_channels(self, start, stop, packet):
        return super().scan_channels(start, stop, packet)

    def set_address(self, address):
        return super().set_address(address)

    def set_arc(self, arc):
        return super().set_arc(arc)

    def send_packet(self, dataOut):
        return super().send_packet(dataOut)


if __name__ == "__main__":
    import time
    def start_radio(*args):
        print("starting radio!!")
        try:
            radio = Crazyradio()
            print("connection successful!!")
        except Exception as e:
            print(e)
    print("calling!!")
    while True:
        start_radio()
        time.sleep(0.5)

        