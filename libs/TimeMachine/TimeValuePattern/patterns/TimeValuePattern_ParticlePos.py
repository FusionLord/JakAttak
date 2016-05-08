import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from libs.TimeMachine.TimeValuePattern.TimeValuePattern import*

class TimeValuePattern_ParticlePos(TimeValuePattern):
    def __init__(self, speed, velocity, mass):
        self.speed = speed
        self.velocity = velocity
        self.mass = mass

    def get_estimated_value(self, start_value, timedif):
        dif = timedif

        p = (1.0 - (1.0-(1.0/self.mass))**dif)
        max_offset = (self.speed*self.mass)

        x = start_value[0] + self.velocity[0] * max_offset * p
        y = start_value[1] + self.velocity[1] * max_offset * p

        return (x,y)