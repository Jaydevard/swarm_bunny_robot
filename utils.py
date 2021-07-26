import queue
import threading
import time


class DataHandler(queue.Queue):
    def __init__(self, name: str = None):
        super(DataHandler, self).__init__()
        self._name = name

    def send_data(self, message):
        if self.full():
            raise Exception("stream is full")
        else:
            self.put(message)


if __name__ == "__main__":
    pass















