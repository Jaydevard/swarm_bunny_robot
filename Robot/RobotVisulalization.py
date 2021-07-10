from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from Robot.robotSimulator import BunnySim

class RobotCanvas(BoxLayout):
    def __init__(self, **kwargs):
        super(RobotCanvas, self).__init__(**kwargs)
        self.robots = {}

    def createRobots(self, numRobots):
        for i in range(numRobots):
            self.robots[f'Robot{i}'] = BunnySim(id=i)

    def defineEnvironment(self, dimension, *args):
        pass


class RobotVisualization(App):
    def build(self):
        pass


if __name__ == "__main__":
    RobotVisualization().run()




# def change_button_color(self, widget, *args):
    #     animate_button = Animation(background_color=(1, 0, 0, 1), duration=5) # Make the animation last for 5 seconds
    #     animate_button += Animation(opacity=0)                                # Add another animation afterwards
    #     animate_button.bind(on_start=self.print_me)                           # Attach a function callback
    #     animate_button.start(widget)
    #
    # def print_me(self, *args):
    #     print("starting...")
