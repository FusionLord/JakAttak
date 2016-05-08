import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from libs.TimeMachine.TimeValuePattern.TimeValuePattern import*

class TimeValuePattern_SawIncrement(TimeValuePattern):
    def __init__(self, min, max, amount = 1):
        #THERE'S NO NEED FOR PHASE, YA GOOF
        self.min = min
        self.max = max
        self.amount = amount

    def get_estimated_value(self, start_value, timedif):
        dif = self.max-self.min
        return (start_value+(timedif*self.amount)-self.min)%(dif)+self.min