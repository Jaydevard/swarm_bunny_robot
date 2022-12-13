import math
from kivy.clock import Clock
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty
from functools import partial
import random
import numpy as np
from operator import itemgetter
from kivy.event import EventDispatcher
from math import pi, cos, sin, atan2, sqrt
from core.exceptions import ShapeTooSmallError


class ShapeFormation(EventDispatcher):
    """
    Handles the simulation process from the shapes
    Top level class
    """
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def calc_target_points_from_shape(shape_properties, 
                                      bunny_dim: tuple or list):
        
        """
        TO DO: Create a configuration file so that more object specifications
               can be added, 
        Add the shape properties: 
            {
                "type": "Rectangle",
                "pos": (),
                "size": w, h
                "segments": (if  polygon ): 
                "points": (if triangle)
                "num_robots": from (maximum, minimum, custom(a number))
            }
        """
        SHAPE_TYPES = ("Rectangle", "Triangle", "Polygon", "Ellipse")
        BUNNY_DIMENSION = bunny_dim
        shape_type = shape_properties["type"]
        pos = shape_properties["pos"]
        size = shape_properties["size"]
        segments = None
        points = None
        num_robots = shape_properties["num_robots"]

        if shape_type not in SHAPE_TYPES:
            raise Exception(f"Shape specified not valid, shapes should be {SHAPE_TYPES}")

        elif shape_type == "Polygon":
            segments = shape_properties["segments"]
            targets = []
            add = targets.append
            
            # find the lowest possbile step angle
            angle_step = (pi * 2) / float(segments)
            o_segments = segments
            (x0, y0) = pos
            while segments > 0:
                x1 = x0 + (1 + cos((angle_step * 0) + pi/2)) * (size[0]/2)
                y1 = y0 + (1 + sin((angle_step * 0) + pi/2)) * (size[1]/2)
                x2 = x0 + (1 + cos((angle_step * 1) + pi/2)) * (size[0]/2)
                y2 = y0 + (1 + sin((angle_step * 1) + pi/2)) * (size[1]/2)
                if sqrt( (y2-y1)**2  + (x2-x1)**2 ) >= max(BUNNY_DIMENSION):
                    break
                else:
                    angle_step += 0.01745 # 1 degree increment 
            segments = int(2*pi/angle_step)
            fit_adjacent_robots = False

            if segments < o_segments: 
                raise ShapeTooSmallError("Specified num segments cannot fit" \
                                            + "requested number of robots")
            else:
                if num_robots == "Minimum" or num_robots == type(num_robots) in (float, int):
                    segments = o_segments
                elif num_robots == "Maximum":
                    fit_adjacent_robots = True

            for i in range(segments) :
                x = x0 + (1 + cos((angle_step * i) + pi/2)) * (size[0]/2)
                y = y0 + (1 + sin((angle_step * i) + pi/2)) * (size[1]/2)
                add((x,y))

            # need to add adjacent robots
            if fit_adjacent_robots:
                for i in range(0, len(targets), 1):
                    (x0, y0) = targets[i-1]
                    (x1, y1) = targets[i]
                    rel_angle = atan2((y1-y0), (x1-x0))
                    l = sqrt ((x1-x0)**2 + (y1-y0)**2)
                    num_robots_fitting = int(l // max(BUNNY_DIMENSION))
                    if num_robots_fitting <= 1:
                        continue
                    new_d = l / num_robots_fitting
                    for k in range(1, num_robots_fitting, 1):
                        add(  (x0 + new_d*k*cos(rel_angle), y0 + new_d*k*sin(rel_angle)) )
                        print((x0 + new_d*k*cos(rel_angle), y0 + new_d*k*sin(rel_angle)) )
            return targets

        elif shape_type == "Ellipse":
            segments = int((max(size)/2)*2*pi// min(BUNNY_DIMENSION))
            targets = []
            add = targets.append
            
            # find the lowest possbile step angle
            angle_step = (pi * 2) / float(segments)
            o_segments = segments
            (x0, y0) = pos
            while segments > 0:
                x1 = x0 + (1 + cos((angle_step * 0) + pi/2)) * (size[0]/2)
                y1 = y0 + (1 + sin((angle_step * 0) + pi/2)) * (size[1]/2)
                x2 = x0 + (1 + cos((angle_step * 1) + pi/2)) * (size[0]/2)
                y2 = y0 + (1 + sin((angle_step * 1) + pi/2)) * (size[1]/2)
                if sqrt( (y2-y1)**2  + (x2-x1)**2 ) >= max(BUNNY_DIMENSION):
                    break
                else:
                    angle_step += 0.01745 # 1 degree increment 

            segments = int(2*pi/angle_step)
            for i in range(segments) :
                x = x0 + (1 + cos((angle_step * i) + pi/2)) * (size[0]/2)
                y = y0 + (1 + sin((angle_step * i) + pi/2)) * (size[1]/2)
                add((x,y))
            return targets

        elif shape_type == "Triangle":
            points = shape_properties["points"]
            if len(points) != 3:
                raise AttributeError("number of points specified for triangle is not 3")
            targets = points

            for index, point in enumerate(points):
                (x0, y0) = points[index-1]
                (x1, y1) = points[index]
                distance = sqrt( (y1-y0)**2  + (x1-x0)**2 )                 
                if distance < max(BUNNY_DIMENSION):
                    raise ShapeTooSmallError
            else:
                if num_robots == "Minimum":
                    return targets
                
                elif num_robots == "Maximum":
                    return targets

                    ## Don't have time to finish the algorithm
                    (x0, y0) = points[0]
                    (x1, y1) = points[1]
                    (x2, y2) = points[2]
                    
                    d0 = sqrt( (y1-y0)**2  + (x1-x0)**2 )  
                    d1 = sqrt( (y2-y1)**2  + (x2-x1)**2 )  
                    d2 = sqrt( (y2-y0)**2  + (x2-x0)**2 )
                    
                    th0 = atan2((y1-y0), (x1-x0))
                    th1 = atan2((y2-y1), (x2-x1))
                    th2 = atan2((y2-y0), (x2-x0))
                    
                    prop = [(d0, th0, x0, y0), 
                            (d1, th1, x1, y1), 
                            (d2, th2, x2, y2)
                            ]
                    prop = sorted(prop, key=lambda x: float(x[0]), reverse=True)   # largest first


                    [(d0, th0, x0, y0), (d1, th1, x1, y1), (d2, th2, x2, y2)] = prop
                    ## find the number of robots fitting
                    num_robots_fit = int(d0 // max(BUNNY_DIMENSION ))
                    if num_robots_fit <= 1:
                        pass
                    new_d = d0 / num_robots_fit
                    next_robot_pos = ( ( x + new_d*i*cos(th)), (y + new_d*i*sin(th)) )

        elif shape_type == "Rectangle":
            width = size[0]
            height = size[1]     
            # check size
            if width > BUNNY_DIMENSION[0] * 2 and height > BUNNY_DIMENSION[1]:
                if num_robots == "Minimum":
                    return [ pos, 
                             (pos[0] , pos[1] + size[1]),
                             (pos[0] + size[0], pos[1] + size[1]),
                             (pos[0] + size[0], pos[1])
                           ]
                elif num_robots == "Maximum":
                    # Approach is take each side and see how many robots that we can fit
                    # Obviously, minimum is 4
                    d = max(BUNNY_DIMENSION)
                    targets = [pos]
                    add = targets.append
                    # Take each side
                    num_robots_fitting = int (size[1] // d)
                    print(num_robots_fitting)
                    new_d = size[1] / num_robots_fitting

                    for i in range(1, num_robots_fitting+1):
                        add( (pos[0], pos[1] + new_d*i) )

                    num_robots_fitting = int(size[0] // d)
                    new_d = size[0] / num_robots_fitting
                    
                    for i in range(1, num_robots_fitting+1, 1):
                        add(  (pos[0]+ new_d*i, pos[1] + size[1]) )

                    num_robots_fitting = int(size[1] // d)
                    new_d = size[1] / num_robots_fitting
                    
                    for i in range(0, num_robots_fitting, 1):                    
                        add(  (pos[0] + size[0], pos[1]+ new_d*i ) )                    

                    num_robots_fitting = int(size[0] // d)
                    new_d = size[0] / num_robots_fitting
                    
                    for i in range(1, num_robots_fitting, 1):                    
                        add(  (pos[0]+ new_d*i, pos[1]) )                    
                    return targets
                """
                size = (5, 5)
                b_w, b_h = size[0], size[1]

                s_pos = (100, 150)
                s_w, s_h = (35, 20)
                s_type = "Rectangle"

                target_pts = []
                add = target_pts.append

                # Slider Method ( Faster)
                # First calculate maximum number of robots on the slider line
                num_robots_on_slider = s_h // b_h
                separation_h = b_h + (s_h % b_h) / num_robots_on_slider

                # Calculate the number of columns required
                num_of_slides = s_w // b_w
                slide_increment = b_w + (s_w % b_w) / num_of_slides


                print(num_of_slides, slide_increment)
                ## main for loop
                for pt_num_in_slider in range(num_robots_on_slider+1):
                    add((s_pos[0], s_pos[1] + pt_num_in_slider*separation_h))
                    for increment_num in range(1, num_of_slides+1):
                        add((s_pos[0] + increment_num * slide_increment, 
                            s_pos[1] + pt_num_in_slider*separation_h))  
                """            
            else:
                raise ShapeTooSmallError

    @staticmethod
    def _apply_scale_matrix(current_pos, factor):
        """
        NOTE: ALL Values Need to be positive for current pos
        current_pos: [
            [x1, y1],
            [x2, y2]
        ]
        """
        current_pos = np.array(current_pos).T
        print(current_pos.shape)

        # calculate center points
        centroid = np.reshape(np.average(current_pos, axis=1), (2,1))
        rel_current_pos = current_pos - centroid
        print(rel_current_pos, centroid)

        # calc scale matrix
        R = np.array([[factor, 0], [0, factor]])

        scaled = (np.matmul(R, rel_current_pos)) 
        return (scaled + centroid).T

    @staticmethod
    def _apply_translate_matrix(current_pos, x, y):
        """
        Applies translation in x and y axes
        
        """
        current_pos = np.array(current_pos).T
        translation = np.array([[x], 
                                [y]])
        return (current_pos + translation).T

    @staticmethod
    def create_shape_simulation(self, node_properties):
        """
        Creates the simulation process
        
        node_properties = {
            "robots_current_pos":{
                "LGN01" : (),
                "LGN02": (),
                "LGN03": ()

            }
            "shape":{
                    "type": "Rectangle",
                    "pos": (),
                    "size": w, h
                    "segments": (if  polygon ): 
                    "points": (if triangle)
                    "num_robots": from (maximum, minimum, custom(a number))
                },

            "effects":{

                    "Rotate": {
                                "angle": 90,
                                "current_pos":
                                "size": ,
                                "start_delay":
                                "duration": 
                                "start_sequence": True
                    
                    },

                    "Morph": {

                                "current_pos":  ,
                                "size": ,
                                "scale_factor": ,
                                "duration":  ,
                                "start_delay":
                                "start_sequence": False
                    },

                    "Translate": {

                                "current_pos":,
                                "size": ,
                                "scale_factor":,
                                "x":,
                                "y":,
                                "start_sequence": False
                    }
                    }
            }

        """
        robots_current_pos = node_properties["robots_current_pos"].values()
        shape = node_properties["shape"]
        effects = node_properties["effects"]
        chosen_robots = {}
        # start compiling velocities
        # get target_points first
        try:
            target_points = self.calc_target_points_from_shape(shape)
            targets_pos, chosen_robots = PathPlanner.assign_target_points(current_robot_pos=robots_current_pos,
                                                                          target_pos=target_points)
        except ShapeTooSmallError:
            raise Exception

class Simulator(EventDispatcher):

    def __init__(self) -> None:
        super().__init__()

if __name__ == "__main__":

    shape_formation = ShapeFormation()
    # shape = {"type": "Triangle", 
    #          "pos":(0,0),
    #          "size": (10, 10),
    #          "num_robots": "Maximum",
    #          "segments": 4,
    #          "points": [(100, 45), (45, 45), (24, 80)]
    #         }
    print(shape_formation._apply_translate_matrix([ [2, 3], 
                                                    [3, 2],
                                                    [2, 1],
                                                    [1, 2]], 
                                                    200, 300))


