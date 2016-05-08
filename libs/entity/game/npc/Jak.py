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
from libs.locals import*
from libs.HUD import*

import random
import math

class Jak(Entity):
    TYPES = ("npc","jak")
    SIZE = (0.5,0.5)
    COLLISION_FILTER = tuple(["NONE"])

    def init(self):
        self.true_pos = tuple(self.pos)
        self.facing = 0 #0 is up, 1 is right, 2 is down, 3 is left

        self.target_pos = list(self.pos)
        self.target_facing = int(self.facing)

        self.speed = 20
        self.interp_amount = self.speed - 1

        self.color = HSVtoRGB(random.randint(0,360),random.randint(85,100),random.randint(75,100))

        self.render_pos = None
        self.prev_render_pos = None

        self.rect = self.get_rect()

        self.hit_sound = self.world.main.sounds.get_sound("physics/npc/bump1.wav")
        self.death_sound = self.world.main.sounds.get_sound("npc/jak/death/"+randomChooseFile("data/sounds/npc/jak/death"))

        self.set_id()
        self.update_sprite()

    def pickle(self):
        if self.facing == 0:
            offset = (0,-1)
        elif self.facing == 1:
            offset = (1,0)
        elif self.facing == 2:
            offset = (0,1)
        elif self.facing == 3:
            offset = (-1,0)

        pickle = PickledEntity(int(self.ID), self.world.framenumber, Jak)
        pickle.update_value("alive",TimeValue(bool(self.alive), self.world.framenumber))
        pickle.update_value("health",TimeValue(float(self.health), self.world.framenumber))
        pickle.update_value("pos",
                            TimeValue(tuple(self.pos),
                            self.world.framenumber,
                            TimeValuePattern_VectorSquareIncrement(offset,self.speed)))
        pickle.update_value("size",
                            TimeValue(tuple(self.size),
                            self.world.framenumber))
        pickle.update_value("facing",TimeValue(int(self.facing), self.world.framenumber))
        pickle.update_value("target_pos",
                            TimeValue(tuple(self.target_pos),
                            self.world.framenumber,
                            TimeValuePattern_VectorSquareIncrement(offset,self.speed)))
        pickle.update_value("target_facing",TimeValue(int(self.target_facing), self.world.framenumber))
        pickle.update_value("color",TimeValue(tuple(self.color), self.world.framenumber))
        pickle.update_value("interp_amount",
                            TimeValue(int(self.interp_amount),
                            self.world.framenumber,
                            TimeValuePattern_SawIncrement(0,self.speed)))
        pickle.update_value("speed",
                            TimeValue(int(self.speed),
                            self.world.framenumber))
        return pickle

    def unpickle(self, world, pickledentity):
        pos = pickledentity.tracks["pos"][0].get_value_at(None)
        size = pickledentity.tracks["size"][0].get_value_at(None)

        self.__init__(world,pos,size)

        self.ID = pickledentity.ID

        self.alive = pickledentity.tracks["alive"][0].get_value_at(None)
        self.health = pickledentity.tracks["health"][0].get_value_at(None)
        self.pos = pos
        self.facing = pickledentity.tracks["facing"][0].get_value_at(None)
        self.target_pos = pickledentity.tracks["target_pos"][0].get_value_at(None)
        self.target_facing = pickledentity.tracks["target_facing"][0].get_value_at(None)
        self.color = pickledentity.tracks["color"][0].get_value_at(None)
        self.interp_amount = pickledentity.tracks["interp_amount"][0].get_value_at(None)
        self.speed = pickledentity.tracks["speed"][0].get_value_at(None)

        self.update_true_pos()
        self.update_sprite()

    def get_wall(self,direction):
        F = (self.facing + direction)%4
        if F == 0:
            return self.world.h_walls[self.pos[1]][self.pos[0]]
        elif F == 1:
            return self.world.v_walls[self.pos[1]][self.pos[0]+1]
        elif F == 2:
            return self.world.h_walls[self.pos[1]+1][self.pos[0]]
        elif F == 3:
            return self.world.v_walls[self.pos[1]][self.pos[0]]
        else:
            raise TypeError("Error! 'Facing' isn't legal value!")

    def prep_move(self,direction):
        F = (self.facing + direction)%4
        if F == 0:
            self.target_pos = (self.pos[0],self.pos[1]-1)
        elif F == 1:
            self.target_pos = (self.pos[0]+1,self.pos[1])
        elif F == 2:
            self.target_pos = (self.pos[0],self.pos[1]+1)
        elif F == 3:
            self.target_pos = (self.pos[0]-1,self.pos[1])
        else:
            raise TypeError("Error! 'Facing' isn't legal value!")
        self.target_facing = F

    def update(self):
        if self.is_alive():
            self.interp_amount += 1

            if self.interp_amount >= self.speed or self.target_pos == self.pos:
                self.interp_amount = 0
                self.pos = self.target_pos

                if self.pos[0] < 0 or self.pos[0] > self.world.grid_size[0]-1 or self.pos[1] < 0 or self.pos[1] > self.world.grid_size[1]-1:
                    #it's glitched out outside of the world
                    self.kill()
                else:
                    wall_in_front = self.get_wall(0)

                    if wall_in_front.is_solid:
                        wall_to_left = self.get_wall(-1)
                        wall_to_right = self.get_wall(1)

                        if not wall_to_left.is_solid and not wall_to_right.is_solid:
                            pick = self.world.random.choice(("L","R"))
                        else:
                            wall_behind = self.get_wall(2)
                            if not wall_behind.is_solid:
                                if wall_to_left.is_solid and wall_to_right.is_solid:
                                    pick = "B"
                                else:
                                    if self.world.random.randint(1,3) == 1:
                                        pick = "B"
                                    else:
                                        if not wall_to_left.is_solid:
                                            pick = "L"
                                        else:
                                            pick = "R"
                            else:
                                if not wall_to_left.is_solid:
                                    pick = "L"
                                elif not wall_to_right.is_solid:
                                    pick = "R"
                                else:
                                    #can't do SHIT
                                    return

                        if pick == "L":
                            self.prep_move(-1)
                        elif pick == "R":
                            self.prep_move(1)
                        elif pick == "B":
                            self.prep_move(2)
                        else:
                            return
                        if not self.world.paused:
                            self.play_sound(self.hit_sound, 0.025)
                    else:
                        self.prep_move(0)

    def move(self):
        if self.is_alive():
            if self.interp_amount == 0:
                self.facing = int(self.target_facing)

            self.update_true_pos()

            self.rect = self.get_rect()
            self.collision_rect_needs_updating = True

        self.collisions = []

    def update_true_pos(self):
        self.true_pos = tuple(lerp_lists(self.pos, self.target_pos, self.interp_amount/float(self.speed)))
        self.true_pos = (int(self.true_pos[0]*100)/100.0,int(self.true_pos[1]*100)/100.0)

    def get_rect(self):
        t = self.interp_amount
        p = min(t/float(self.speed),1)

        grid_pos = (lerp(self.pos[0],self.target_pos[0],p),
                    lerp(self.pos[1],self.target_pos[1],p))

        pos = (int((grid_pos[0]+0.5)*self.world.scale + self.world.pos[0]), int((grid_pos[1]+0.5)*self.world.scale + self.world.pos[1]))

        return pygame.Rect((pos[0]-(self.size[0]*self.world.scale/2),
                            pos[1]-(self.size[1]*self.world.scale/2),
                            self.size[0]*self.world.scale,
                            self.size[1]*self.world.scale))

    def get_collision_rect(self):
        if self.collision_rect_needs_updating:
            self.collision_rect = SuperRect( (self.true_pos[0]-(self.size[0]/2.0)+0.5,self.true_pos[1]-(self.size[1]/2.0)+0.5,self.size[0],self.size[1]) )
            self.collision_rect_needs_updating = False
        return self.collision_rect

    def hurt(self, amount, force = [0,0]):
        self.health -= amount
        if self.health <= 0:
            self.kill(force)
        else:
            r = self.get_rect()
            if self.facing == 0:
                offset = (0,-1)
            elif self.facing == 1:
                offset = (1,0)
            elif self.facing == 2:
                offset = (0,1)
            elif self.facing == 3:
                offset = (-1,0)
            for x in xrange(1):
                pos = [(r.center[0]-self.world.pos[0])/float(self.world.scale),
                       (r.center[1]-self.world.pos[1])/float(self.world.scale)]
                size = (self.size[0]*0.25,self.size[1]*0.25)
                ang = math.radians(self.world.random.randint(0,360))
                mass = 2

                velocity = (math.cos(ang),math.sin(ang))
                speed = 0.025*self.world.random.rand()

                v = (velocity[0]*speed+offset[0]*(1.0/self.speed)+(force[0]/float(mass)),
                        velocity[1]*speed+offset[1]*(1.0/self.speed)+(force[1]/float(mass)))

                speed = math.sqrt(v[0]**2+v[1]**2)
                velocity = [v[0]/speed, v[1]/speed]

                restitution = 0.2

                if not DEBUG_DISABLE_GIBS:
                    gib = Gib(self.world, pos, size, mass, velocity, speed, restitution)
                    gib.color = lerp_lists((64,64,64),self.color,0.5)
                    gib.alpha = 127
                    gib.health = int(60*0.25)
                    gib.max_health = int(gib.health)
                    gib.update()
                    gib.move()
                    gib.render_above = False
                    self.world.gibs.append(gib)

            self.update_sprite()

    def explode(self, force = [0,0]):
        if self.is_alive():
            self.alive = False

            if not (self.world.paused or self.world.main.paused):
                self.play_sound(self.death_sound,0.1)

            r = self.get_rect()
            if self.facing == 0:
                offset = (0,-1)
            elif self.facing == 1:
                offset = (1,0)
            elif self.facing == 2:
                offset = (0,1)
            elif self.facing == 3:
                offset = (-1,0)

            rects = SuperRect((self.true_pos[0]+(self.size[0]*0.5),
                              self.true_pos[1]+(self.size[1]*0.5),
                              self.size[0],
                              self.size[1])).quad_split()
            i = 0
            for R in rects:
                pos = R.center
                size = R.size
                ang = math.radians(self.world.random.randint(-45,45)+(90*i))
                mass = 6
                velocity = (math.cos(ang),math.sin(ang))
                speed = 0.2*self.world.random.rand()
                v = (velocity[0]*speed+offset[0]*(1.0/self.speed)+(force[0]/float(mass)),
                        velocity[1]*speed+offset[1]*(1.0/self.speed)+(force[1]/float(mass)))
                speed = math.sqrt(v[0]**2+v[1]**2)
                velocity = [v[0]/speed, v[1]/speed]
                restitution = 0.2

                if not DEBUG_DISABLE_GIBS:
                    gib = FleshChunk(self.world, pos, size, mass, velocity, speed, restitution)
                    gib.color = lerp_lists((127,127,127),self.color,max(min(self.health/100.0,1),0))
                    gib.update()
                    gib.move()
                    gib.update()
                    gib.move()
                    gib.render_above = False
                    self.world.gibs.append(gib)

                i += 1

            pos = (self.true_pos[0]+0.5,self.true_pos[1]+0.5)
            radius = max(self.size) * 0.5
            eye_radius = max(self.size) * 0.25

            if self.facing == 0:
                eye = (pos[0], pos[1]-radius+eye_radius)
            elif self.facing == 1:
                eye = (pos[0]+radius-eye_radius, pos[1])
            elif self.facing == 2:
                eye = (pos[0], pos[1]+radius-eye_radius)
            elif self.facing == 3:
                eye = (pos[0]-radius+eye_radius, pos[1])
            else:
                raise TypeError("Error! Can't render this illegal facing!")

            pos = eye
            size = (eye_radius*2,eye_radius*2)
            ang = math.radians(self.world.random.randint(0,360))
            mass = 6
            velocity = (math.cos(ang),math.sin(ang))
            speed = 0.1*self.world.random.rand()
            v = (velocity[0]*speed+offset[0]*(1.0/self.speed)+(force[0]/float(mass)),
                    velocity[1]*speed+offset[1]*(1.0/self.speed)+(force[1]/float(mass)))
            speed = math.sqrt(v[0]**2+v[1]**2)
            velocity = [v[0]/speed, v[1]/speed]
            restitution = 0.2

            if not DEBUG_DISABLE_GIBS:
                gib = Gib(self.world, pos, size, mass, velocity, speed, restitution)
                gib.color = (0,0,0)
                gib.health = int(60*0.1)
                gib.max_health = int(gib.health)
                gib.update()
                gib.move()
                gib.update()
                gib.move()
                gib.render_above = False
                self.world.gibs.append(gib)

    def kill(self, force = [0,0]):
        if self.is_alive():
            self.alive = False

            r = self.get_rect()
            if self.facing == 0:
                offset = (0,-1)
            elif self.facing == 1:
                offset = (1,0)
            elif self.facing == 2:
                offset = (0,1)
            elif self.facing == 3:
                offset = (-1,0)
            for x in xrange(1):
                pos = [(r.center[0]-self.world.pos[0])/float(self.world.scale),
                       (r.center[1]-self.world.pos[1])/float(self.world.scale)]
                size = self.size
                ang = math.radians(self.world.random.randint(0,360))
                mass = 6

                velocity = (math.cos(ang),math.sin(ang))
                speed = 0.05*self.world.random.rand()

                v = (velocity[0]*speed+offset[0]*(1.0/self.speed)+(force[0]/float(mass)),
                        velocity[1]*speed+offset[1]*(1.0/self.speed)+(force[1]/float(mass)))

                speed = math.sqrt(v[0]**2+v[1]**2)
                velocity = [v[0]/speed, v[1]/speed]

                restitution = 0.2

                if not DEBUG_DISABLE_GIBS:
                    gib = Gib(self.world, pos, size, mass, velocity, speed, restitution)
                    p = max(min(self.health/100.0,1),0)
                    gib.color = lerp_lists((127,127,127),self.color,p)
                    gib.alpha = lerp(96,192,p)
                    gib.update()
                    gib.move()
                    gib.render_above = False
                    self.world.gibs.append(gib)

            pos = (self.true_pos[0]+0.5,self.true_pos[1]+0.5)
            radius = max(self.size) * 0.5
            eye_radius = max(self.size) * 0.25

            if self.facing == 0:
                eye = (pos[0], pos[1]-radius+eye_radius)
            elif self.facing == 1:
                eye = (pos[0]+radius-eye_radius, pos[1])
            elif self.facing == 2:
                eye = (pos[0], pos[1]+radius-eye_radius)
            elif self.facing == 3:
                eye = (pos[0]-radius+eye_radius, pos[1])
            else:
                raise TypeError("Error! Can't render this illegal facing!")

            pos = eye
            size = (eye_radius*2,eye_radius*2)
            ang = math.radians(self.world.random.randint(0,360))
            mass = 3
            velocity = (math.cos(ang),math.sin(ang))
            speed = 0.025*self.world.random.rand()
            v = (velocity[0]*speed+offset[0]*(1.0/self.speed)+(force[0]/float(mass)),
                    velocity[1]*speed+offset[1]*(1.0/self.speed)+(force[1]/float(mass)))
            speed = math.sqrt(v[0]**2+v[1]**2)
            velocity = [v[0]/speed, v[1]/speed]
            restitution = 0.2

            if not DEBUG_DISABLE_GIBS:
                gib = Gib(self.world, pos, size, mass, velocity, speed, restitution)
                gib.color = (0,0,0)
                gib.health = int(60*0.1)
                gib.max_health = int(gib.health)
                gib.update()
                gib.move()
                gib.update()
                gib.move()
                gib.render_above = False
                self.world.gibs.append(gib)

    def cleanup(self):
        pass
        #del self.hit_sound
        #del self.death_sound

    def update_sprite(self):
        radius = max(int(  (self.world.scale * max(self.size)) * 0.5 ),1)
        eye_radius = max(int(  (self.world.scale * max(self.size)) * 0.25 ),0.5)

        self.sprite = pygame.Surface((radius*2,radius*2),flags=SRCALPHA)

        color = lerp_lists((127,127,127,96),list(self.color)+[192],max(min(self.health/100.0,1),0))

        self.sprite.fill(color)

        pygame.draw.rect(self.sprite, (0,0,0), (radius-eye_radius,0,eye_radius*2,eye_radius*2))

    def render(self):
        if self.alive:
            t = self.interp_amount
            p = min(t/float(self.speed),1)

            grid_pos = (lerp(self.pos[0],self.target_pos[0],p),
                        lerp(self.pos[1],self.target_pos[1],p))
            render_pos = [int(self.world.pos[0]+((grid_pos[0]+0.5)*self.world.scale)),int(self.world.pos[1]+((grid_pos[1]+0.5)*self.world.scale))]

            rect = self.sprite.get_rect(center = render_pos)
            draw_rect_shadow(self.world.main.screen, rect, int(max(self.world.scale*0.025,1)), 64)
            self.world.main.screen.blit(pygame.transform.rotate(self.sprite,-90*(self.facing)), rect)

            if self.world.paused and not self.world.main.paused and not self.world.is_preview:
                font = self.world.main.fonts.get_font(self.world.main.fonts.DEFAULT, 8)
                text = renderText(str(self.speed),font, font, antialias=True)

                rect = text.get_rect(center = render_pos)
                self.world.main.screen.blit(text,rect)
                              

