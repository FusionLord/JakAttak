import pygame
from pygame.locals import*

import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from libs.entity.Entity import*
from libs.common import*
from libs.locals import*

import random

class Tile(Entity):
    def __init__(self,world,pos):
        self.world = world
        self.pos = pos
        self.color_index = 0

        self.has_shadow = True

        self.needs_to_rerender = True

        self.init()

    def init(self):
        pass

    def rerender_shadow(self):
        if self.has_shadow:
            rect = pygame.Rect((self.pos[0]*self.world.scale),
                                (self.pos[1]*self.world.scale),
                                self.world.scale,
                                self.world.scale)
            rect = rect.inflate(self.world.scale*TILE_SHADOW_SIZE,self.world.scale*TILE_SHADOW_SIZE)

            self.world.surface.fill(lerp_lists(self.world.bg_color,(0,0,0),0.5), rect)

    def get_color(self):
        if self.color_index == 0:
            color = [255,255,255]
        elif self.color_index == 1:
            color = [32,32,32]
        else:
            color = HSVtoRGB((self.color_index-2)*60,100,100)

        #color[0] += self.offset_color[0]
        #color[1] += self.offset_color[1]
        #color[2] += self.offset_color[2]

        #color[0] = min(max(color[0],0),255)
        #color[1] = min(max(color[1],0),255)
        #color[2] = min(max(color[2],0),255)

        color = lerp_lists((64,64,64),color,0.25)

        color[0] = int(color[0])
        color[1] = int(color[1])
        color[2] = int(color[2])

        return color

    def rerender(self):
        self.needs_to_rerender = False

        rect = ((self.pos[0]*self.world.scale),
                            (self.pos[1]*self.world.scale),
                            self.world.scale,
                            self.world.scale)

        color = self.get_color()

        tile = pygame.Surface((self.world.scale,self.world.scale))
        tile.fill(color)

        self.world.surface.blit(tile,(self.pos[0]*self.world.scale, self.pos[1]*self.world.scale))

