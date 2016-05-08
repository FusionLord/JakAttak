import os
import sys
import time
import math
import random
from libs import HUD

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

##################################

import pygame
from pygame.locals import*
pygame.mixer.pre_init(frequency=44100, buffer = 2**10)

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()

pygame.mixer.set_num_channels(50)

##################################

import libs.SoundSystem
import libs.FontSystem
from libs.cutscene.scenes.StartUpIntro import*
from libs.menu.menus.MainMenu import*
from libs.locals import*

##################################

class Main(object):
    def __init__(self):
        #sets up the screen
        self.screen_size = SCREENSIZE
        if FULLSCREEN_MODE:
            self.screen = pygame.display.set_mode(self.screen_size, FULLSCREEN)
            time.sleep(2)
        else:
            self.screen = pygame.display.set_mode(self.screen_size)
        if SCREENSIZE[0] == 0 and SCREENSIZE[1] == 0:
            self.screen_size = self.screen.get_size()

        self.framerate = FRAMERATE
        self.clock = pygame.time.Clock()

        self.__update_vars()

        self.sounds = libs.SoundSystem.SoundSystem()
        self.fonts = libs.FontSystem.FontSystem()

        self.cutscene = StartUpIntro(self)
        self.menu = MainMenu(self)
        self.world = None

        self.paused = False

    def cleanup(self):
        pygame.display.quit()
        pygame.mixer.quit()
        pygame.quit()
        sys.exit()

    def __update_vars(self):
        self.events = pygame.event.get()
        self.keys = pygame.key.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_button = pygame.mouse.get_pressed()
        self.time = time.time()

    def __update(self):
        if self.world:
            #this means that we're in game right now
            if self.paused and self.menu:
                self.menu.update()
            else:
                if self.cutscene:
                    #this means a cutscene is playing
                    self.cutscene.update()
                else:
                    #runs the simulation
                    self.world.update()
        else:
            #this means no game is currently loaded, so it's either cut-scenes or menus
            if self.cutscene:
                #this means a cutscene is playing
                self.cutscene.update()
            elif self.menu:
                #runs the menu
                self.menu.update()

    def __move(self):
        if self.world:
            #this means that we're in game right now
            if self.paused:
                self.menu.move()
            else:
                if self.cutscene:
                    #this means a cutscene is playing
                    self.cutscene.move()
                    if not self.cutscene.is_alive():
                        #removes the cutscene
                        self.cutscene = None
                else:
                    #runs the simulation
                    self.world.move()
        else:
            #this means no game is currently loaded, so it's either cut-scenes or menus
            if self.cutscene:
                #this means a cutscene is playing
                self.cutscene.move()
                if not self.cutscene.is_alive():
                    #removes the cutscene
                    self.cutscene = None
            elif self.menu:
                #runs the menu
                self.menu.move()

    def __render(self):
        if self.world:
            self.world.render()

        if self.cutscene:
            self.cutscene.render()

        if (((self.world or self.cutscene) and self.paused) or (not (self.world or self.cutscene))) and self.menu:
            self.menu.render()

        rect = pygame.Rect([4,2,0,0])

        #fps
        s = "FPS: "+str(int(self.clock.get_fps()))
        text = HUD.renderText(s, self.fonts.get_font(self.fonts.DEFAULT, 16), antialias=True)
        rect = text.get_rect(topleft = rect.bottomleft)

        self.screen.blit(text, rect)

        pygame.display.flip()

    def run(self):
        self.program_is_running = True
        while self.program_is_running:
            self.clock.tick(self.framerate)
            self.__update_vars()

            self.__update()
            self.__move()

            self.__render()
        self.cleanup()
