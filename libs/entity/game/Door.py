import pygame

import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from libs.entity.game.Wall import*
from libs.locals import*
from libs.common import*

class Door(Wall):
    def __init__(self,world,wall_type,pos):
        self.world = world
        self.wall_type = wall_type#0 for horizontal, 1 for vertical
        self.pos = pos

        self.is_solid = True
        self.group = 0
        self.active = False

        self.needs_to_rerender = True

        self.init()

    def init(self):
        pass

    def update(self):
        self.active = self.world.group_status[self.group] > 0
        self.is_solid = not self.active

    def rerender(self):
        self.needs_to_rerender = False

    def render(self):
        self.color = HSVtoRGB(self.group*30,75,75)

        wall_width =  max(int(self.world.scale*WALL_THICKNESS),1)
        wall_offset = int((wall_width/2.0 - 0.5))
        
        if self.wall_type == 0:
           rect = pygame.Rect((self.pos[0]*self.world.scale)-wall_offset+self.world.pos[0],
                               (self.pos[1]*self.world.scale)-(wall_width/2)+self.world.pos[1],
                               self.world.scale+(wall_offset*2)+1,
                               wall_width+1)
        else:
            rect = pygame.Rect((self.pos[0]*self.world.scale)-(wall_width/2)+self.world.pos[0],
                               (self.pos[1]*self.world.scale)-wall_offset+self.world.pos[1],
                               wall_width+1,
                               self.world.scale+(wall_offset*2)+1)
        s = pygame.Surface(rect.size)
        s.fill(self.color)
        if not self.is_solid:
            s.set_alpha(127)

        self.world.main.screen.blit(s,rect)

