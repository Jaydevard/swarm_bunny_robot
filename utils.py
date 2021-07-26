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

# Used to normalize our robot location in meters to dimensions we can draw based on pixels
def normalize_dimensions(location_meters, dimensions_pixels, dimensions_meters):
    return ((location_meters[0] / dimensions_pixels[0]) * dimensions_meters[0],
            (location_meters[1]/ dimensions_pixels[1]) * dimensions_meters[1])

if __name__ == "__main__":
    pass















