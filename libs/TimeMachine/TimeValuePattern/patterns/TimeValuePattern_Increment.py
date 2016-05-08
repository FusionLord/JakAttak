import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from libs.TimeMachine.TimeValuePattern.TimeValuePattern import*

class TimeValuePattern_Increment(TimeValuePattern):
    def __init__(self, amount=1):
        self.amount = amount

    def get_estimated_value(self, start_value, timedif):
        return start_value+(timedif*self.amount)