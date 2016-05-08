import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from libs.TimeMachine.TimeValuePattern.TimeValuePattern import*
from libs.common import*

class TimeValuePattern_VectorIncrement(TimeValuePattern):
    def __init__(self, velocity, speed, phase = 0):
        self.velocity = velocity
        self.speed = speed
        self.phase = phase

    def get_estimated_value(self, start_value, timedif):
        return tuple(lerp_lists(start_value,(start_value[0]+self.velocity[0],start_value[1]+self.velocity[1]),(timedif+self.phase)/float(self.speed)))