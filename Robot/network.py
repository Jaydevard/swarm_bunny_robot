import asyncio


class Channel:
    """
    .:param uri: uri of robot
            latency: expected latency of channel (in s)
            transmitter: object having a method receiver_message(self, data), /
                         object sending data to robot
            receiver:    object having a method receiver_message(self, data),/
                         object receiving data from transmitter
            snr:         Default is None
                         signal-to-noise ratio
    """
    SENDING_TO_TRANSMITTER = 2
    SENDING_TO_RECEIVER = 1
    IDLE = 0

    def __init__(self, channel_id, transmitter, receiver, latency,snr=None):
        self._channel_id = channel_id
        self._transmitter = transmitter
        self._receiver = receiver
        self._latency = latency
        self._data_direction = self.IDLE
        self._snr = snr

    async def send_to_receiver(self, data):

        if self._receiver is None:
            return
        try:
            assert self._data_direction == self.IDLE
        except AssertionError:
            await self.wait_for_transmission()
        finally:
            self._data_direction = self.SENDING_TO_RECEIVER
            await asyncio.sleep(self._latency)
            await self._receiver.receive_message(data)
            self._data_direction = self.IDLE

    async def send_to_transmitter(self, data):
        if self._transmitter is None:
            return
        try:
            assert self._data_direction == self.IDLE
        except AssertionError:
            await self.wait_for_transmission()
        finally:
            self._data_direction = self.SENDING_TO_TRANSMITTER
            await asyncio.sleep(self._latency)
            await self._transmitter.receive_message(data)
            self._data_direction = self.IDLE

    async def wait_for_transmission(self):
        if self._data_direction == self.IDLE:
            return
        else:
            while self._data_direction != self.IDLE:
                await asyncio.sleep(self._latency / 100)

    async def add_snr(self, transmitted_data):
        if self._snr is None:
            return
        # To do add Noise to the signal

    @property
    def receiver(self):
        return self._receiver

    @receiver.setter
    def receiver(self, _receiver):
        self._receiver = _receiver

    @property
    def transmitter(self):
        return self._transmitter

    @transmitter.setter
    def transmitter(self, _transmitter):
        self._transmitter = _transmitter


class Network:
    """
    Creates a virtual network for the simulation

    """
    def __init__(self, **kwargs):
        self._num_channels = 128
        self._latency = 1e-9
        self._active_channels = {}

    def add_robot_to_network(self, robot):
        channel_id = robot.uri
        dedicated_receiver = robot.receiver
        dedicated_transmitter = Transmitter(receive_message_callback=None)
        allocated_channel = Channel(channel_id=channel_id,
                                    transmitter=dedicated_transmitter,
                                    receiver=dedicated_receiver,
                                    latency=1,
                                    snr=None)
        dedicated_transmitter.communication_channel = allocated_channel
        dedicated_receiver.communication_channel = allocated_channel
        self._active_channels[channel_id] = allocated_channel
        return dedicated_transmitter

    def remove_robot_from_network(self, robot):
        del self._active_channels[robot.uri]


class Transmitter:
    def __init__(self, receive_message_callback=None):
        self._latency = 1e-9
        self._message_received = None
        self._receive_message_callback = receive_message_callback
        self._communication_channel = None

    async def receive_message(self, data):
        self._message_received = data
        await self._receive_message_callback(data)

    async def send_message(self, message):
        if self._communication_channel is None:
            return
        await asyncio.sleep(self._latency)
        await self.communication_channel.send_to_receiver(message)

    @property
    def communication_channel(self):
        return self._communication_channel

    @communication_channel.setter
    def communication_channel(self, channel):
        self._communication_channel = channel

    @property
    def receive_message_callback(self):
        return self._receive_message_callback

    @receive_message_callback.setter
    def receive_message_callback(self, callback):
        """
        callback should be asynchronous
        :param callback: function to be called when transmitter receives a message
        :return: None
        """
        self._receive_message_callback = callback


if __name__ == "__main__":
    pass
