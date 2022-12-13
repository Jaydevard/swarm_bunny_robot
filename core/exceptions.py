#---------- Create own Exceptions to better handle errors ---------#
# Date: 18 Feb 2022
#
#
#
# ----------------- Add more if needed!!! -------------------------#

class BunnyNotReadyError(Exception):
    # raised when Bunny is still initializing or
    # is not ready to accept Velocity commands
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NoAckError(Exception):
    # Raises an error when no acknowledgement is received
    # from the bunny robot

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class RadioDisconnectedError(Exception):
    # raises an error when Radio Dongle is disconnected
    # extremely unwanted!!
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ShapeTooSmallError(Exception):
    # raised when Shape is too small
    def __init__(self, *args: object) -> None:
        super().__init__(*args)









