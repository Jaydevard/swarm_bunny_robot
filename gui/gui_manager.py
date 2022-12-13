"""
gui_manager.py
============================================================
Gui Manager.py
Manages the shapes, and robots on the robot canvas
this helps in maintaining a central class to control
everything instead of trying to tie ends to every sub class
of the canvas
============================================================
"""
from kivy.clock import Clock
import numpy as np
from core.constants import Constants as Cons

class ShapeManager():
    """
    ShapeManager
    """
    safety_margin = Cons.SAFETY_MARGIN

    def __init__(self, app:object, canvas:object, **kwargs) -> None:
        self.app = app
        self.canvas = canvas
        self.tracked_shapes = []

    def track_shape(self, shape):
        self.tracked_shapes.append(shape)

    def untrack_shape(self, shape):
        try:
            self.tracked_shapes.remove(shape)
        except Exception as e:
            print(e)

    def check_collision(self):
        pass
    

        



