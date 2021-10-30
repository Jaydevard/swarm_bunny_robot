from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.properties import NumericProperty
from kivy.uix.behaviors import DragBehavior
from pathlib import Path

class TransmitterWidget(DragBehavior, Image):

    def __init__(self, **kwargs):
        super(TransmitterWidget, self).__init__(**kwargs)
        self.source = str(Path("custom_widgets/transmitter_widget/images/transmitter.png"))
    

    
    



