#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import math
import random

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

##################################

import pygame
from pygame.locals import*

##################################

import libs.HUD
from libs.entity.game.World import*
from libs.menu.menus.MainMenu import*
from libs.menu.Menu import*
from libs.common import*
from libs.locals import*

##################################


class PauseMenu(Menu):
    def init(self):
        self.list = ["MAIN MENU","CLOSE"]
        self.selected = 0

        self.screen_cover = pygame.Surface(self.main.screen_size)
        self.screen_cover.set_alpha(127)

    def cleanup(self):
        pass

    def update(self):
        offset = 0
        select = False
        for e in self.main.events:
            if e.type == KEYDOWN:
                if e.key == K_UP:
                    offset -= 1
                elif e.key == K_DOWN:
                    offset += 1
                elif e.key == K_RETURN:
                    select = True
                elif e.key == K_ESCAPE:
                    self.main.paused = False

        self.selected += offset
        self.selected %= len(self.list)

        if select:
            selection = self.list[self.selected]
            if selection == "MAIN MENU":
                self.cleanup()
                self.main.paused = False
                self.main.world.cleanup()
                self.main.world = None
                self.main.menu = libs.menu.menus.MainMenu.MainMenu(self.main)
            elif selection == "CLOSE":
                self.cleanup()
                self.main.world.cleanup()
                self.main.world = None
                self.main.menu = None
                self.main.program_is_running = False

    def render(self):
        self.main.screen.blit(self.screen_cover,(0,0))

        libs.HUD.drawPause(self.main)

        rect = pygame.Rect([4,2,0,0])

        L = ["JAK ATTAK - "+VERSION.upper(),""] + self.list

        for i in xrange(len(self.list)+2):
            color = (255,255,255)
            s = L[i]
            if i >= 2:
                if i-2 == self.selected:
                    s = u'›'+s
                    color = (127,255,0)
                else:
                    s = " "+s
            text = libs.HUD.renderText(s,
                                       self.main.fonts.get_font(self.main.fonts.DEFAULT,HUDSIZE),
                                       color = color,
                                       antialias = True)
            rect = text.get_rect(topleft = (rect.left, rect.bottom+3))

            self.main.screen.blit(text, rect)