from kivy.uix.widget import Widget
from kivy.graphics import Ellipse, Line, Color
from kivy.clock import Clock
from kivy.properties import ObjectProperty
import numpy as np
import os


class BunnyShape(Ellipse):
    uri = ObjectProperty()

    def __init__(self, **kwargs):
        super(BunnyShape, self).__init__(**kwargs)
        self._uri = self.uri
        self.image_source = kwargs.get('image_source') if kwargs.get('image_source') is not None else None
        self.size = kwargs.get('size') if kwargs.get('size') is not None else (50, 50)
        self.color = kwargs.get('color') if kwargs.get('color') is not None else (1, 1, 1, 1)
        with self.canvas:
            self.c = Color(rgba=self.color)
            self.shape = Ellipse(pos=self.pos, size=self.size, source=self.image_source)

    def on_start(self):
        pass

    if __name__ == "__main__":
        pass







