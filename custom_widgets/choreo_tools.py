from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.graphics import Line, Rectangle, Ellipse, Triangle
from kivy.clock import Clock
from kivy.core.window import Window


class ChoreoBase(Widget):
    """
    Base class for the Choreography widgets
    """    
    touch_pos = "Border"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.touch_pos ="Border"
        self.c_line = Line()
        self.t_line - Line()
        self.touch_tol = 5


    def on_pos(self, instance, value):
        if self.x < self.parent.x:
            self.x += 10
        if self.y < self.parent.y:
            self.y += 10

        if (self.x + self.width) > self.parent.x:
            self.x -= 10
        
        if (self.y + self.height) > self.parent.y:
            self.y -= 10
        
        else:
            self.pos = value

    def on_size(self, instance, value):
        self.size = value
    
    def change_shape(self, touch, touch_pos):
        """"
        changes the widget's shape
        """

        xx, yy = self.to_widget(*touch.pos, relative=True)

        if touch_pos == 'top':
                if yy > 0:
                    if self.size_hint_y is None:
                        self.height = min(yy, self.parent.height)
                    else:
                        self.size_hint_y = yy / self.parent.height
                        if self.size_hint_y >= 1:
                            self.size_hint_y = 1
            
        elif touch_pos == "bottom":
            if self.height - yy > 0:
                if self.size_hint_y is None:
                    self.height -= yy
                    self.y += yy
                else:
                    self.size_hint_y = (self.height - yy) / self.parent.height
                    self.y += yy
        
        elif touch_pos == 'left':
            if touch.x > self.parent.x:
                if self.size_hint is None:
                    self.width -= xx
                    self.x += xx
                else:
                    self.size_hint_x = min(1, (self.width - xx) / self.parent.width)
                    self.x += xx
        
        elif touch_pos == 'right':
            if xx > 0:
                if self.size_hint_x is None:
                    self.width = xx
                else:
                    self.size_hint_x = xx / self.parent.width
                    self.width = xx

        elif touch_pos == 'nw':
            if yy > 0:
                if self.size_hint_y is None:
                    self.height = min(yy, self.parent.height)
                else:
                    self.size_hint_y = yy / self.parent.height
                    if self.size_hint_y >= 1:
                        self.size_hint_y = 1
            if self.width - xx > 0:
                if self.size_hint is None:
                    self.width -= xx
                    self.x += xx
                else:
                    self.size_hint_x = min(1, (self.width - xx) / self.parent.width)
                    self.x += xx
        elif touch_pos == 'ne':
            if yy > 0:
                if self.size_hint_y is None:
                    self.height = min(yy, self.parent.height)
                else:
                    self.size_hint_y = yy / self.parent.height
                    if self.size_hint_y >= 1:
                        self.size_hint_y = 1
            if xx > 0:
                if self.size_hint_x is None:
                    self.width = xx
                else:
                    self.size_hint_x = xx / self.parent.width
                    self.width = xx
        
        elif touch_pos == 'se':
            if self.height - yy > 0:
                if self.size_hint_y is None:
                    self.height -= yy
                    self.y += yy
                else:
                    self.size_hint_y = (self.height - yy) / self.parent.height
                    self.y += yy
            if xx > 0:
                if self.size_hint_x is None:
                    self.width = xx
                else:
                    self.size_hint_x = xx / self.parent.width
                    self.width = xx
        
        elif touch_pos == 'sw':
            if self.width - xx > 0:
                if self.size_hint is None:
                    self.width -= xx
                    self.x += xx
                else:
                    self.size_hint_x = min(1, (self.width - xx) / self.parent.width)
                    self.x += xx
            if self.height - yy > 0:
                if self.size_hint_y is None:
                    self.height -= yy
                    self.y += yy



    


