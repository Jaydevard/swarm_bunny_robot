# # '''
# # Mesh test
# # =========

# # This demonstrates the use of a mesh mode to distort an image. You should see
# # a line of buttons across the bottom of a canvas. Pressing them displays
# # the mesh, a small circle of points, with different mesh.mode settings.
# # '''

# # from kivy.uix.button import Button
# # from kivy.uix.widget import Widget
# # from kivy.uix.boxlayout import BoxLayout
# # from kivy.app import App
# # from kivy.graphics import Mesh
# # from functools import partial
# # from kivy.graphics import Color
# # from math import cos, sin, pi
# # from kivy.graphics import Line


# # class MeshTestApp(App):

# #     def change_mode(self, mode, *largs):
# #         self.mesh1.mode = mode

# #     def build_mesh(self, length, width):
# #         """ returns a Mesh of a rough circle. """
# #         vertices = []
# #         indices = []
# #         step = 50
# #         istep = (pi * 2) / float(step)
# #         for i in range(step):
# #             x = 100 + (1+cos(istep * i)) * length/2
# #             y = 100 + (1+sin(istep * i)) * width/2
# #             vertices.extend([x, y, 0, 0])
# #             indices.append(i)
# #         return Mesh(vertices=vertices, indices=indices)

# #     def build(self):
# #         wid = Widget()
# #         with wid.canvas:
# #             Color(1, 1, 0, 1)
# #             self.mesh1 = self.build_mesh(length=100, width=100)
# #             Color(0, 0, 1, 1)
# #             N =5
# #             istep = (2* pi)/ float(N)
# #             length=800
# #             width = 400
# #             points = []
# #             for i in range(N):
# #                 x = 100 + (1 + cos((istep*i)  +  pi/2)) * length/2
# #                 y = 100 + (1 + sin((istep*i)  +  pi/2)) * width/2
# #                 points.extend([x, y])
# #             points.extend([points[0], points[1]])
# #             Line(points=points)

# #         layout = BoxLayout(size_hint=(1, None), height=50)
# #         for mode in ('points', 'line_strip', 'line_loop', 'lines',
# #                 'triangle_strip', 'triangle_fan'):
# #             button = Button(text=mode)
# #             button.bind(on_release=partial(self.change_mode, mode))
# #             layout.add_widget(button)

# #         root = BoxLayout(orientation='vertical')
# #         root.add_widget(wid)
# #         root.add_widget(layout)

# #         return root


# # if __name__ == '__main__':
# #     MeshTestApp().run()

# from email.mime import base
# from kivy.app import App
# from kivy.lang import Builder
# from kivy.uix.recycleview import RecycleView
# from kivy.uix.recycleview.views import RecycleDataViewBehavior
# from kivy.uix.label import Label
# from kivy.properties import BooleanProperty
# from kivy.uix.recycleboxlayout import RecycleBoxLayout
# from kivy.uix.behaviors import FocusBehavior
# from kivy.uix.recycleview.layout import LayoutSelectionBehavior

# Builder.load_string('''
# <SelectableLabel>:
#     # Draw a background to indicate selection
#     canvas.before:
#         Color:
#             rgba: (.0, 0.9, .1, .3) if self.selected else (0, 0, 0, 1)
#         Rectangle:
#             pos: self.pos
#             size: self.size
# <RV>:
#     viewclass: 'SelectableLabel'
#     SelectableRecycleBoxLayout:
#         default_size: None, dp(56)
#         default_size_hint: 1, None
#         size_hint_y: None
#         height: self.minimum_height
#         orientation: 'vertical'
#         multiselect: True
#         touch_multiselect: True
# ''')


# class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
#                                  RecycleBoxLayout):
#     ''' Adds selection and focus behaviour to the view. '''


# class SelectableLabel(RecycleDataViewBehavior, Label):
#     ''' Add selection support to the Label '''
#     index = None
#     selected = BooleanProperty(False)
#     selectable = BooleanProperty(True)

#     def refresh_view_attrs(self, rv, index, data):
#         ''' Catch and handle the view changes '''
#         self.index = index
#         return super(SelectableLabel, self).refresh_view_attrs(
#             rv, index, data)

#     def on_touch_down(self, touch):
#         ''' Add selection on touch down '''
#         if super(SelectableLabel, self).on_touch_down(touch):
#             return True
#         if self.collide_point(*touch.pos) and self.selectable:
#             return self.parent.select_with_touch(self.index, touch)

#     def apply_selection(self, rv, index, is_selected):
#         ''' Respond to the selection of items in the view. '''
#         self.selected = is_selected
#         if is_selected:
#             print("selection changed to {0}".format(rv.data[index]))
#         else:
#             print("selection removed for {0}".format(rv.data[index]))


# class RV(RecycleView):
#     def __init__(self, **kwargs):
#         super(RV, self).__init__(**kwargs)
#         self.data = [{'text': str(x)} for x in range(100)]


# class TestApp(App):
#     def build(self):
#         return RV()

# if __name__ == '__main__':
#     TestApp().run()


import numpy as np
import math



# current_pos = np.array([0.1, 0.5, np.pi/2])
# print(type(current_pos))
# print(current_pos[0])

# pos = [0, 0]
# center = [0, 0]

# [x, y] = [pos[0] - center[0], pos[1] - center[1]]
# angle = 0

# if float(x) == 0.0 and float(y) == 0.0:
#     angle = 0.0

# elif float(x) == 0.0 and float(y) > 0.0:
#     angle = math.pi /2

# elif float(x) == 0.0 and float(y) < 0.0:
#     angle = 3/2*math.pi 

# else:
#     if x > 0:
#         if y < 0:
#             angle = 2*math.pi - math.atan(abs(y / x))
#         else:
#             angle = math.atan(abs(y / x))
#     elif y >= 0:
#             angle = math.pi - math.atan(abs(y / x))
    
#     else:
#         angle = math.pi + math.atan(abs(y / x))
    

# print(x, y, angle)

def run():
    pass
    x1 = x0 + (1 + cos(angle_step * 0) + np.pi/2)





if __name__ == "__main__":
    run()








