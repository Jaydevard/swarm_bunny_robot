from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.properties import NumericProperty
from kivy.uix.behaviors import DragBehavior


class TransmitterWidget(Widget, DragBehavior):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pos():
        print("changing position!!")


