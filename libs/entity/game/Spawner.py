import pygame

import os
from libs.entity.game.npc.Jak import Jak

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from libs.entity.Entity import*
from libs.common import*

from libs.TimeMachine.PickledEntity import*
from libs.TimeMachine.TimeValue import*
from libs.TimeMachine.TimeValuePattern.patterns.TimeValuePattern_SawIncrement import*
from libs.TimeMachine.TimeValuePattern.patterns.TimeValuePattern_VectorIncrement import*
from libs.TimeMachine.TimeValuePattern.patterns.TimeValuePattern_VectorSquareIncrement import*
from libs.entity.game.particles.Gib import*
from libs.viseffect import*
from libs.entity.game.particles.FleshChunk import*
from libs.common import*
from libs.HUD import*

import random
import math

class Spawner(Entity):
    TYPES = ("entity","spawner")
    SIZE = (0.5,0.5)
    COLLISION_FILTER = tuple(["NONE"])

    def init(self):
        self.delay = 0
        self.delay_time = 60

        self.color = (255,255,255)

        self.set_id()

    def pickle(self):
        pickle = PickledEntity(int(self.ID), self.world.framenumber, type(self))
        pickle.update_value("alive",TimeValue(bool(self.alive), self.world.framenumber))
        pickle.update_value("pos",TimeValue(tuple(self.pos), self.world.framenumber))
        pickle.update_value("size",TimeValue(tuple(self.size), self.world.framenumber))
        pickle.update_value("health",TimeValue(float(self.health), self.world.framenumber))
        pickle.update_value("delay",TimeValue(int(self.delay),
                                              self.world.framenumber,
                                              TimeValuePattern_SawIncrement(0,self.delay_time+1,-1)))
        pickle.update_value("delay_time",TimeValue(int(self.delay_time), self.world.framenumber))

        return pickle

    def unpickle(self, world, pickledentity):
        pos = pickledentity.tracks["pos"][0].get_value_at(None)
        size = pickledentity.tracks["size"][0].get_value_at(None)

        self.__init__(world,pos,size)

        self.ID = pickledentity.ID

        self.alive = pickledentity.tracks["alive"][0].get_value_at(None)
        self.health = pickledentity.tracks["health"][0].get_value_at(None)
        self.pos = pos
        self.delay = pickledentity.tracks["delay"][0].get_value_at(None)
        self.delay_time = pickledentity.tracks["delay_time"][0].get_value_at(None)

    def update(self):
        if self.is_alive():
            if self.delay == 0:
                self.delay = int(self.delay_time)
                j = Jak(self.world, tuple(self.pos))
                j.facing = 2
                j.target_facing = 2
                self.world.characters.append(j)
            else:
                self.delay -= 1

    def render(self):
        if self.alive:
            render_pos = [int(self.world.pos[0]+((self.pos[0]+0.5)*self.world.scale)),int(self.world.pos[1]+((self.pos[1]+0.5)*self.world.scale))]

            radius = max(int(  (self.world.scale * max(self.size)) * 0.5 ),1)
            pos = (int(render_pos[0]), int(render_pos[1]))
            rect = pygame.Rect((pos[0]-radius,pos[1]-radius,radius*2,radius*2))

            draw_rect_shadow(self.world.main.screen, rect, int(max(self.world.scale*0.025,1)), 64)
            pygame.draw.rect(self.world.main.screen, self.color, rect)

            if self.world.paused and not self.world.main.paused and not self.world.is_preview:
                font = self.world.main.fonts.get_font(self.world.main.fonts.DEFAULT, 8)
                text = renderText(str(self.delay_time),font, font, antialias=True)

                rect = text.get_rect(center = pos)
                self.world.main.screen.blit(text,rect)

