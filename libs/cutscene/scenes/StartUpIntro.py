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
import libs.viseffect
from libs.cutscene.Cutscene import*
from libs.common import*
from libs.locals import*

##################################


class StartUpIntro(Cutscene):
    def init(self):
        self.start_time = float(self.main.time)
        self.sound = self.main.sounds.get_sound("sfx/vcr/vcr_insert.wav")
        self.channel = self.play_sound(self.sound, force = True)

    def cleanup(self):
        self.channel.stop()

    def update(self):
        if self.is_alive():
            dif = self.main.time - self.start_time

            if dif >= 21:
                self.kill()
            else:
                if dif > 10:
                    self.bg_color = (96,64,64)
                elif dif > 8:
                    self.bg_color = (36,36,36)
                elif dif > 3.25:
                    self.bg_color = (32,32,255)
                elif dif > 2.25:
                    self.bg_color = lerp_lists((32,32,32),(255,255,255),(max((0.75-(dif-2.25)),0)/0.75)**32)
                    self.bg_color = (int(self.bg_color[0]),int(self.bg_color[1]),int(self.bg_color[2]))
                else:
                    self.bg_color = (0,0,0)

                for event in self.main.events:
                    if event.type in [KEYDOWN,MOUSEBUTTONDOWN]:
                        if (event.type == KEYDOWN and str(event.unicode) != "") or event.type == MOUSEBUTTONDOWN:
                            self.kill()

    def render(self):
        if self.is_alive():
            dif = self.main.time - self.start_time

            self.main.screen.fill(self.bg_color)

            if dif >10 and dif <15:
                s = libs.HUD.renderText("RAUBANA PRESENTS", self.main.fonts.get_font(self.main.fonts.DEFAULT,HUDSIZE), antialias=True)
                r = s.get_rect(center = (self.main.screen_size[0]/2, self.main.screen_size[1]/2))
                self.main.screen.blit(s,r)

            if dif >16 and dif <20:
                s = libs.HUD.renderText("JAK ATTAK - "+VERSION.upper(), self.main.fonts.get_font(self.main.fonts.DEFAULT,HUDSIZE), antialias=True)
                r = s.get_rect(center = (self.main.screen_size[0]/2, self.main.screen_size[1]/2))
                self.main.screen.blit(s,r)

            if dif > 3 and dif <= 11:
                libs.HUD.drawPlay(self.main)

            if dif >8 and dif <11:
                libs.HUD.drawTapeTime(self.main, int((dif-11)*self.main.framerate))
            elif dif > 3 and dif <= 8:
                libs.HUD.drawTapeTime(self.main, -3)

            #static
            if dif > 8:
                particles = lerp(0,random.randint(0,300),(max(((21-8)-(dif-8)),0)/(21-8))**4)
            elif dif > 2.25:
                particles = 1
            else:
                particles = 0

            libs.viseffect.static(self.main.screen, int(particles), 1, 4)

            if dif > 8:
                #tape jitter
                height = int(lerp(0,self.main.screen_size[1]*0.02, math.sqrt(((21-8)-(dif-8))/(21-8)) ))
                bands = int(lerp(0,8,max(((21-8)-(dif-8)),0)/(21-8)))
                h_jitter = 8
                v_jitter = 4
                total = height*bands
                libs.viseffect.tape_jitter(self.main.screen, 0, height, bands, h_jitter, v_jitter, True)
                libs.viseffect.tape_jitter(self.main.screen, -total, height, bands, h_jitter, v_jitter)


