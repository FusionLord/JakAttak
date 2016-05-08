import pygame

import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from libs.entity.Entity import*
from libs.locals import*

class Wall(Entity):
    def __init__(self,world,wall_type,pos):
        self.world = world
        self.wall_type = wall_type#0 for horizontal, 1 for vertical
        self.pos = pos

        self.is_solid = True

        self.needs_to_rerender = True

        self.init()

    def init(self):
        pass

    def rerender(self):
        self.needs_to_rerender = False

        wall_width =  max(int(self.world.scale*WALL_THICKNESS),1)
        wall_offset = int((wall_width/2.0 - 0.5))
        
        if self.wall_type == 0:
           rect = pygame.Rect((self.pos[0]*self.world.scale)-wall_offset,
                               (self.pos[1]*self.world.scale)-(wall_width/2),
                               self.world.scale+(wall_offset*2)+1,
                               wall_width+1)
        else:
            rect = pygame.Rect((self.pos[0]*self.world.scale)-(wall_width/2),
                               (self.pos[1]*self.world.scale)-wall_offset,
                               wall_width+1,
                               self.world.scale+(wall_offset*2)+1)

        s = pygame.Surface(rect.size)
        """
        c1 = HSVtoRGB(120,0,100)
        c2 = HSVtoRGB(0,0,100)

        if self.wall_type == 0:
            if self.world.grid[self.pos[1]-1][self.pos[0]].has_shadow:
                C1 = self.world.grid[self.pos[1]-1][self.pos[0]].get_color()
            else:
                C1 = c2

            if self.world.grid[self.pos[1]][self.pos[0]].has_shadow:
                C2 = self.world.grid[self.pos[1]][self.pos[0]].get_color()
            else:
                C2 = c2

        else:
            if self.world.grid[self.pos[1]][self.pos[0]-1].has_shadow:
                C1 = self.world.grid[self.pos[1]][self.pos[0]-1].get_color()
            else:
                C1 = c2

            if self.world.grid[self.pos[1]][self.pos[0]].has_shadow:
                C2 = self.world.grid[self.pos[1]][self.pos[0]].get_color()
            else:
                C2 = c2

        if C1 != c2 and C2 != c2:
            C1 = c2
            C2 = c2

        if self.wall_type == 0:
            if (self.world.v_walls[self.pos[1]-1][self.pos[0]]).is_solid:
                bevel_topleft = True
            else:
                bevel_topleft = False
            if (self.world.v_walls[self.pos[1]-1][self.pos[0]+1]).is_solid:
                bevel_topright = True
            else:
                bevel_topright = False
            if (self.world.v_walls[self.pos[1]][self.pos[0]]).is_solid:
                bevel_bottomleft = True
            else:
                bevel_bottomleft = False
            if (self.world.v_walls[self.pos[1]][self.pos[0]+1]).is_solid:
                bevel_bottomright = True
            else:
                bevel_bottomright = False
        else:
            if (self.world.h_walls[self.pos[1]][self.pos[0]-1]).is_solid:
                bevel_topleft = True
            else:
                bevel_topleft = False
            if (self.world.h_walls[self.pos[1]][self.pos[0]]).is_solid:
                bevel_topright = True
            else:
                bevel_topright = False
            if (self.world.h_walls[self.pos[1]+1][self.pos[0]-1]).is_solid:
                bevel_bottomleft = True
            else:
                bevel_bottomleft = False
            if (self.world.h_walls[self.pos[1]+1][self.pos[0]]).is_solid:
                bevel_bottomright = True
            else:
                bevel_bottomright = False


        for i in xrange(wall_width+1):
            p = i/float(wall_width)
            c = lerp_lists(C1,C2,p)
            if self.wall_type == 0:
                left = rect.left
                right = rect.right

                if bevel_topleft:
                    left = max(left,lerp(rect.left+wall_offset*2,rect.left,p))
                if bevel_bottomleft:
                    left = max(left,lerp(rect.left,rect.left+wall_offset*2,p))

                if bevel_topright:
                    right = min(right,lerp(rect.right-wall_offset*2,rect.right,p))
                if bevel_bottomright:
                    right = min(right,lerp(rect.right,rect.right-wall_offset*2,p))

                pygame.draw.line(self.world.surface, c, (left,rect.top+i), (right,rect.top+i))
            else:
                top = rect.top
                bottom = rect.bottom

                if bevel_topleft:
                    top = max(top,lerp(rect.top+wall_offset*2,rect.top,p))
                if bevel_topright:
                    top = max(top,lerp(rect.top,rect.top+wall_offset*2,p))

                if bevel_bottomleft:
                    bottom = min(bottom,lerp(rect.bottom-wall_offset*2,rect.bottom,p))
                if bevel_bottomright:
                    bottom = min(bottom,lerp(rect.bottom,rect.bottom-wall_offset*2,p))
                pygame.draw.line(self.world.surface, c, (rect.left+i,top), (rect.left+i,bottom))
        """
        s.fill((245,245,245))
        self.world.surface.blit(s,rect)