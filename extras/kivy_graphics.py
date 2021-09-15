from kivy.graphics import Triangle
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.clock import Clock


class Graphics(App):
    robot_pos = ObjectProperty

    def __init__(self, **kwargs):
        super(Graphics, self).__init__(**kwargs)
        self.ids = None

    def build(self):
        self.ids = self.root.ids


if __name__ == "__main__":
    graphics = Graphics()
    graphics.run()
