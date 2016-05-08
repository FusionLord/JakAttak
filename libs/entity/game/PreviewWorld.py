import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

##################################

import pygame
from pygame.locals import *

##################################

from libs.entity.Entity import *
from libs.common import *
from libs.locals import *

##################################
class PreviewWorld(object):
    TYPES = []

    def __init__(self, main, world, snapshot):
        self.main = main
        self.world = world

        self.pos = tuple(self.world.pos)
        self.scale = float(world.scale)

        self.is_preview = True
        self.framenumber = long(self.world.framenumber)
        self.paused = True

        self.reset()

        self.set_world_with_snapshot(snapshot)

    def reset(self):
        self.ID = self.world.ID

        self.characters = []
        self.entities = []
        self.gibs = []

    def unpickle(self, pickledentity):
        self.framenumber = pickledentity.tracks["framenumber"][0].get_value_at(None)
        self.ID = pickledentity.ID

    def set_world_with_snapshot(self, snapshot):
        self.unpickle(snapshot[str(self.ID)])
        for key in snapshot:
            pickle = snapshot[key]
            if "npc" in pickle.type.TYPES or "pc" in pickle.type.TYPES:
                self.characters.append(pickle.type(self, pickle_data = pickle))
            elif "entity" in pickle.type.TYPES:
                self.entities.append(pickle.type(self, pickle_data = pickle))
            elif "gib" in pickle.type.TYPES:
                self.gibs.append(pickle.type(self, pickle_data = pickle))
            else:
                #print "Unknown type: "+str(type(pickle.type))
                pass

    def render(self):
        self.main.screen.blit(self.world.surface, self.pos)

        #tiles
        for row in self.world.grid:
            for tile in row:
                tile.render()

        #h walls
        for row in self.world.h_walls:
            for wall in row:
                wall.render()

        #v walls
        for row in self.world.v_walls:
            for wall in row:
                wall.render()

        for g in self.gibs:
            if not g.render_above:
                g.render()
        for e in self.entities:
            if not e.render_above:
                e.render()

        for n in self.characters:
            n.render()

        for e in self.entities:
            if e.render_above:
                e.render()
        for g in self.gibs:
            if g.render_above:
                g.render()