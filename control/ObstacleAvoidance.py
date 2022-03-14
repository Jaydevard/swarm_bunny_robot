import math
from kivy.event import EventDispatcher

class ObstacleAvoidance(EventDispatcher):
    """
        Class: Obstacle Advoidance
        
        Static methods to apply obstacle advoidance to the velocity matrix
    """    
    @staticmethod
    def map_collisions(velocity_matrix, time_step, current_pos):
        """
            Scans the velocity matrix to find where collisions will occur. 
            
            To fix: Creates duplicates
        """
        PIXEL_THRESHOLD = 10 # Change to some global threshold
        robot_positions = current_pos
        num_timestamps = len(velocity_matrix[0][0])
        num_robot = len(velocity_matrix[0])
        
        # List of collisions (timestamp index, robot1, robot2) 
        collisions=[]
        
        for t in range(0, num_timestamps):
            # Update robots to next position. Not actually changing location of robots, just simulating
            for r in range(0, num_robot):
                robot_positions[r][0] += (velocity_matrix[r][0][t] * time_step) 
                robot_positions[r][1] += (velocity_matrix[r][1][t] * time_step)
            
            # Check if between collision threshold
            for robot in range (0, num_robot):
                for other_robot in range(0, num_robot):
                    if(robot == other_robot): # Don't compare same robots
                        continue
                    else:
                        r1 = robot_positions[robot]
                        r2 = robot_positions[other_robot]
                        distance_between = math.hypot(r2[0] - r1[0], r2[1] - r1[1])
                        if(distance_between < PIXEL_THRESHOLD):
                            collisions.append([t,robot,other_robot])
            
        return collisions