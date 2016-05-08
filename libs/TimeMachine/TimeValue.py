import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from libs.TimeMachine.TimeValuePattern.patterns.TimeValuePattern_ParticlePos import*

class TimeValue(object):
    def __init__(self, value, frame, pattern=None):
        self.value = value
        self.frame = int(frame)
        self.pattern = pattern

    def __str__(self):
        return "TimeValue("+str(self.frame)+"): "+str(self.value)

    def __repr__(self):
        return "("+str(self.frame)+"): "+str(self.value)

    def get_value_at(self, frame):
        if self.pattern != None:
            dif = frame-self.frame
            estimate = self.pattern.get_estimated_value(self.value, dif)
        else:
            estimate = self.value
        return estimate

    def compare(self, timevalue):
        estimate = self.get_value_at(timevalue.frame)
        if type(self.pattern) == TimeValuePattern_ParticlePos:
            print timevalue.value, estimate
        return timevalue.value == estimate

