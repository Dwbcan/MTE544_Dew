import numpy as np
# Type of planner
POINT_PLANNER=0; TRAJECTORY_PLANNER=1



class planner:
    def __init__(self, type_):

        self.type=type_

    
    def plan(self, goalPoint=[-1.0, -1.0]):
        
        if self.type==POINT_PLANNER:
            return self.point_planner(goalPoint)
        
        elif self.type==TRAJECTORY_PLANNER:
            return self.trajectory_planner()


    def point_planner(self, goalPoint):
        x = goalPoint[0]
        y = goalPoint[1]
        return x, y

    # TODO Part 6: Implement the trajectories here
    def trajectory_planner(self):

        # Choose which trajectory to use: 'parabola' or 'sigmoid'
        trajectory_type = 'parabola'  # Change to 'sigmoid' to test the other trajectory
        
        if trajectory_type == 'parabola':
            # Parabola: y = x^2 for x ∈ [0.0, 1.5]
            x_values = np.linspace(0.0, 1.5, num=50)  # 50 points along the trajectory
            trajectory = [[x, x**2] for x in x_values]
            
        elif trajectory_type == 'sigmoid':
            # Sigmoid: σ(x) = 2/(1 + e^(-2x)) - 1 for x ∈ [0.0, 2.5]
            x_values = np.linspace(0.0, 2.5, num=50)  # 50 points along the trajectory
            trajectory = [[x, 2.0 / (1.0 + np.exp(-2.0 * x)) - 1.0] for x in x_values]
        
        else:
            # Default to a simple straight line if neither is selected
            trajectory = [[0.0, 0.0], [1.0, 1.0]]
        
        # The return should be a list of trajectory points: [ [x1,y1], ..., [xn,yn]]
        return trajectory