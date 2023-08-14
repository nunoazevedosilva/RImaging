
# coding: utf-8

# In[ ]:


import serial
import time
import numpy as np


from Stage_Standa import *


class Stage_System:

    def __init__(self, parameters = {}):        
        
        self.stage = Stage_Standa(parameters)
    
    def check_state(self):
        """
        Checks the state of the stage system
        Returns
        -------
        bool True/False - if is ready
        [x,y] - current position
        """
        return self.stage.check_state()
    
    def turn_on(self):
        """
        Start the stage system
        """
        self.stage.turn_on()

    def turn_off(self):
        """
        Turns off the stage system
        """
        self.stage.turn_off()
    
    def go_home(self):
        """
        Send stages to the starting position
        """
        return self.stage.go_home()
        
    def current_position(self):
        """
        Gets the current position
        """
        return self.stage.check_state()[1]
        
        
    
    def move_to(self, x, y):
        """
        Moves to x,y position
        
        """
        self.stage.move_to(x=x,y=y)
        
    
    def rotate(self, theta):
        self.stage.rotate(theta)
        
   

if __name__ == "__main__": 
    
    stage_system = Stage_System(parameters={})
    stage_system.turn_on()
    stage_system.go_home()
    stage_system.move_to(x = 0, y = 10)
    print(stage_system.stage.get_speed()[0])

    stage_system.turn_off()
    
