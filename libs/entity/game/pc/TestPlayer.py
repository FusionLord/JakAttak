import pygame
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from libs.entity.Entity import*
from libs.common import*

from libs.TimeMachine.PickledEntity import*
from libs.TimeMachine.TimeValue import*
from libs.TimeMachine.TimeValuePattern.patterns.TimeValuePattern_SawIncrement import*
from libs.TimeMachine.TimeValuePattern.patterns.TimeValuePattern_VectorIncrement import*
from libs.TimeMachine.TimeValuePattern.patterns.TimeValuePattern_VectorSquareIncrement import*
from libs.entity.game.particles.Gib import*
from libs.viseffect import*
from libs.entity.game.particles.FleshChunk import*
from libs.common import*

import random
import math

class TestPlayer(Entity):
    TYPES = ("pc","player","testplayer")
    SIZE = (0.45,0.45)
    COLLISION_FILTER = tuple(["jak"])

    def init(self):
        self.prev_pos = tuple(self.pos)

        self.noclip = False

        self.speed = 0.05

        self.color = (255,127,0)

        self.set_id()

    def pickle(self):
        pickle = PickledEntity(int(self.ID), self.world.framenumber, type(self))
        pickle.update_value("alive",TimeValue(bool(self.alive), self.world.framenumber))
        pickle.update_value("health",TimeValue(float(self.health), self.world.framenumber))

        dif = (self.pos[0]-self.prev_pos[0],self.pos[1]-self.prev_pos[1])
        if dif[0] != 0 or dif[1] != 0:
            pickle.update_value("pos",
                                TimeValue(tuple(self.pos),
                                          self.world.framenumber,
                                          TimeValuePattern_VectorIncrement(dif,1)))
        else:
            pickle.update_value("pos",TimeValue(tuple(self.pos),self.world.framenumber))

        pickle.update_value("speed",TimeValue(float(self.speed),self.world.framenumber))
        pickle.update_value("size",TimeValue(tuple(self.size),self.world.framenumber))
        pickle.update_value("color",TimeValue(tuple(self.color), self.world.framenumber))
        pickle.update_value("noclip",TimeValue(bool(self.noclip), self.world.framenumber))
        return pickle

    def unpickle(self, world, pickledentity):
        pos = pickledentity.tracks["pos"][0].get_value_at(None)
        size = pickledentity.tracks["size"][0].get_value_at(None)

        self.__init__(world,pos,size)

        self.ID = pickledentity.ID

        self.alive = pickledentity.tracks["alive"][0].get_value_at(None)
        self.health = pickledentity.tracks["health"][0].get_value_at(None)
        self.speed = pickledentity.tracks["speed"][0].get_value_at(None)
        self.pos = pos
        self.color = pickledentity.tracks["color"][0].get_value_at(None)
        self.noclip = pickledentity.tracks["noclip"][0].get_value_at(None)

    def update(self):
        if self.is_alive():
            if len(self.collisions) > 0:
                self.explode()

            for event in self.world.main.events:
                if event.type == KEYDOWN:
                    if event.key == K_v:
                        self.noclip = not self.noclip

    def move(self):
        if self.is_alive():
            self.prev_pos = tuple(self.pos)

            offset = [0,0]

            if not self.world.paused and not self.world.main.paused:
                if self.world.main.keys[K_LEFT]:
                    offset[0] -= self.speed
                if self.world.main.keys[K_RIGHT]:
                    offset[0] += self.speed
                if self.world.main.keys[K_UP]:
                    offset[1] -= self.speed
                if self.world.main.keys[K_DOWN]:
                    offset[1] += self.speed

            start = (self.pos[0]+0.5,self.pos[1]+0.5)
            end = (start[0]+offset[0],start[1]+offset[1])

            if not self.noclip:
                remaining_distance = math.sqrt((end[0]-start[0])**2+(end[1]-start[1])**2)

                if end[0] != start[0] or end[1] != start[1]:
                    ray = Hull(self.world, start, end, self.size)
                    ray.end_pos = start
                    ray.test_can_extend()

                    while not (end[0] == start[0] and end[1] == start[1]) and not (offset[0] == 0 and offset[1] == 0) and remaining_distance > 0:
                        dist = math.sqrt((ray.end_pos[0]-ray.start_pos[0])**2+(ray.end_pos[1]-ray.start_pos[1])**2)
                        if dist > remaining_distance:
                            #we've hit the limit, no need to continue
                            break
                        else:
                            #checks if ray is even inside of the grid
                            if ray.end_pos[0] < 0 or ray.end_pos[1] < 0 or ray.end_pos[0] > self.world.grid_size[0] or ray.end_pos[1] > self.world.grid_size[1]:
                                pass
                            else:
                                if not ray.can_extend:
                                    remaining_distance -= dist
                                    if ray.impact_horiz:
                                        offset[1] = 0
                                        end = (end[0],ray.end_pos[1])
                                    if ray.impact_verti:
                                        offset[0] = 0
                                        end = (ray.end_pos[0],end[1])
                                    start = ray.end_pos
                                    ray = Hull(self.world, start, end, self.size)
                                    ray.end_pos = start
                                    ray.test_can_extend()
                        if not (end[0] == start[0] and end[1] == start[1]) and not (offset[0]==0 and offset[1] == 0):
                            ray.extend()

            end = (end[0]-0.5,end[1]-0.5)
            if end[0] != self.pos[0] or end[1] != self.pos[1]:
                self.pos = tuple(end)
                self.collision_rect_needs_updating = True
        self.collisions = []

    def get_collision_rect(self):
        if self.collision_rect_needs_updating:
            self.collision_rect = SuperRect( (self.pos[0]-(self.size[0]/2.0)+0.5,self.pos[1]-(self.size[1]/2.0)+0.5,self.size[0],self.size[1]) )
            self.collision_rect_needs_updating = False
        return self.collision_rect

    def explode(self, force = [0,0]):
        if self.is_alive():
            self.alive = False
            self.cleanup()

            rects = [SuperRect((self.pos[0]+0.25,
                              self.pos[1]+0.25,
                              self.size[0],
                              self.size[1]))]

            i = 0
            while i < len(rects):
                R = rects.pop(i)
                rl = R.quad_split()
                rects = rl + rects
                i += 4

            i = 0
            while i < len(rects):
                R = rects.pop(i)
                rl = R.quad_split()
                rects = rl + rects
                i += 4


            for R in rects:
                pos = R.center
                size = R.size
                ang = math.radians(self.world.random.randint(-45,45)+(90*i))
                mass = 10
                velocity = (math.cos(ang),math.sin(ang))
                speed = 0.5*self.world.random.rand()
                v = (velocity[0]*speed+(force[0]/float(mass)),
                        velocity[1]*speed+(force[1]/float(mass)))
                speed = math.sqrt(v[0]**2+v[1]**2)
                velocity = [v[0]/speed, v[1]/speed]
                restitution = 0.5

                gib = FleshChunk(self.world, pos, size, mass, velocity, speed, restitution)
                gib.health = int(60*5)
                gib.max_health = int(gib.health)
                gib.color = self.color
                gib.start_frame -= 1
                gib.render_above = True
                self.world.gibs.append(gib)

                i += 1

    def kill(self, force = [0,0]):
        if self.is_alive():
            self.alive = False
            self.cleanup()

            pos = [(self.pos[0]-self.world.pos[0])/float(self.world.scale),
                   (self.pos[1]-self.world.pos[1])/float(self.world.scale)]
            size = self.size
            ang = math.radians(self.world.random.randint(0,360))
            mass = 6

            velocity = (math.cos(ang),math.sin(ang))
            speed = 0.1*self.world.random.rand()

            v = (velocity[0]*speed+(force[0]/float(mass)),
                    velocity[1]*speed+(force[1]/float(mass)))

            speed = math.sqrt(v[0]**2+v[1]**2)
            velocity = [v[0]/speed, v[1]/speed]

            restitution = 0.2

            gib = Gib(self.world, pos, size, mass, velocity, speed, restitution)
            gib.color = lerp_lists((64,64,64),self.color,0.5)
            gib.alpha = 127
            gib.update()
            gib.move()
            gib.render_above = False
            self.world.gibs.append(gib)

    def cleanup(self):
        pass
        #del self.hit_sound
        #del self.death_sound

    def render(self):
        if self.alive:
            pos = (int((self.pos[0]+0.5)*self.world.scale)+self.world.pos[0],
                   int((self.pos[1]+0.5)*self.world.scale)+self.world.pos[1])
            radius = (max(self.size)*self.world.scale*0.5)

            s = pygame.Surface((radius*2,radius*2))
            s.fill(self.color)
            rect = s.get_rect(center = pos)

            draw_rect_shadow(self.world.main.screen, rect, int(max(self.world.scale*0.025,1)), 64)

            if not self.noclip:
                s.fill(self.color)
            else:
                pygame.draw.rect(s, self.color, (0,0,radius*2,radius*2), 1)

            self.world.main.screen.blit(s,rect)

