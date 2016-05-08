import os
import random
import math

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

import pygame
from pygame.locals import*

from libs import raytrace
from libs.TimeMachine.PickledEntity import PickledEntity
from libs.TimeMachine.TimeValue import TimeValue
from libs.TimeMachine.TimeValuePattern.patterns.TimeValuePattern_Increment import*
from libs.entity.game.particles.Flame import Flame
from libs.entity.game.particles.Gib import Gib
from libs.viseffect import*

from libs.entity.Entity import*
from libs.common import*
from libs.locals import*

class Turret(Entity):
    TYPES = ("entity","turret")
    SIZE = (1,1)
    COLLISION_FILTER = tuple(["jak"])

    def init(self):
        self.render_above = False

        self.color = (192,127,64)

        self.range = 1.5

        self.shot_delay = 0
        self.delay_between_shots = 10

        self.fire_sound = self.world.main.sounds.get_sound("sfx/turret/fire.ogg")

        self.set_id()

    def pickle(self):
        pickle = PickledEntity(int(self.ID), self.world.framenumber, type(self))
        pickle.update_value("alive",TimeValue(bool(self.alive), self.world.framenumber))
        pickle.update_value("health",TimeValue(float(self.health), self.world.framenumber))
        pickle.update_value("pos",TimeValue(tuple(self.pos), self.world.framenumber))
        pickle.update_value("size",TimeValue(tuple(self.size),self.world.framenumber))
        pickle.update_value("range",TimeValue(float(self.range),self.world.framenumber))
        if self.shot_delay>0:
            pickle.update_value("shot_delay",TimeValue(int(self.shot_delay),
                                                       self.world.framenumber,
                                                       TimeValuePattern_Increment(-1)))
        else:
            pickle.update_value("shot_delay",TimeValue(int(self.shot_delay),self.world.framenumber))
        pickle.update_value("delay_between_shots",TimeValue(int(self.delay_between_shots),self.world.framenumber))

        return pickle

    def unpickle(self, world, pickledentity):
        pos = pickledentity.tracks["pos"][0].get_value_at(None)
        size = pickledentity.tracks["size"][0].get_value_at(None)

        self.__init__(world,pos,size)

        self.ID = pickledentity.ID

        self.alive = pickledentity.tracks["alive"][0].get_value_at(None)
        self.health = pickledentity.tracks["health"][0].get_value_at(None)
        self.range = pickledentity.tracks["range"][0].get_value_at(None)
        self.shot_delay = pickledentity.tracks["shot_delay"][0].get_value_at(None)
        self.delay_between_shots = pickledentity.tracks["delay_between_shots"][0].get_value_at(None)
        self.pos = pos

    def get_collision_rect(self):
        if self.collision_rect_needs_updating:
            self.collision_rect = SuperRect( (self.pos[0]-self.range+0.5,self.pos[1]-self.range+0.5,self.range*2,self.range*2) )
            self.collision_rect_needs_updating = False
        return self.collision_rect

    def update(self):
        if self.is_alive():
            target = None

            if self.shot_delay > 0:
                self.shot_delay -= 1
                target = None
            else:
                closest = None
                for ent in self.collisions:
                    if ent.is_alive():
                        #test if it's within the mines LOS
                        p1 = (self.pos[0]+0.5, self.pos[1]+0.5)
                        p2 = (ent.true_pos[0]+0.5, ent.true_pos[1]+0.5)
                        target_length = math.sqrt((p2[0]-p1[0])**2+(p2[1]-p1[1])**2)

                        ray = raytrace.Hull(self.world,p1,p2,(0,0))
                        ray.end_pos = p1
                        ray.test_can_extend()

                        if ray.iterations > 100:
                            print "WARNING: Exceeded max iterations for hull trace!"

                        while ray.can_extend:
                            ray.extend()

                            length = math.sqrt((ray.start_pos[0]-ray.end_pos[0])**2+(ray.start_pos[1]-ray.end_pos[1])**2)
                            if length >= target_length:
                                #target is close enough and is visible
                                if closest == None or target_length < closest[1]:
                                    closest = [ent, target_length]
                                break
                if closest != None:
                    target = closest[0]
                else:
                    target = None

                if target:
                    p1 = (self.pos[0]+0.5, self.pos[1]+0.5)
                    p2 = (target.true_pos[0]+0.5, target.true_pos[1]+0.5)
                    dif = (p2[0]-p1[0],p2[1]-p1[1])
                    length = math.sqrt(dif[0]**2+dif[1]**2)

                    pos = p1

                    size = (0.0,0.0)

                    ang = math.atan2(dif[1],dif[0])
                    mass = 10

                    velocity = (math.cos(ang),math.sin(ang))
                    speed = 1

                    restitution = 0.2

                    if not DEBUG_DISABLE_GIBS:
                        gib = Gib(self.world, pos, size, mass, velocity, speed, restitution)
                        gib.health = int(60*0.1)
                        gib.max_health = int(gib.health)
                        gib.alpha = 64
                        gib.render_above = True
                        gib.die_on_stop_moving = False

                    if length != 0:
                        f = 0.5
                        force = (f*(dif[0]/length),
                                 f*(dif[1]/length))
                        target.hurt(self.world.random.randint(15,25),force)
                    else:
                        target.hurt(self.world.random.randint(15,25))

                    self.shot_delay = int(self.delay_between_shots)

                    if not DEBUG_DISABLE_GIBS:
                        self.world.gibs.append(gib)

                    if not (self.world.paused or self.world.main.paused):
                        self.play_sound(self.fire_sound,0.2)

                    for x in xrange(1):
                        size2 = (0.25,0.25)

                        ang2 = math.radians(random.randint(0,360))
                        mass2 = 4

                        velocity2 = (math.cos(ang2),math.sin(ang2))
                        speed2 = 0.1*random.random()

                        v = (velocity2[0]*speed2+0.25*(velocity[0]*speed),
                                    velocity2[1]*speed2+0.25*(velocity[1]*speed))

                        speed2 = math.sqrt(v[0]**2+v[1]**2)
                        velocity2 = [v[0]/speed2, v[1]/speed2]

                        restitution = 1.0
                        if not DEBUG_DISABLE_GIBS:
                            gib = Flame(self.world, pos, size2, mass2, velocity2, speed2, restitution)
                            gib.health = int(60*lerp(0.05,0.2,random.random()))
                            gib.max_health = int(gib.health)

                            self.world.gibs.append(gib)
            self.collisions = []

    def prerender(self):
        if self.alive:
            render_pos = [(self.world.pos[0]+((self.pos[0]+0.5)*self.world.scale)),(self.world.pos[1]+((self.pos[1]+0.5)*self.world.scale))]
            #fire radius
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
            #fire radius
            size = ((self.range*2) * self.world.scale)

            rays = self.world.do_lighting_algorithm((self.pos[0]+0.5,self.pos[1]+0.5),self.range)
            points = []
            for r in rays:
                point = ( (r.end_pos[0])*self.world.scale,
                          (r.end_pos[1])*self.world.scale)
                points.append(point)
            pygame.draw.polygon(self.world.prerender_surface, list(self.color)+[127], points, 1)

    def render(self):
        if self.is_alive():
            render_pos = [int(self.world.pos[0]+((self.pos[0]+0.5)*self.world.scale)),int(self.world.pos[1]+((self.pos[1]+0.5)*self.world.scale))]
            radius = max(int(  (self.world.scale * 0.5) * 0.4 ),1)
            leg_length = max(int(  (self.world.scale * 0.5) * 0.3 ),1)
            leg_width= max(int(  (self.world.scale * 0.5) * 0.2 ),1)
            pos = (int(render_pos[0]), int(render_pos[1]))

            leg_color = lerp_lists((0,0,0),self.color, 0.75)
            leg_color = [int(leg_color[0]),int(leg_color[1]),int(leg_color[2])]

            rect = pygame.Rect((pos[0]-radius-leg_length,pos[1]-radius+leg_width,leg_length,(radius-leg_width)*2))
            draw_rect_shadow(self.world.main.screen, rect, int(max(self.world.scale*0.01,1)), 64)
            pygame.draw.rect(self.world.main.screen, leg_color, rect)
            rect = pygame.Rect((pos[0]+radius,pos[1]-radius+leg_width,leg_length,(radius-leg_width)*2))
            draw_rect_shadow(self.world.main.screen, rect, int(max(self.world.scale*0.01,1)), 64)
            pygame.draw.rect(self.world.main.screen, leg_color, rect)
            rect = pygame.Rect((pos[0]-radius+leg_width,pos[1]-radius-leg_length,(radius-leg_width)*2,leg_length))
            draw_rect_shadow(self.world.main.screen, rect, int(max(self.world.scale*0.01,1)), 64)
            pygame.draw.rect(self.world.main.screen, leg_color, rect)
            rect = pygame.Rect((pos[0]-radius+leg_width,pos[1]+radius,(radius-leg_width)*2,leg_length))
            draw_rect_shadow(self.world.main.screen, rect, int(max(self.world.scale*0.01,1)), 64)
            pygame.draw.rect(self.world.main.screen, leg_color, rect)

            rect = pygame.Rect((pos[0]-radius,pos[1]-radius,radius*2,radius*2))
            draw_rect_shadow(self.world.main.screen, rect, int(max(self.world.scale*0.025,1)), 64)
            pygame.draw.rect(self.world.main.screen, lerp_lists((255,255,255),self.color, 0.5), rect)

