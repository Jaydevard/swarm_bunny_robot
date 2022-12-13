"""
Author: Jaydev Madub
Date: 7 November 2022
"""
from pathlib import Path
import os
from kivy.clock import Clock
import cflib.drivers.crazyradio as CR
import queue
from core.exceptions import *


class SignalBuffer(queue.Queue):
    """
    Helper Class to send and receive signals 
    from radio
    Due to the serial nature of the connection:
        ==> Data is best sent in a queue buffer
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class NetworkManager():
    """
    Network Manager:
        ==> Takes care of the Radio Class configuration
        ==> Takes care of checking the Target Link status
        ==> Takes care of handling and receiving data from the targets
    """
    def __init__(self, cls) -> None:
        self.__DIR__ = Path(os.path.dirname(os.path.realpath(__file__)))
        
        # Radio Object
        self._radio = None
        
        # Radio Link Status
        self._RADIO_CONNECTED = False
        self._SEND_PACKET = True
        self._send_buffer = SignalBuffer(maxsize=10)

        # Data Flow Control CONSTANTS
        # Initialized from the Config file
        self._COMM_LINK_TRANSFER_RATE = None   # per 100 ms
        self._RADIO_CHECK_INTERVAL = None
        self._CHANNEL = None
        self._DATA_RATE = None
        self._ARC = None
        self._ADDR_PREFIX = None

        # Load the Radio configs and set the vairables
        self._configs = self._load_config()
        self._set_variables()


        # use this link to communicate back to the GUI front-end
        # In this case, it would be the Connection class's object
        self._connection_cls = cls

        # Establish Radio Link
        Clock.schedule_interval(self._connect_to_dongle, self._RADIO_CHECK_INTERVAL)


    # +===================== Radio Setup ============================#
   
    def _connect_to_dongle(self, *args):
        try:
            self._radio = CR.Crazyradio()
        except Exception as e:
            return 
        self._RADIO_CONNECTED = True

        # Call the Connection cls radio_connected function
        self._connection_cls.radio_connected(self)

        self._initialize_radio()
        Clock.schedule_interval(self._check_radio_link, self._RADIO_CHECK_INTERVAL)
        return False
    
    def _check_radio_link(self, *args):
        try:
            self._radio = CR.Crazyradio()
        except:
            self._RADIO_CONNECTED = False
            
            # Call the Connection class radio_disconnected function
            self._connection_cls.radio_disconnected(self)
            Clock.schedule_interval(self._connect_to_dongle, self._RADIO_CHECK_INTERVAL)
            return False

    def _initialize_radio(self, *args):
        """
        Initializes the Radio
        """
        # Retrieve the variables from the config file
        for (key, value) in self._configs.items():
            if key.lower() == "channel":
                self._radio.set_channel(int(value))

            elif key.lower() == "data_rate":
                self._radio.set_data_rate(int(value))

            elif key.lower() == "arc":
                self._radio.set_arc(int(value))

        # Start sending data
        self._send_packets()



    def scan_for_targets(timeout=5):
        """
        :param timeout - time taken to do a second
        """
        print("Scanning for targets!!")

    # +==============================================================#
    # +==============================================================#


    # ++++++++ Functions available to control Network Manager ======= #
    def send_packet(self, addr, cb, packet):
        """
        sends packet through Radio
        using Address
        : ==> addr = Address of Destination
              packet = packet to be sent ( CrazyRadio protocol)
              cb = Function to process the response: will be 
                    called as cb(addr, response)
        """
        if not self._RADIO_CONNECTED or self._radio is None:
            raise RadioDisconnectedError

        else:
            # Put in the SEND Buffer
            self._send_buffer.put((addr, cb, packet))

    def clear_buffers(self):
        self._SEND_PACKET = False
        while (not self._send_buffer.empty()):
            self._send_buffer.get()
        
        while (not self._recv_buffer.empty()):
            self._recv_buffer.get()
        self._SEND_PACKET = True

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ # 
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ # 


    # +===================   Send DATA    ============================#
    """
    Handles the connection data flow
    Decides when to send the packet
    Decides when to wait
    """
    def _send_packets(self, *args):

        print(f"sending packets!! at {args[0]}")
        if not self._send_buffer.empty() and self._radio is not None and \
            self._RADIO_CONNECTED and self._SEND_PACKET:

            # retrieve packet from buffer
            data = self._send_buffer.get()
            addr = data[0]
            cb_func = data[1]
            packet = data[2]

            # send packet through the radio
            response = self._radio.send_packet(addr, packet)

            # pass addr, response to cb
            cb_func(addr, response)

        send_interval = self._COMM_LINK_TRANSFER_RATE / 0.1
        Clock.schedule_interval(self._send_packets, send_interval)

    # +=================================================================#
    # +=================================================================#


    # ====================== Read from File ============================#
    def _load_config(self):
        """
        Helper Function
        Loads the radio config file
        """
        read_lines = []
        configs = {}
        try:
            with open(str(self.__DIR__ / "radio_config.txt"), 'r') as config_file:
                read_lines = config_file.readlines()
        except Exception as e:
            raise e
        for line_num, line in enumerate(read_lines):
            line = line.strip()
            line = line.strip('\n')
            if line.startswith('#'):
                continue
            try:
                attr, value = line.split('=')
                attr = attr.strip()
                value = value.strip()
                configs[attr] = value
            except Exception as e:
                # print(f"line Number {line_num} raised Exception {e}")
                continue
        return configs


    def _set_variables(self):
        for (key, value) in self._configs.items():
            try:
                try:
                    value = int(value)
                except:
                    pass
                setattr(self,'_'+key, value)
            except Exception as e:
                continue

    # ==================================================================#
    # ==================================================================#


    # ======================== Transmission Control =====================#
    def pause_transmission(self):
        self._SEND_PACKET = False
    
    def resume_transmission(self):
        self._SEND_PACKET = True

    # ==================================================================#
    # ==================================================================#






if __name__ == "__main__":
    import time
    network_manager = NetworkManager(None)
    network_manager._load_config()
    print(network_manager._configs)
    print('#'*20)
    network_manager.initialize_radio()
