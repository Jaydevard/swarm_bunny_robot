import queue


class DataHandler(queue.Queue):
    def __init__(self):
        super(DataHandler, self).__init__()

    def send_data(self, message):
        if self.full():
            raise Exception("stream is full")
        else:
            self.put(message)

