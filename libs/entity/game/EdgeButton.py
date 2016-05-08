import pygame
from pygame.locals import*
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from libs.entity.Entity import*
from libs.TimeMachine.PickledEntity import*
from libs.TimeMachine.TimeValue import*
from libs.entity.game.Button import*
from libs.common import*

import random
import math

class EdgeButton(Button):
    TYPES = ["entity","button","edgebutton"]
    SIZE = (2,2)

    def init(self):
        self.render_above = False

        self.group = 0

        self.edge = False
        self.active = False

        self.set_id()

    def update(self):
        if self.alive:
            edge = False
            active = False

            for ent in self.collisions:
                if "jak" in ent.TYPES and ent.is_alive():
                    dif1 = (abs(ent.pos[0]-self.pos[0]),abs(ent.pos[1]-self.pos[1]))
                    dif2 = (abs(ent.target_pos[0]-self.pos[0]),abs(ent.target_pos[1]-self.pos[1]))

                    if max(dif2) == 0 and max(max(dif1),max(dif2)) != 0 and ent.interp_amount >= ent.speed-1:
                        edge = True
                        break

            if edge != self.edge:
                active = edge
                self.edge = edge

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

            radius = max(int(  (self.world.scale * 0.5) * 0.8 ),1)
            eye_radius = max(int(  (self.world.scale * 0.5) * 0.6 ),0.5)

            rect = pygame.Rect((pos[0]-radius,pos[1]-radius,radius*2,radius*2))
            pygame.draw.rect(self.world.main.screen, lerp_lists((0,0,0),self.color,0.25), rect)

            if not self.active:
                color = self.color
            else:
                color = lerp_lists((0,0,0),self.color,0.25)

            pygame.draw.rect(self.world.main.screen, color, (pos[0]-eye_radius,pos[1]-eye_radius,eye_radius*2,eye_radius*2))


