import pygame
from pygame.locals import*
import os
from libs import viseffect
from libs.TimeMachine.PickledEntity import PickledEntity
from libs.TimeMachine.TimeValue import TimeValue
from libs.entity.game.particles.Flame import Flame
from libs.entity.game.particles.Gib import Gib
from libs.raytrace import Hull
from libs.viseffect import*

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from libs.entity.Entity import*
from libs.entity.game.particles.Gib import*
from libs.common import*

import random
import math

class Mine(Entity):
    TYPES = ("entity","mine")
    SIZE = (0.3,0.3)

    def init(self):
        self.render_above = False

        self.color = (0,255,0)

        self.range = 1.5

        self.active = False
        self.delay_before_active = 60
        self.delay_before_explode = 15

        self.exploding = False

        self.last_rendered_range_surface = long(-1)
        self.range_surface = None

        self.set_id()

    def pickle(self):
        pickle = PickledEntity(int(self.ID), self.world.framenumber, Mine)
        pickle.update_value("alive",TimeValue(bool(self.alive), self.world.framenumber))
        pickle.update_value("pos",TimeValue(tuple(self.pos), self.world.framenumber))
        pickle.update_value("range",TimeValue(float(self.range), self.world.framenumber))
        pickle.update_value("active",TimeValue(bool(self.active), self.world.framenumber))
        pickle.update_value("delay_before_active",TimeValue(int(self.delay_before_active), self.world.framenumber))
        pickle.update_value("delay_before_explode",TimeValue(int(self.delay_before_explode), self.world.framenumber))
        pickle.update_value("exploding",TimeValue(bool(self.exploding), self.world.framenumber))
        return pickle

    def unpickle(self, world, pickledentity):
        pos = pickledentity.tracks["pos"][0].get_value_at(None)

        self.__init__(world,pos)

        self.ID = pickledentity.ID

        self.alive = pickledentity.tracks["alive"][0].get_value_at(None)
        self.range = pickledentity.tracks["range"][0].get_value_at(None)
        self.active = pickledentity.tracks["active"][0].get_value_at(None)
        self.delay_before_active = pickledentity.tracks["delay_before_active"][0].get_value_at(None)
        self.delay_before_explode = pickledentity.tracks["delay_before_explode"][0].get_value_at(None)
        self.exploding = pickledentity.tracks["exploding"][0].get_value_at(None)

    def update(self):
        if self.alive:
            if not self.active:
                self.delay_before_active -= 1
                if self.delay_before_active <= 0:
                    self.active = True
                if self.delay_before_active == 10:
                    if not (self.world.paused or self.world.main.paused):
                        self.play_sound(self.world.main.sounds.get_sound("sfx/mine/activate.ogg"),0.4)
            else:
                if not self.exploding:
                    for ent in self.collisions:
                        if ent.is_alive() and ("pc" in ent.TYPES or "npc" in ent.TYPES):
                            #test if it's within the mines LOS
                            p1 = (self.pos[0]+0.5, self.pos[1]+0.5)
                            p2 = (ent.pos[0]+0.5, ent.pos[1]+0.5)
                            target_length = math.sqrt((p2[0]-p1[0])**2+(p2[1]-p1[1])**2)

                            ray = Hull(self.world,p1,p2,(0,0))
                            ray.end_pos = p1
                            ray.test_can_extend()

                            while ray.can_extend:
                                ray.extend()

                                length = math.sqrt((ray.start_pos[0]-ray.end_pos[0])**2+(ray.start_pos[1]-ray.end_pos[1])**2)
                                if length >= target_length:
                                    self.exploding = True
                                    if not (self.world.paused or self.world.main.paused):
                                        self.play_sound(self.world.main.sounds.get_sound("sfx/mine/detect.ogg"),0.4)
                                    break
                            if self.exploding:
                                break
                else:
                    self.delay_before_explode -= 1
                    if self.delay_before_explode <= 0:
                        self.explode()

    def explode(self, force = (0,0)):
        if self.alive:
            self.alive = False
            for ent in self.collisions:
                if ent.is_alive() and ("pc" in ent.TYPES or "npc" in ent.TYPES or "mine" in ent.TYPES):
                    dif = ((ent.pos[0]-self.pos[0]),(ent.pos[1]-self.pos[1]))
                    dist = math.sqrt(dif[0]**2+dif[1]**2)

                    if ("mine" in ent.TYPES and dist < self.range) or not "mine" in ent.TYPES:
                        if dist == 0:
                            ent.explode()
                        else:
                            #test if it's within the mines LOS
                            p1 = (self.pos[0]+0.5, self.pos[1]+0.5)
                            p2 = (ent.pos[0]+0.5, ent.pos[1]+0.5)
                            dif = ((p2[0]-p1[0]),(p2[1]-p1[1]))
                            target_length = math.sqrt((p2[0]-p1[0])**2+(p2[1]-p1[1])**2)

                            ray = Hull(self.world,p1,p2,(0,0))
                            ray.end_pos = p1
                            ray.test_can_extend()

                            while ray.can_extend:
                                ray.extend()

                                length = math.sqrt((ray.start_pos[0]-ray.end_pos[0])**2+(ray.start_pos[1]-ray.end_pos[1])**2)
                                if length >= target_length:
                                    force = 2
                                    f = (force*dif[0]/float(length),force*dif[1]/float(length))
                                    ent.explode(f)
                                    break

            self.world.shake_amount = max(self.world.shake_amount,int(self.world.max_shake*0.25))

            if not (self.world.paused or self.world.main.paused):
                self.play_sound(self.world.main.sounds.get_sound("sfx/explosions/mine.ogg"),1.0)

            pos = (self.pos[0]+0.5,self.pos[1]+0.5)

            rects = SuperRect((self.pos[0]+(self.size[0]*0.5)+0.25,
                              self.pos[1]+(self.size[1]*0.5)+0.25,
                              self.size[0],
                              self.size[1])).quad_split()
            i = 0
            for R in rects:
                ang = math.radians(random.randint(-45,45)+(i*90))
                mass = 10

                velocity = (math.cos(ang),math.sin(ang))
                speed = lerp(0.25,1,random.random())

                restitution = 0.3
                gib = Gib(self.world, R.center, R.size, mass, velocity, speed, restitution)
                gib.color = lerp_lists((0,0,0),self.color,0.5)
                gib.alpha = 127
                gib.life = int(60*0.25)
                gib.max_life = int(gib.life)
                gib.render_above = False
                self.world.gibs.append(gib)

                i += 1
            """
            for x in xrange(random.randint(2,4)):
                size = (0.1,0.1)

                ang = math.radians(random.randint(0,360))
                mass = 4

                velocity = (math.cos(ang),math.sin(ang))
                speed = 0.25*random.random()*random.random()

                restitution = 0.9
                gib = Spark(self.world, pos, size, mass, velocity, speed, restitution)
                gib.life = 60*lerp(2,4,random.random())
                gib.max_life = int(gib.life)
                gib.render_above = False
                self.world.main.gibs.append(gib)
            """
            for x in xrange(10):
                size = None

                ang = math.radians(random.randint(-45,45)+(x*90))
                mass = 3

                velocity = (math.cos(ang),math.sin(ang))
                speed = lerp(0.2,0.6,random.random())

                restitution = 1.0
                gib = Flame(self.world, pos, size, mass, velocity, speed, restitution)
                gib.alpha = 127
                gib.health = 60*lerp(0.2,0.4,random.random())
                gib.max_health = int(gib.health)

                self.world.gibs.append(gib)
            self.cleanup()

    def cleanup(self):
        pass
        #del self.explode_sound
        #del self.activate_sound

    def get_collision_rect(self):
        if self.collision_rect_needs_updating:
            self.collision_rect = SuperRect( (self.pos[0]-self.range+0.5,self.pos[1]-self.range+0.5,self.range*2,self.range*2) )
            self.collision_rect_needs_updating = False
        return self.collision_rect

    def prerender(self):
        if self.alive:
            render_pos = [(self.world.pos[0]+((self.pos[0]+0.5)*self.world.scale)),(self.world.pos[1]+((self.pos[1]+0.5)*self.world.scale))]
            #blast radius
            size = ((self.range*2) * self.world.scale)

            rays = self.world.do_lighting_algorithm((self.pos[0]+0.5,self.pos[1]+0.5),self.range)
            points = []
            for r in rays:
                point = ( (r.end_pos[0])*self.world.scale,
                          (r.end_pos[1])*self.world.scale)
                points.append(point)
            pygame.draw.polygon(self.world.prerender_surface, list(self.color)+[64], points)

    def prerender_outline(self):
        if self.alive:
            render_pos = [(self.world.pos[0]+((self.pos[0]+0.5)*self.world.scale)),(self.world.pos[1]+((self.pos[1]+0.5)*self.world.scale))]
            #blast radius
            size = ((self.range*2) * self.world.scale)

            rays = self.world.do_lighting_algorithm((self.pos[0]+0.5,self.pos[1]+0.5),self.range)
            points = []
            for r in rays:
                point = ( (r.end_pos[0])*self.world.scale,
                          (r.end_pos[1])*self.world.scale)
                points.append(point)
            pygame.draw.polygon(self.world.prerender_surface, list(self.color)+[127], points, 1)

    def render(self):
        if self.alive:
            render_pos = [(self.world.pos[0]+((self.pos[0]+0.5)*self.world.scale)),(self.world.pos[1]+((self.pos[1]+0.5)*self.world.scale))]
            pos = [int(render_pos[0]),int(render_pos[1])]

            radius = max(int(  (self.world.scale * 0.5) * 0.3 ),1)
            eye_radius = max(int(  (self.world.scale * 0.5) * 0.15 ),0.5)

            if self.delay_before_explode == 1:
                radius *= 2
                eye_radius *= 2

            rect = pygame.Rect((pos[0]-radius,pos[1]-radius,radius*2,radius*2))

            draw_rect_shadow(self.world.main.screen, rect, int(max(self.world.scale*0.01,1)), 64)

            pygame.draw.rect(self.world.main.screen, lerp_lists((0,0,0),self.color,0.5), rect)

            if self.exploding:
                if self.world.framenumber%4 <= 1:
                    color = (255,255,0)
                else:
                    color = (96,64,64)
            elif self.active:
                color = (255,0,0)
            else:
                color = (96,64,64)
            pygame.draw.rect(self.world.main.screen, color, (pos[0]-eye_radius,pos[1]-eye_radius,eye_radius*2,eye_radius*2))



