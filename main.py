from gui.swarm_gui import SwarmGUI
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')


if __name__ == "__main__":

    Simulation = SwarmGUI()
    Simulation.run()







 