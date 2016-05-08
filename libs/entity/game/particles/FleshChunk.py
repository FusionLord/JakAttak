import os
import math

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

##################################

import pygame
from pygame.locals import *

##################################

from libs.entity.game.particles.Gib import*
from libs.common import*

##################################

class FleshChunk(Gib):
    TYPES = ["gib","fleshchunk"]

    def update(self):
        if self.alpha > 127:
            self.alpha -= 5
            if self.alpha < 127:
                self.alpha = 127
        my_prev_pos = self.get_pos_at_frame(self.world.framenumber-1)
        my_pos = self.get_pos_at_frame(self.world.framenumber)
        my_speed = self.get_speed_at_frame(self.world.framenumber)

        for p in self.impact_pos:
            for x in xrange(random.randint(1,3)):
                pos = lerp_lists(p,my_pos,0.5)
                size = (0.0,0.0)
                ang = math.radians(random.randint(0,360))
                mass = 2

                velocity = (math.cos(ang),math.sin(ang))
                speed = 3*(my_speed)

                v = (velocity[0]*speed+0.5*my_speed*(self.velocity[0]),
                            velocity[1]*speed+0.5*my_speed*(self.velocity[1]))

                speed = math.sqrt(v[0]**2+v[1]**2)
                velocity = [v[0]/speed, v[1]/speed]

                restitution = 0.2

                gib = Gib(self.world, pos, size, mass, velocity, speed, restitution)
                gib.color = lerp_lists((0,0,0),self.color,0.9)
                gib.alpha = 127
                gib.health = int(60*0.1)
                gib.max_health = int(gib.health)

                self.world.gibs.append(gib)

        if not self.moving:
            self.health -= 1
            if self.health <= 0:
                self.alive = False
        else:
            if my_speed/2.0 > 0:
                if my_speed > 0.01:
                    if self.world.framenumber%8 == 0:
                        particles = 1
                    else:
                        particles = 0
                else:
                    particles = 0

                for x in xrange(particles):
                    pos = lerp_lists(my_pos,my_prev_pos,random.random())
                    size = (0.05,0.05)
                    ang = math.radians(random.randint(0,360))
                    mass = 4

                    velocity = (math.cos(ang),math.sin(ang))
                    speed = 0.05*random.random()

                    v = (velocity[0]*speed+0.5*my_speed*(self.velocity[0]),
                            velocity[1]*speed+0.5*my_speed*(self.velocity[1]))

                    speed = math.sqrt(v[0]**2+v[1]**2)
                    velocity = [v[0]/speed, v[1]/speed]

                    restitution = 0.2

                    gib = Gib(self.world, pos, size, mass, velocity, speed, restitution)
                    gib.color = lerp_lists((0,0,0),self.color,0.9)
                    gib.alpha = 127
                    gib.render_above = False
                    gib.health = int(60*0.5)
                    gib.max_health = int(gib.health)

                    self.world.gibs.append(gib)
