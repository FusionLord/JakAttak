import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

import pygame

from libs.common import*

##################################

class Entity(object):
    ENTITY_ID = long(0)
    TYPES = tuple(["entity"])
    COLLISION_FILTER = None

    def __init__(self,world,pos=None,size=None,pickle_data=None):
        self.world = world

        self.collision_rect_needs_updating = True
        self.collision_rect = None
        self.collisions = []

        if not pickle_data:
            self.pos = pos
            if not size:
                self.size = type(self).SIZE
            else:
                self.size = size

            self.alive = True
            self.health = 100

            self.render_above = True

            self.init()
        else:
            self.unpickle(world,pickle_data)

    def init(self):
        #this is for child classes
        pass

    def unpickle(self,world,pickle_data):
        raise NotImplementedError("This class can NOT unpickle yet!")

    def pickle(self):
        raise NotImplementedError("This class can't be pickled yet!")

    def set_id(self):
        self.ID = long(Entity.ENTITY_ID)
        Entity.ENTITY_ID = Entity.ENTITY_ID + 1

    def cleanup(self):
        pass

    def play_sound(self, sound, mul, force=False):
        channel = pygame.mixer.find_channel(force)

        if channel:
            pos = max(min(self.pos[0]*self.world.scale + self.world.pos[0],self.world.main.screen_size[0]),0) / float(self.world.main.screen_size[0])
            channel.set_volume((1.0-pos)*mul,(pos)*mul)
            channel.play(sound)

        return channel

    def update_sprite(self):
        #this is called so the entity re-renders it's sprite, due to something changing
        pass

    def get_health(self):
        return float(self.health)

    def set_health(self, amount):
        self.health = amount
        if self.health <= 0:
            self.kill()

    def is_alive(self):
        return self.alive

    def hurt(self, amount, force = [0,0]):
        self.health -= amount
        if self.health <= 0:
            self.kill(force)

    def kill(self, force = [0,0]):
        self.health = 0
        self.alive = False
        self.cleanup()

    def explode(self, force = [0,0]):
        self.kill()

    def get_collision_rect(self):
        if self.collision_rect_needs_updating:
            self.collision_rect = SuperRect( (self.pos[0]-(self.size[0]/2.0)+0.5,self.pos[1]-(self.size[1]/2.0)+0.5,self.size[0],self.size[1]) )
            self.collision_rect_needs_updating = False
        return self.collision_rect

    def update(self):
        pass

    def move(self):
        self.collisions = []

    def prerender(self):
        pass

    def prerender_outline(self):
        pass

    def render(self):
        pass
