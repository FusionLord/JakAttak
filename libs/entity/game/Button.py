import pygame
from pygame.locals import*
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from libs.entity.Entity import*
from libs.TimeMachine.PickledEntity import*
from libs.TimeMachine.TimeValue import*
from libs.common import*

import random
import math

class Button(Entity):
    TYPES = ["entity","button"]
    SIZE = (2,2)

    def init(self):
        self.render_above = False

        self.group = 0

        self.active = False

        self.set_id()

    def cleanup(self):
        if self.active:
            self.active = False
            self.world.next_group_status[self.group] -= 1

    def pickle(self):
        pickle = PickledEntity(int(self.ID), self.world.framenumber, type(self))
        pickle.update_value("_alive",TimeValue(bool(self.alive), self.world.framenumber))
        pickle.update_value("_group",TimeValue(int(self.group), self.world.framenumber))
        pickle.update_value("_active",TimeValue(int(self.active), self.world.framenumber))
        pickle.update_value("pos",TimeValue(tuple(self.pos),self.world.framenumber))
        pickle.update_value("size",TimeValue(tuple(self.size),self.world.framenumber))
        return pickle

    def unpickle(self, world, pickledentity):
        pos = pickledentity.tracks["pos"][0].get_value_at(None)
        size = pickledentity.tracks["size"][0].get_value_at(None)

        self.__init__(world,pos,size)

        self.ID = pickledentity.ID

        self.alive = pickledentity.tracks["_alive"][0].get_value_at(None)
        self.pos = pos
        self.active = pickledentity.tracks["_active"][0].get_value_at(None)
        self.group = pickledentity.tracks["_group"][0].get_value_at(None)

    def update(self):
        if self.alive:
            active = False

            for ent in self.collisions:
                if "jak" in ent.TYPES and ent.is_alive():
                    dif1 = (abs(ent.pos[0]-self.pos[0]),abs(ent.pos[1]-self.pos[1]))
                    dif2 = (abs(ent.target_pos[0]-self.pos[0]),abs(ent.target_pos[1]-self.pos[1]))

                    if max(dif2) == 0 or max(dif1) == 0:
                        active = True
                        break

            if active != self.active:
                self.active = active

                if self.active:
                    self.world.next_group_status[self.group] += 1
                else:
                    self.world.next_group_status[self.group] -= 1

    def render(self):
        if self.alive:
            self.color = HSVtoRGB(self.group*30,75,75)

            pos = [int(self.world.pos[0]+((self.pos[0]+0.5)*self.world.scale)),int(self.world.pos[1]+((self.pos[1]+0.5)*self.world.scale))]

            radius = max(int(  (self.world.scale * 0.5) * 0.75 ),1)
            eye_radius = max(int(  (self.world.scale * 0.5) * 0.75 ),0.5)

            if not self.active:
                color = self.color
            else:
                color = lerp_lists((0,0,0),self.color,0.25)

            pygame.draw.rect(self.world.main.screen, color, (pos[0]-eye_radius,pos[1]-eye_radius,eye_radius*2,eye_radius*2))


