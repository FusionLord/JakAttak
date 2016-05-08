import os
import math


parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

##################################

import pygame
from pygame.locals import *

##################################

from libs.TimeMachine.PickledEntity import*
from libs.TimeMachine.TimeValue import*
from libs.TimeMachine.TimeValuePattern.patterns.TimeValuePattern_Increment import*
from libs.TimeMachine.TimeValuePattern.patterns.TimeValuePattern_ParticlePos import*
from libs.entity.Entity import*
from libs.raytrace.Hull import*
from libs.common import*

##################################

class Gib(Entity):
    TYPES = tuple(["gib"])
    SIZE = (0.0,0.0)

    def __init__(self, world=None, pos=None, size=None, mass=None, velocity=None, speed=None, restitution=None, pickle_data=None):
        if not pickle_data:
            self.world = world

            self.die_on_stop_moving = True
            self.health = 60
            self.max_health = int(self.health)
            self.alive = True

            self.render_above = True

            self.color = (0,0,0)
            self.alpha = 255

            self.start_frame = int(world.framenumber)
            self.end_pos = None
            self.start_pos = tuple(pos)

            self.impact_pos = []

            if not size:
                self.size = tuple(self.SIZE)
            else:
                self.size = size
            self.mass = mass
            self.velocity = tuple(velocity)
            self.speed = speed
            self.restitution = restitution

            self.moving = True

            self.set_id()

            self.init()
        else:
            self.unpickle(world, pickle_data)

    def init(self):
        pass

    def pickle(self):
        pickle = PickledEntity(int(self.ID), self.world.framenumber, type(self))
        pickle.update_value("alive",TimeValue(bool(self.alive), self.world.framenumber))
        if self.moving:
            pickle.update_value("health",TimeValue(float(self.health), self.world.framenumber))
        else:
            pickle.update_value("health",
                                TimeValue(float(self.health),
                                          self.world.framenumber,
                                          TimeValuePattern_Increment(-1)))
        pickle.update_value("max_health",TimeValue(float(self.max_health), self.world.framenumber))
        pickle.update_value("render_above",TimeValue(float(self.render_above), self.world.framenumber))
        pickle.update_value("color",TimeValue(tuple(self.color), self.world.framenumber))
        pickle.update_value("alpha",TimeValue(float(self.alpha), self.world.framenumber))
        pickle.update_value("start_frame",TimeValue(int(self.start_frame), self.world.framenumber))
        pickle.update_value("start_pos",TimeValue(tuple(self.start_pos), self.world.framenumber))
        if self.end_pos == None:
            pickle.update_value("end_pos",TimeValue(None, self.world.framenumber))
        else:
            pickle.update_value("end_pos",TimeValue(tuple(self.end_pos), self.world.framenumber))
        pickle.update_value("impact_pos",TimeValue(tuple(self.impact_pos), self.world.framenumber))
        pickle.update_value("size",TimeValue(tuple(self.size), self.world.framenumber))
        pickle.update_value("mass",TimeValue(float(self.mass), self.world.framenumber))
        pickle.update_value("velocity",TimeValue(tuple(self.velocity), self.world.framenumber))
        pickle.update_value("speed",TimeValue(float(self.speed), self.world.framenumber))
        pickle.update_value("restitution",TimeValue(float(self.restitution), self.world.framenumber))
        pickle.update_value("moving",TimeValue(bool(self.moving), self.world.framenumber))

        return pickle

    def unpickle(self, world, pickledentity):
        pos = pickledentity.tracks["start_pos"][0].get_value_at(None)
        size = pickledentity.tracks["size"][0].get_value_at(None)
        mass = pickledentity.tracks["mass"][0].get_value_at(None)
        velocity = pickledentity.tracks["velocity"][0].get_value_at(None)
        speed = pickledentity.tracks["speed"][0].get_value_at(None)
        restitution = pickledentity.tracks["restitution"][0].get_value_at(None)

        self.__init__(world, pos, size, mass, velocity, speed, restitution)

        self.ID = pickledentity.ID

        self.alive = pickledentity.tracks["alive"][0].get_value_at(None)
        self.health = pickledentity.tracks["health"][0].get_value_at(None)
        self.max_health = pickledentity.tracks["max_health"][0].get_value_at(None)
        self.render_above = pickledentity.tracks["render_above"][0].get_value_at(None)
        self.color = pickledentity.tracks["color"][0].get_value_at(None)
        self.alpha = pickledentity.tracks["alpha"][0].get_value_at(None)
        self.start_frame = pickledentity.tracks["start_frame"][0].get_value_at(None)
        self.end_pos = pickledentity.tracks["end_pos"][0].get_value_at(None)
        self.start_pos = pos
        self.impact_pos = pickledentity.tracks["impact_pos"][0].get_value_at(None)
        self.size = pickledentity.tracks["size"][0].get_value_at(None)
        self.mass = mass
        self.velocity = velocity
        self.speed = speed
        self.restitution = restitution
        self.moving = pickledentity.tracks["moving"][0].get_value_at(None)

    def get_pos_at_frame(self, frame):
        dif = frame - self.start_frame - 1

        if frame == self.start_frame:
            return self.start_pos

        p = (1.0 - (1.0-(1.0/self.mass))**dif)
        max_offset = (self.speed*self.mass)

        x = self.start_pos[0] + self.velocity[0] * max_offset * p
        y = self.start_pos[1] + self.velocity[1] * max_offset * p

        return (x,y)

    def get_speed_at_frame(self, frame):
        dif = frame - self.start_frame

        p = (1.0-(1.0/self.mass))**dif

        return p * self.speed

    def update(self):
        if (self.die_on_stop_moving and not self.moving) or not self.die_on_stop_moving:
            self.health -= 1
            if self.health <= 0:
                self.alive = False


    def move(self):
        self.impact_pos = []

        pos = self.get_pos_at_frame(self.world.framenumber)

        if self.moving:
            speed = self.get_speed_at_frame(self.world.framenumber)
            if speed * self.world.scale <= 1.0/float(self.world.main.framerate):
                self.moving = False
                self.end_pos= pos
            else:
                rect = [pos[0]-(self.size[0]/2.0),pos[1]-(self.size[1]/2.0),self.size[0],self.size[1]]

                if rect[0]+rect[2] <= 0 or rect[1]+rect[3] <= 0 or rect[0] > self.world.grid_size[0] or rect[1] > self.world.grid_size[1]:
                    self.alive = False
                else:
                    start = pos
                    end = self.get_pos_at_frame(self.world.framenumber+1)
                    vel = list(self.velocity)

                    remaining_distance = math.sqrt((end[0]-start[0])**2+(end[1]-start[1])**2)

                    ray = Hull(self.world, start, end, self.size)
                    ray.end_pos = start
                    ray.test_can_extend()

                    while remaining_distance > 0:
                        dist = math.sqrt((ray.end_pos[0]-ray.start_pos[0])**2+(ray.end_pos[1]-ray.start_pos[1])**2)
                        if dist > remaining_distance:
                            #we've hit the limit, no need to continue
                            break
                        else:
                            #checks if ray is even inside of the grid
                            if ray.end_pos[0] < 0 or ray.end_pos[1] < 0 or ray.end_pos[0] > self.world.grid_size[0] or ray.end_pos[1] > self.world.grid_size[1]:
                                pass
                            else:
                                if not ray.can_extend:
                                    self.impact_pos.append(ray.end_pos)

                                    if ray.impact_horiz:
                                        vel[1] *= -1
                                    if ray.impact_verti:
                                        vel[0] *= -1

                                    remaining_distance -= dist
                                    remaining_distance *= self.restitution

                                    start = tuple(ray.end_pos)
                                    end = (start[0]+vel[0]*remaining_distance,start[1]+vel[1]*remaining_distance)

                                    ray = Hull(self.world, start, end, self.size)
                                    ray.end_pos = start
                                    ray.test_can_extend()
                        ray.extend()

                    if len(self.impact_pos) > 0:
                        self.speed = self.get_speed_at_frame(self.world.framenumber)*(self.restitution**len(self.impact_pos))
                        self.velocity = vel
                        self.start_pos = end
                        self.start_frame = int(self.world.framenumber)

    def render(self):
        if self.moving:
            pos = list(self.get_pos_at_frame(self.world.framenumber))
        else:
            pos = list(self.end_pos)

        size = list(self.size)

        size[0] = size[0]*self.world.scale
        size[1] = size[1]*self.world.scale

        size[0] = round((size[0])/PRECISION)*PRECISION
        size[1] = round((size[1])/PRECISION)*PRECISION

        size[0] = max(size[0],PRECISION)
        size[1] = max(size[1],PRECISION)

        topleft = list(pos)

        topleft[0] = self.world.pos[0]+(topleft[0]*self.world.scale)
        topleft[1] = self.world.pos[1]+(topleft[1]*self.world.scale)

        topleft[0] -= size[0]/2.0
        topleft[1] -= size[1]/2.0

        bottomright = [topleft[0]+size[0],
                        topleft[1]+size[1]]

        topleft[0] = round((topleft[0])/PRECISION)*PRECISION
        topleft[1] = round((topleft[1])/PRECISION)*PRECISION

        bottomright[0] = round((bottomright[0])/PRECISION)*PRECISION
        bottomright[1] = round((bottomright[1])/PRECISION)*PRECISION

        new_size = (bottomright[0]-topleft[0],bottomright[1]-topleft[1])

        surface = pygame.Surface((new_size[0],new_size[1]))
        surface.fill(self.color)
        surface.set_alpha(max(int(self.alpha*((self.health/float(self.max_health)))),0))
        rect = surface.get_rect(topleft = (int(topleft[0]),int(topleft[1])))

        self.world.main.screen.blit(surface, rect)
