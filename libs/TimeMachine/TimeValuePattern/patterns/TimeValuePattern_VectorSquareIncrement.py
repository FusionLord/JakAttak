import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from libs.TimeMachine.TimeValuePattern.TimeValuePattern import*

class TimeValuePattern_VectorSquareIncrement(TimeValuePattern):
    def __init__(self, velocity, speed):
        self.velocity = velocity
        self.speed = speed

    def get_estimated_value(self, start_value, timedif):
        return (start_value[0]+(timedif/self.speed*self.velocity[0]),
                start_value[1]+(timedif/self.speed*self.velocity[1]))