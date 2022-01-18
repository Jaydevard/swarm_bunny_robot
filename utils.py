import queue
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from functools import partial

from core.constants import Constants


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


class InformationPopup(Popup):
    """
    ->Displays message, warning or error to the user\n
    ->Use it only to display information to the user\n
    ->Popup will exit on clicking outside the popup area\n
    Required Arguments:
        --> _type: string, should be from ("e", "w", "i")
            "e": error
            "w": warning
            "i": info
        --> _message: string, Message to be displayed\n
        (optional)\n
        --> _callback_on_dismiss: function called when popup closes (caller is passed as argument)
    """
    def __init__(self, _type: str, _message: str, callback_on_dismiss=None, **kwargs):
        super(InformationPopup, self).__init__()
        # Popup Settings
        self.size_hint = (0.35, 0.25)
        self.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.title_color = (0.9, 0.9, 0.9, 1)
        self.title_align = 'center'
        self.title_size = '20sp'
        self.callback_on_dismiss = callback_on_dismiss
        # Message Settings
        self.message_size = '18sp'
        if _type not in ("e", "w", "i"):
            raise Exception("Unknown error type\n _type should be 'e' or 'w' or 'i'")
        else:
            self._type = _type
        self._message = _message
        if self.callback_on_dismiss is not None:
            self.bind(on_dismiss=callback_on_dismiss)

        if _type == "e":
            self._message = f"[size={self.message_size}][color=ff3333]{self._message}[/color][/size]"
            self.title = "Error"

        elif _type == "w":
            self._message = f"[size={self.message_size}][color=33ff33]{self._message}[/color][/size]"
            self.title = "Warning"
        else:
            self._message = f"[size={self.message_size}][color=3333ff]{self._message}[/color][/size]"
            self.title = "Info"
        self._main_layout = BoxLayout(size_hint=(1, 1),
                                      pos_hint={"center_x": 0.5, "center_y": 0.5},
                                      pos=self.pos)
        self._message_label = Label(pos_hint={"center_x": 0.5, "center_y": 0.5},
                                    size_hint=(1, 1),
                                    text=self._message,
                                    markup=True)

        self._main_layout.add_widget(self._message_label)
        self.add_widget(self._main_layout)

class Scale(Constants):
    _scale = [100, 1, "m"]
    
    def __init__(self, **kwargs) -> None:
        self._scale = kwargs.get("scale", [100, 1, "m"])
        pass
    
    def set_scale(self, scale):
        self._scale = scale

    def to_pixels(self, val: int or float or list or tuple, unit: str, scale=None):
        """
        :params -val , value to convert
                -unit, unit of value ==> ("m", "ft")
                -scale(optional) if None, uses set scale, default is 100 pixels = 1m
                                 else must be a list like [200, 1, "ft"]
                                                          200 pixels = 1 ft
        """
        if type(val) == list or type(val) == tuple:
            val = [float(value) for value in val]
        else: 
            val = [float(val)]
        
        [base_pixel, base_unit, _unit] = self._scale if scale is None else scale
        base_pixel = float(base_pixel)
        conv_val = []
        for value in val:
            if _unit == "m" and unit == "m":
                conv_val.append(value * base_pixel)
            elif _unit == "m" and unit == "ft":
                conv_val.append(value * 0.3048 * base_pixel)
            elif _unit == "ft" and unit == "ft":
                conv_val.append(value * base_pixel)
            elif _unit == "ft" and unit == "m":
                conv_val.append(value * base_pixel * (1.0/0.3048))
        if len(conv_val) == 1:
            return conv_val[0]
        else:
            return conv_val
    
    def to_unit(self, val:int or float or list or tuple, unit:str, scale=None):
        """
        :params -val, value to convert pixels 
                -unit, unit to convert to
                -scale(optional) if None, uses set scale, default is 100 pixels = 1m
                                 else must be a list like [200, 1, "ft"]
                                                          200 pixels = 1 ft
        """
        if type(val) == list or type(val) == tuple:
            val = [float(value) for value in val]
        else: 
            val = [float(val)]
        
        [base_pixel, base_unit, _unit] = self._scale if scale is None else scale
        base_pixel = float(base_pixel)
        conv_val = []
        for value in val:
            if _unit == "m" and unit == "m":
                conv_val.append(value / base_pixel)
            elif _unit == "m" and unit == "ft":
                conv_val.append(value / 0.3048 / base_pixel)
            elif _unit == "ft" and unit == "ft":
                conv_val.append(value / base_pixel)
            elif _unit == "ft" and unit == "m":
                conv_val.append(value / base_pixel / 0.3048)
        if len(conv_val) == 1:
            return conv_val[0]
        else:
            return conv_val


if __name__ == "__main__":
    pass

























