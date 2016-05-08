import pygame
from pygame.locals import*

import random
import math

from common import*

def tape_jitter(surface, top_pos, height, bands, horizontal_jitter, vertical_jitter, reverse=False, seed=None):
    R = random.Random()

    if seed:
        R.seed(seed)

    original_screen = surface.copy()
    surface_size = surface.get_size()

    for i in xrange(bands):
        if reverse:
            pos = ((top_pos+(height*bands)-(i*height))%(surface_size[1]+height))
        else:
            pos = ((top_pos+(i*height))%(surface_size[1]+height))
        pos %= surface_size[1]+height
        pos -= height
        s = pygame.Surface((int(surface_size[0]), int(height)))

        if bands == 1:
            p = 1
        else:
            p = (i/float(bands-1))**2

        if horizontal_jitter < 1 and vertical_jitter < 1:
            s.set_alpha( int(lerp(0,127,p)) )
            surface.blit(s,(0,pos))
        else:
            surface.blit(s,(0,pos))

            for color in xrange(3):
                s = pygame.Surface((int(surface_size[0]), int(height)))

                v_offset = lerp(0,vertical_jitter,p)

                if v_offset < 1:
                    if v_offset < R.random():
                        v_offset = 0
                    else:
                        v_offset = R.randint(0,1)*2-1
                else:
                    v_offset = v_offset * R.random() * (R.randint(0,1)*2-1)

                v_offset = int(round(v_offset))

                s.blit(original_screen, (0,-pos + v_offset) )

                s2 = pygame.Surface((int(surface_size[0]), int(height))).convert()
                if color == 0:
                    s2.fill((255,0,0))
                elif color == 1:
                    s2.fill((0,255,0))
                elif color == 2:
                    s2.fill((0,0,255))

                s.blit(s2,(0,0),special_flags = BLEND_RGB_MULT)


                h_offset = lerp(0,horizontal_jitter,p)

                if h_offset < 1:
                    if h_offset < R.random():
                        h_offset = 0
                    else:
                        h_offset = R.randint(0,1)*2-1
                else:
                    h_offset = h_offset * R.random() * (R.randint(0,1)*2-1)

                h_offset = int(round(h_offset))

                s.scroll(h_offset,0)

                s2.fill((0,0,0))
                s2.set_alpha( int(lerp(0,127,p)) )
                s.blit(s2,(0,0))
                surface.blit(s, (0,int(pos)), special_flags = BLEND_RGB_ADD)

def tape_pull(surface, mid_pos, height, bands, amount):
    original_screen = surface.copy()
    surface_size = surface.get_size()

    for i in xrange(bands):
        pos = ((mid_pos+(i*height))%(surface_size[1]+height)) - ((height*bands)/2.0)
        pos %= surface_size[1]+height
        pos -= height
        s = pygame.Surface((int(surface_size[0]), int(height)))

        if bands == 1:
            p = 1
        else:
            p = (i/float(bands-1))**2

        s = pygame.Surface((int(surface_size[0]), int(height)))

        s.blit(original_screen, (0,-pos) )

        h_offset = lerp(0,amount,(math.sin(p*math.pi))**2)

        h_offset = int(round(h_offset))

        s.scroll(h_offset,0)

        surface.blit(s, (0,int(pos)))


def static(surface, count, minwidth, maxwidth, max_alpha = 127, seed = None):
    size = surface.get_size()

    R = random.Random()

    if seed:
        R.seed(seed)

    for i in xrange( count ):
        width = R.randint(minwidth,maxwidth)*2
        rect = pygame.Rect((R.randint(-width,size[0]),R.randint(0,size[1]),width,2))
        s = pygame.Surface(rect.size)
        s.fill((R.randint(0,255),R.randint(0,255),R.randint(0,255)))
        s.set_alpha(int(max_alpha*R.random()*R.random()))
        surface.blit(s,rect)


def bulge(surface, pos, radius, depth, inverted = False, rectangular = False):
    original_size = (radius*2,radius*2)
    if rectangular:
        new_surface = pygame.Surface(original_size)
    else:
        new_surface = pygame.Surface(original_size, flags=SRCALPHA)

    new_surface.fill((0,0,0,0))

    for i in xrange(radius+1):
        p = i/float(radius)

        size = (lerp(original_size[0],0,p),lerp(original_size[1],0,p))

        if inverted:
            p = 1 - p

        if depth>0:
            p = p ** (1/float(depth+1))
        else:
            p = p ** (float(abs(depth)+1))

        if inverted:
            p = 1 - p

        new_size = (lerp(original_size[0],0,p),lerp(original_size[1],0,p))

        s = pygame.Surface(new_size)
        s.blit(surface, (-(pos[0]-(new_size[0])/2),-(pos[1]-(new_size[1])/2)))

        s2 = pygame.transform.scale(s,(int(size[0]),int(size[1])))
        if not rectangular:
            s2.set_colorkey((255,255,0))

            s3 = pygame.Surface(size)
            s3.fill((255,255,0))
            s3.set_colorkey((1,1,1))
            pygame.draw.circle(s3, (1,1,1), (int(size[0]/2),int(size[1]/2)), int(min(size)/2))

            s2.blit(s3, (0,0))

        new_surface.blit(s2, ((original_size[0]-size[0])/2,(original_size[1]-size[1])/2))

    surface.blit(new_surface,(pos[0]-radius,pos[1]-radius))


def draw_rect_shadow(surface, rect, size, alpha):
    s1 = pygame.Surface((rect.width+(size*2), size))
    s2 = pygame.Surface((size, rect.height))

    s1.set_alpha(alpha)
    s2.set_alpha(alpha)

    surface.blit(s1, (rect.left-size,rect.top-size))
    surface.blit(s1, (rect.left-size,rect.bottom))
    surface.blit(s2, (rect.left-size,rect.top))
    surface.blit(s2, (rect.right,rect.top))


def draw_letterboxing(surface, amount, alpha):
    size = surface.get_size()

    s = pygame.Surface((size[0],amount))
    s.set_alpha(alpha)

    surface.blit(s, (0,0))
    surface.blit(s, (0,size[1]-amount))



