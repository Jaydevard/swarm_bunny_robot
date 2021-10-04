#import libusb



class WirelessNetwork:
    """
    Wireless Network class to manage devices connected to the
    radio dongle
    """

    def __init__(self):
        self._radio_dongle = None
        self._active_channels = []

    def search_for_radio_dongle(self):
        """
        Look for robots or other recipients
        Need to look at the CrazyRadio Protocol
        :return: None if no devices present
        """
        pass

    def connect_to_radio_dongle(self):
        """
        Connects to the radio dongle
        Performs a search for devices and then connects to it if present
        CrazyRadio has a unique id and address
        :return: None
        """
        pass

    def disconnect_from_radio_dongle(self):
        """
        Must issue a warning to the user that the connection is being stopped
        since communication to robots will be lost
        :return: None
        """
        pass

    def search_for_robots(self):
        """
        Once connected to the dongle, search for the active robot channels

        :return: None
        """
        pass

    def add_robot_to_network(self):
        """
        Adds the robot to the network
        Can perform a PING to check the connection

        :return: None
        """
        pass

    def remove_robot_from_network(self):
        """
        Removes the robot from the network
        :return:
        """
        pass




