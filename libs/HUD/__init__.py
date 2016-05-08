#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import math

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

##################################

import pygame
from pygame.locals import*

##################################

from libs.locals import *

##################################


def renderText(s, font, font_outline=None, color=(255, 255, 255), outline_color=(32, 32, 32), antialias=False):
    text1 = font.render(s, antialias, color)
    if font_outline:
        text2 = font_outline.render(s, antialias, outline_color)

        surface = pygame.Surface((text2.get_width()+2,text2.get_height()+2), flags=SRCALPHA)
        surface.fill((0,0,0,0))
        surface.blit(text2,(2,2))

        surface.blit(text1,(0,0))
        return surface
    else:
        return text1


def drawRewind(main):
    s = u"«"

    text = renderText(s, main.fonts.get_font(main.fonts.DEFAULT, HUDSIZE),
                      main.fonts.get_font(main.fonts.DEFAULT, HUDSIZE))
    rect = text.get_rect(topright=(main.screen_size[0] - 16, 16))

    main.screen.blit(text, rect)

def drawPause(main):
    s = u"ǁ"

    text = renderText(s, main.fonts.get_font(main.fonts.DEFAULT, HUDSIZE),
                      main.fonts.get_font(main.fonts.DEFAULT, HUDSIZE))
    rect = text.get_rect(topright=(main.screen_size[0] - 16, 16))

    main.screen.blit(text, rect)

def drawStop(main):
    s = u"•"

    text = renderText(s, main.fonts.get_font(main.fonts.DEFAULT, HUDSIZE),
                      main.fonts.get_font(main.fonts.DEFAULT, HUDSIZE))
    rect = text.get_rect(topright=(main.screen_size[0] - 16, 16))

    main.screen.blit(text, rect)

def drawPlay(main):
    s = u"›"

    text = renderText(s, main.fonts.get_font(main.fonts.DEFAULT, HUDSIZE),
                      main.fonts.get_font(main.fonts.DEFAULT, HUDSIZE))
    rect = text.get_rect(topright=(main.screen_size[0] - 16, 16))

    main.screen.blit(text, rect)

def drawScrub(main):
    s = u"‹›"

    text = renderText(s, main.fonts.get_font(main.fonts.DEFAULT, HUDSIZE),
                      main.fonts.get_font(main.fonts.DEFAULT, HUDSIZE))
    rect = text.get_rect(topright=(main.screen_size[0] - 16, 16))

    main.screen.blit(text, rect)

def drawTapeTime(main, t, p=None):
    T = abs(t)

    frames_digits = int(math.ceil(math.log10(main.framerate)))
    frames = T % main.framerate
    seconds = (T / main.framerate) % 60
    minutes = (T / (main.framerate * 60)) % 60
    hours = (T / (main.framerate * 60 * 60)) % 60

    s = "%02d:%02d:%02d:%02d" % (hours,minutes,seconds,frames)
    
    #s = ("{0:0>2}".format(hours)) + ":" + ("{0:0>2}".format(minutes)) + ":" + ("{0:0>2}".format(seconds)) + ":" + (
    #    ("{0:0>" + str(frames_digits) + "}").format(frames))
    #s = str(hours)+":"+str(minutes)+":"+str(seconds)+":"+str(frames)

    if t < 0:
        s = "-" + s
    else:
        s = " " + s

    text = renderText(s, main.fonts.get_font(main.fonts.DEFAULT, HUDSIZE),
                      main.fonts.get_font(main.fonts.DEFAULT, HUDSIZE))
    rect = text.get_rect(bottomleft=(16, main.screen_size[1] - 16))

    main.screen.blit(text, rect)

    if p != None:
        parts = 10
        left_of = int(round(parts*p))
        s = "I" + ("-"*left_of) + "I" + ("-"*(parts-left_of)) + "I"

        text = renderText(s, main.fonts.get_font(main.fonts.DEFAULT, HUDSIZE),
                      main.fonts.get_font(main.fonts.DEFAULT, HUDSIZE))
        rect = text.get_rect(bottomright=(main.screen_size[0] - 16, main.screen_size[1] - 16))

        main.screen.blit(text, rect)
        

