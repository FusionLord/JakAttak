import os
import sys
import time
import math
import random

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

##################################

import pygame
from pygame.locals import *

##################################

from libs.TimeMachine.TimeValuePattern.patterns.TimeValuePattern_Increment import *
from libs.entity.game.PreviewWorld import *
from libs.TimeMachine.TimeMachine import *
from libs.entity.game.Wall import *
from libs.entity.game.EmptyWall import *
from libs.entity.game.Door import *
from libs.entity.game.Tile import *
from libs.entity.game.Button import *
from libs.entity.game.EdgeButton import *
from libs.entity.game.EmptyTile import *
from libs.entity.game.npc.Jak import *
from libs.entity.TimeRandom import *
from libs.entity.IdManager import *
from libs.common import *
from libs.locals import *
from libs.viseffect import *
from libs.entity.IdManager import *
from libs.entity.TimeRandom import *
from libs.entity.game.weapon.Mine import *
from libs.entity.game.EmptyTile import *
from libs.entity.game.Button import *
from libs.entity.game.EdgeButton import *
from libs.entity.game.EmptyWall import *
from libs.entity.game.Tile import *
from libs.entity.game.Wall import *
from libs.entity.game.pc.TestPlayer import *
from libs.entity.game.weapon.Turret import *
from libs.entity.game.Spawner import *
from libs.quadtree.Quadtree import *

##################################
class World(object):
    TYPES = tuple(["world"])

    def __init__(self, main):
        self.set_id()

        self.main = main

        self.pos = (0, 0)

        self.grid_size = (0, 0)
        self.scale = GRIDSCALE
        self.grid = []

        self.h_walls = []
        self.v_walls = []

        self.surface = pygame.Surface(
            (int(self.grid_size[0] * self.scale + 1), int(self.grid_size[1] * self.scale + 1)),
            flags=HWSURFACE | SRCALPHA)
        self.prerender_surface = pygame.Surface(
            (int(self.grid_size[0] * self.scale + 1), int(self.grid_size[1] * self.scale + 1)),
            flags=HWSURFACE | SRCALPHA)
        self.last_prerendered_frame = long(-1)
        self.bg_color = HSVtoRGB(0*30,0,25)

        self.group_status = []
        self.next_group_status = []
        for x in xrange(12):
            self.group_status.append(0)
            self.next_group_status.append(0)

        self.is_preview = False

        self.paused = False
        self.step_once = False
        self.framenumber = long(0)
        self.preview_framenumber = long(0)

        self.shake_amount = 0
        self.max_shake = 100

        self.timemachine = TimeMachine()
        self.random = TimeRandom(self, (0, 0), (0, 0))
        self.id_manager = IdManager(self, (0, 0), (0, 0))

        self.debug_data = []

        self.edit_mode = 0
        self.prev_tile_selected = None

        self.rerender()
        self.reset()

    def set_id(self):
        self.ID = int(Entity.ENTITY_ID)
        Entity.ENTITY_ID = Entity.ENTITY_ID + 1

    def reset(self):
        self.quadtree = QuadTree(self, SuperRect((0, 0, self.grid_size[0], self.grid_size[1])), 2, 1)

        self.characters = []
        self.entities = []
        self.gibs = []

    def pickle(self):
        pickle = PickledEntity(int(self.ID), self.framenumber, World)
        pickle.update_value("alive", TimeValue(True, long(self.framenumber)))
        pickle.update_value("framenumber",
                            TimeValue(long(self.framenumber), long(self.framenumber), TimeValuePattern_Increment()))
        pickle.update_value("group_status", TimeValue(tuple(self.group_status), long(self.framenumber)))
        pickle.update_value("next_group_status", TimeValue(tuple(self.next_group_status), long(self.framenumber)))
        return pickle

    def unpickle(self, pickledentity):
        self.framenumber = pickledentity.tracks["framenumber"][0].get_value_at(None)
        self.group_status = list(pickledentity.tracks["group_status"][0].get_value_at(None))
        self.next_group_status = list(pickledentity.tracks["next_group_status"][0].get_value_at(None))
        self.ID = pickledentity.ID

    def cleanup(self):
        pass

    def get_snapshot_at_frame(self, frame):
        snapshot = self.timemachine.get_frame(frame)
        return snapshot

    def set_world_with_snapshot(self, snapshot):
        self.reset()
        self.unpickle(snapshot[str(self.ID)])
        self.random.unpickle(self, snapshot[str(self.random.ID)])
        self.timemachine.clear_everything_after_this_frame(self.framenumber)
        for key in snapshot:
            pickle = snapshot[key]
            if "npc" in pickle.type.TYPES or "pc" in pickle.type.TYPES:
                self.characters.append(pickle.type(self, pickle_data=pickle))
            elif "entity" in pickle.type.TYPES:
                self.entities.append(pickle.type(self, pickle_data=pickle))
            elif "gib" in pickle.type.TYPES:
                self.gibs.append(pickle.type(self, pickle_data=pickle))
            else:
                #print "Unknown type: "+str(type(pickle.type))
                pass
        self.id_manager.unpickle(self, snapshot[str(self.id_manager.ID)])

    def resize(self, new_size):
        new_grid = []
        new_h_walls = []
        new_v_walls = []

        #tiles
        for y in xrange(new_size[1]):
            row = []
            for x in xrange(new_size[0]):
                if x < self.grid_size[0] and y < self.grid_size[1]:
                    row.append(self.grid[y][x])
                else:
                    row.append(EmptyTile(self, (x, y)))
            new_grid.append(row)

        #h walls
        for y in xrange(new_size[1] + 1):
            row = []
            for x in xrange(new_size[0]):
                if x < self.grid_size[0] and y < self.grid_size[1] + 1:
                    row.append(self.h_walls[y][x])
                else:
                    row.append(EmptyWall(self, 0, (x, y)))
            new_h_walls.append(row)

        #v walls
        for y in xrange(new_size[1]):
            row = []
            for x in xrange(new_size[0] + 1):
                if x < self.grid_size[0] + 1 and y < self.grid_size[1]:
                    row.append(self.v_walls[y][x])
                else:
                    row.append(EmptyWall(self, 1, (x, y)))
            new_v_walls.append(row)

        self.grid_size = new_size
        self.grid = new_grid
        self.h_walls = new_h_walls
        self.v_walls = new_v_walls

        self.surface = pygame.Surface(
            (int(self.grid_size[0] * self.scale + 1), int(self.grid_size[1] * self.scale + 1)),
            flags=HWSURFACE | SRCALPHA)
        self.prerender_surface = pygame.Surface(
            (int(self.grid_size[0] * self.scale + 1), int(self.grid_size[1] * self.scale + 1)),
            flags=HWSURFACE | SRCALPHA)
        self.surface.fill((0, 0, 0, 0))
        self.prerender_surface.fill((0, 0, 0, 0))

        self.rerender()

    def resize_to_screen(self):
        self.resize((int(math.ceil((self.main.screen_size[0] / float(self.scale)))),
                     int(math.ceil(self.main.screen_size[1] / float(self.scale)))))

        self.rerender()

    def close_grid(self):
        for y in xrange(self.grid_size[1]):
            for x in xrange(self.grid_size[0]):
                if type(self.grid[y][x]) != EmptyTile:
                    #check left tile
                    if x - 1 < 0 or type(self.grid[y][x - 1]) == EmptyTile:
                        self.v_walls[y][x] = Wall(self, 1, (x, y))
                        #check right tile
                    if x + 1 > self.grid_size[0] - 1 or type(self.grid[y][x + 1]) == EmptyTile:
                        self.v_walls[y][x + 1] = Wall(self, 1, (x, y))
                        #check top tile
                    if y - 1 < 0 or type(self.grid[y - 1][x]) == EmptyTile:
                        self.h_walls[y][x] = Wall(self, 0, (x, y))
                        #check bottom tile
                    if y + 1 > self.grid_size[1] - 1 or type(self.grid[y + 1][x]) == EmptyTile:
                        self.h_walls[y + 1][x] = Wall(self, 0, (x, y))

        self.rerender()

    def do_lighting_algorithm(self, pos, max_length=None):
        test_rays = []

        start_pos = pos
        if max_length:
            number_of_rays_per_side = int(6*max_length)
        else:
            number_of_rays_per_side = 16#12
        directions = []

        for i in xrange(4):
            c1 = (int(i == 0 or i == 3) * 2 - 1, int(i >= 2) * 2 - 1)
            c2 = (int((i + 1) % 4 == 0 or (i + 1) % 4 == 3) * 2 - 1, int((i + 1) % 4 >= 2) * 2 - 1)
            #print i, c1, c2
            for i2 in xrange(number_of_rays_per_side):
                p = i2 / float(number_of_rays_per_side)
                directions.append(lerp_lists(c1, c2, p))

        """
		for x in xrange(360/4):
			a=x*4
			directions.append(Vector(cos(a), sin(a)))
		"""
        for d in directions:
            end = (start_pos[0]+d[0]/2, start_pos[1]+d[1]/2)
            test_rays.append(raytrace.Hull(self, start_pos, end, (0,0), self.paused or self.main.paused))
            test_rays[-1].end_pos = start_pos
            test_rays[-1].test_can_extend()

        #d = directions[0]
        #self.test_rays.append(RT_ray(self.grid, start_pos, start_pos+(d/2)))
        #self.test_rays[-1].fit_to_grid()

        rays = list(test_rays)

        length = len(rays)
        while length != 0:
            i = length - 1
            while i >= 0:
                if abs(rays[i].normalized[0]) <= abs(rays[i].normalized[1]):
                    dif = abs(rays[i].end_pos[1]-rays[i].start_pos[1])
                else:
                    dif = abs(rays[i].end_pos[0]-rays[i].start_pos[0])

                if not rays[i].can_extend or (max_length and dif >= max_length):
                    if max_length and dif >= max_length:
                        if abs(rays[i].normalized[0]) <= abs(rays[i].normalized[1]):
                            if rays[i].normalized[1] > 0:
                                y = rays[i].start_pos[1]+float(max_length)
                            else:
                                y = rays[i].start_pos[1]-float(max_length)
                            if rays[i].normalized[1] > 0:
                                x = rays[i].start_pos[0]+(rays[i].normalized[0]*(y-rays[i].start_pos[1]))/abs(rays[i].normalized[1])
                            else:
                                x = rays[i].start_pos[0]+(rays[i].normalized[0]*(rays[i].start_pos[1]-y))/abs(rays[i].normalized[1])
                        else:
                            if rays[i].normalized[0] > 0:
                                x = rays[i].start_pos[0]+float(max_length)
                            else:
                                x = rays[i].start_pos[0]-float(max_length)
                            if rays[i].normalized[0] > 0:
                                y = rays[i].start_pos[1]+(rays[i].normalized[1]*(x-rays[i].start_pos[0]))/abs(rays[i].normalized[0])
                            else:
                                y = rays[i].start_pos[1]+(rays[i].normalized[1]*(rays[i].start_pos[0]-x))/abs(rays[i].normalized[0])

                        rays[i].end_pos = (x,y)

                    rays.pop(i)
                else:
                    rays[i].extend()
                i -= 1
            length = len(rays)

        #self.prune_ray_list(self.test_rays)
        return test_rays

    def update(self):
        if not self.main.paused:
            if self.step_once:
                self.step_once = False

            for event in self.main.events:
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        if self.paused and long(self.preview_framenumber) < self.framenumber:
                            self.set_world_with_snapshot(self.get_snapshot_at_frame(long(self.preview_framenumber)))
                            self.framenumber = long(self.preview_framenumber)
                        else:
                            self.paused = not self.paused

                            if self.paused:
                                self.scrub_preview = PreviewWorld(self.main, self,
                                                                  self.get_snapshot_at_frame(self.framenumber))
                                self.preview_framenumber = long(self.framenumber)
                            else:
                                if long(self.preview_framenumber) == self.framenumber:
                                    pass
                                else:
                                    self.set_world_with_snapshot(
                                        self.get_snapshot_at_frame(long(self.preview_framenumber)))
                    elif event.key == K_TAB:
                        if self.paused and self.framenumber != 0:
                            if long(self.preview_framenumber) == self.framenumber:
                                self.preview_framenumber = long(self.framenumber - 1)
                                mid = (self.main.screen_size[0] / 2, self.main.screen_size[1] / 2)
                                self.main.mouse_pos = mid
                                pygame.mouse.set_pos(mid)
                            else:
                                self.preview_framenumber = long(self.framenumber)
                            self.scrub_preview = PreviewWorld(self.main, self, self.get_snapshot_at_frame(
                                long(self.preview_framenumber)))
                    elif event.key == K_RIGHT:
                        if self.paused and long(self.preview_framenumber) == self.framenumber:
                            self.step_once = True
                            self.debug_data = []
                    elif event.key == K_ESCAPE:
                        self.main.paused = True

            if self.paused and long(self.preview_framenumber) < self.framenumber:
                mid = (self.main.screen_size[0] / 2, self.main.screen_size[1] / 2)
                dif = (self.main.mouse_pos[0] - mid[0], self.main.mouse_pos[1] - mid[1])
                pygame.mouse.set_pos(mid)
                self.main.mouse_pos = mid

                dif = dif[0] / 4.0

                if self.main.keys[K_LCTRL] or self.main.keys[K_RCTRL]:
                    rate = 16
                else:
                    rate = 4

                if self.main.keys[K_RIGHT]:
                    dif += rate
                elif self.main.keys[K_LEFT]:
                    dif -= rate

                for event in self.main.events:
                    if event.type == MOUSEBUTTONDOWN and (event.button == 4 or event.button == 5):
                        if event.button == 4:
                            dif += 1
                        else:
                            dif -= 1

                preview_framenumber = max(min(long(self.preview_framenumber) + dif, self.framenumber - 1), 0)

                if long(preview_framenumber) != long(self.preview_framenumber):
                    if long(preview_framenumber) != self.framenumber:
                        self.scrub_preview = PreviewWorld(self.main, self,
                                                          self.get_snapshot_at_frame(long(preview_framenumber)))
                self.preview_framenumber = long(preview_framenumber)

            if (not self.paused or self.step_once) and not self.main.paused:
                if self.main.keys[K_0]:
                    for x in xrange(1):
                        pos = ((self.main.mouse_pos[0] - self.pos[0]) / float(self.scale),
                               (self.main.mouse_pos[1] - self.pos[1]) / float(self.scale))
                        size = (0.1, 0.1)
                        ang = math.radians(random.randint(0, 360))
                        mass = 100
                        velocity = (math.cos(ang), math.sin(ang))
                        speed = 1.2 * random.random()
                        restitution = 1.0
                        gib = Gib(self, pos, size, mass, velocity, speed, restitution)
                        self.gibs.append(gib)

            if not self.paused or (self.paused and self.framenumber == long(self.preview_framenumber)):
                rect = pygame.Rect(
                    (self.pos[0], self.pos[1], self.grid_size[0] * self.scale, self.grid_size[1] * self.scale))
                tile = ((self.main.mouse_pos[0] - self.pos[0]) / self.scale,
                        (self.main.mouse_pos[1] - self.pos[1]) / self.scale)

                if self.edit_mode == 1:
                    rerender = False
                    if self.main.mouse_button[0]:
                        rerender = True
                        self.grid[tile[1]][tile[0]] = Tile(self, tile)
                        if not (self.main.keys[K_LCTRL] or self.main.keys[K_RCTRL]):
                            pass
                        else:
                            #check left tile
                            if tile[0] - 1 < 0 or type(self.grid[tile[1]][tile[0] - 1]) == EmptyTile:
                                self.v_walls[tile[1]][tile[0]] = Wall(self, 1, (tile[0], tile[1]))
                            else:
                                self.v_walls[tile[1]][tile[0]] = EmptyWall(self, 1, (tile[0], tile[1]))
                                #check right tile
                            if tile[0] + 1 > self.grid_size[0] - 1 or type(
                                    self.grid[tile[1]][tile[0] + 1]) == EmptyTile:
                                self.v_walls[tile[1]][tile[0] + 1] = Wall(self, 1, (tile[0] + 1, tile[1]))
                            else:
                                self.v_walls[tile[1]][tile[0] + 1] = EmptyWall(self, 1, (tile[0] + 1, tile[1]))
                                #check top tile
                            if tile[1] - 1 < 0 or type(self.grid[tile[1] - 1][tile[0]]) == EmptyTile:
                                self.h_walls[tile[1]][tile[0]] = Wall(self, 0, (tile[0], tile[1]))
                            else:
                                self.h_walls[tile[1]][tile[0]] = EmptyWall(self, 0, (tile[0], tile[1]))
                                #check bottom tile
                            if tile[1] + 1 > self.grid_size[1] - 1 or type(
                                    self.grid[tile[1] + 1][tile[0]]) == EmptyTile:
                                self.h_walls[tile[1] + 1][tile[0]] = Wall(self, 0, (tile[0], tile[1] + 1))
                            else:
                                self.h_walls[tile[1] + 1][tile[0]] = EmptyWall(self, 0, (tile[0], tile[1] + 1))
                    elif self.main.mouse_button[2]:
                        self.grid[tile[1]][tile[0]] = EmptyTile(self, tile)
                        rerender = True
                        if not (self.main.keys[K_LCTRL] or self.main.keys[K_RCTRL]):
                            pass
                        else:
                            #check left tile
                            if not (tile[0] - 1 < 0 or type(self.grid[tile[1]][tile[0] - 1]) == EmptyTile):
                                self.v_walls[tile[1]][tile[0]] = Wall(self, 1, (tile[0], tile[1]))
                            else:
                                self.v_walls[tile[1]][tile[0]] = EmptyWall(self, 1, (tile[0], tile[1]))
                                #check right tile
                            if not (tile[0] + 1 > self.grid_size[0] - 1 or type(
                                    self.grid[tile[1]][tile[0] + 1]) == EmptyTile):
                                self.v_walls[tile[1]][tile[0] + 1] = Wall(self, 1, (tile[0] + 1, tile[1]))
                            else:
                                self.v_walls[tile[1]][tile[0] + 1] = EmptyWall(self, 1, (tile[0] + 1, tile[1]))
                                #check top tile
                            if not (tile[1] - 1 < 0 or type(self.grid[tile[1] - 1][tile[0]]) == EmptyTile):
                                self.h_walls[tile[1]][tile[0]] = Wall(self, 0, (tile[0], tile[1]))
                            else:
                                self.h_walls[tile[1]][tile[0]] = EmptyWall(self, 0, (tile[0], tile[1]))
                                #check bottom tile
                            if not (tile[1] + 1 > self.grid_size[1] - 1 or type(
                                    self.grid[tile[1] + 1][tile[0]]) == EmptyTile):
                                self.h_walls[tile[1] + 1][tile[0]] = Wall(self, 0, (tile[0], tile[1] + 1))
                            else:
                                self.h_walls[tile[1] + 1][tile[0]] = EmptyWall(self, 0, (tile[0], tile[1] + 1))

                    if rerender and (self.prev_tile_selected == None or not (
                                self.prev_tile_selected[0] == tile[0] and self.prev_tile_selected[1] == tile[1])):
                        self.prev_tile_selected = (int(tile[0]), int(tile[1]))
                        self.rerender()
                        self.last_prerendered_frame = long(-1)

                if rect.collidepoint(self.main.mouse_pos):
                    for event in self.main.events:
                        if event.type == KEYDOWN:
                            if event.key == K_1:
                                self.edit_mode = 1
                            elif event.key == K_2:
                                self.edit_mode = 2
                            elif event.key == K_3:
                                self.edit_mode = 3
                            elif event.key == K_4:
                                self.edit_mode = 4
                            elif event.key == K_5:
                                self.edit_mode = 5
                            elif event.key == K_6:
                                self.edit_mode = 6
                            elif event.key == K_7:
                                self.edit_mode = 7
                            elif event.key == K_k:
                                i = len(self.characters) - 1
                                while i >= 0:
                                    npc = self.characters[i]
                                    npc.explode()
                                    i -= 1
                        elif event.type == MOUSEBUTTONUP:
                            if self.edit_mode == 1:
                                self.prev_tile_selected = None
                        elif event.type == MOUSEBUTTONDOWN:
                            if self.edit_mode == 3:
                                if event.button == 1 or event.button == 3:
                                    selected = []

                                    for npc in self.characters:
                                        if npc.is_alive() and "jak" in npc.TYPES and npc.rect.collidepoint(self.main.mouse_pos):
                                            selected.append(npc)

                                    if event.button == 1:
                                        if len(selected) != 0:
                                            for j in selected:
                                                j.facing = (j.facing + 1) % 4
                                                j.target_facing = int(j.facing)
                                        else:
                                            self.characters.append(Jak(self, tile))
                                    elif event.button == 3:
                                        for j in selected:
                                            j.kill()
                                elif event.button == 4 or event.button == 5:
                                    if event.button == 4:
                                        offset = 1
                                    else:
                                        offset = -1

                                    for npc in self.characters:
                                        if npc.is_alive() and "jak" in npc.TYPES and npc.rect.collidepoint(self.main.mouse_pos):
                                            npc.speed += offset
                                            npc.speed = max(min(npc.speed, 60), 1)
                            elif self.edit_mode == 1:
                                if event.button == 4 or event.button == 5:
                                    T = self.grid[tile[1]][tile[0]]

                                    if event.button == 4:
                                        offset = -1
                                    else:
                                        offset = 1

                                    T.color_index = (T.color_index + offset) % 12
                                    T.needs_to_rerender = True

                                    self.rerender()
                            elif self.edit_mode == 2:
                                self.last_prerendered_frame = long(-1)
                                if event.button == 1 or event.button == 3:
                                    tile_rect = pygame.Rect((self.pos[0] + (tile[0] * self.scale),
                                                             self.pos[1] + (tile[1] * self.scale),
                                                             self.scale,
                                                             self.scale))
                                    left = self.main.mouse_pos[0] - tile_rect.left
                                    right = tile_rect.right - self.main.mouse_pos[0]
                                    top = self.main.mouse_pos[1] - tile_rect.top
                                    bottom = tile_rect.bottom - self.main.mouse_pos[1]

                                    m = min(left, right, top, bottom)

                                    if event.button == 1:
                                        if self.main.keys[K_LCTRL] or self.main.keys[K_RCTRL]:
                                            new_type = Door
                                        else:
                                            new_type = Wall
                                    else:
                                        new_type = EmptyWall

                                    if left == m:
                                        self.v_walls[tile[1]][tile[0]] = new_type(self, 1, tile)
                                    elif right == m:
                                        self.v_walls[tile[1]][tile[0] + 1] = new_type(self, 1, (tile[0] + 1, tile[1]))
                                    elif top == m:
                                        self.h_walls[tile[1]][tile[0]] = new_type(self, 0, tile)
                                    elif bottom == m:
                                        self.h_walls[tile[1] + 1][tile[0]] = new_type(self, 0, (tile[0], tile[1] + 1))
                                elif event.button == 4 or event.button == 5:
                                    if event.button == 4:
                                        offset = 1
                                    else:
                                        offset = -1

                                    tile_rect = pygame.Rect((self.pos[0] + (tile[0] * self.scale),
                                                             self.pos[1] + (tile[1] * self.scale),
                                                             self.scale,
                                                             self.scale))
                                    left = self.main.mouse_pos[0] - tile_rect.left
                                    right = tile_rect.right - self.main.mouse_pos[0]
                                    top = self.main.mouse_pos[1] - tile_rect.top
                                    bottom = tile_rect.bottom - self.main.mouse_pos[1]

                                    m = min(left, right, top, bottom)

                                    if left == m:
                                        wall = self.v_walls[tile[1]][tile[0]]
                                    elif right == m:
                                        wall = self.v_walls[tile[1]][tile[0] + 1]
                                    elif top == m:
                                        wall = self.h_walls[tile[1]][tile[0]]
                                    elif bottom == m:
                                        wall = self.h_walls[tile[1] + 1][tile[0]]

                                    if type(wall) == Door:
                                        wall.group = (wall.group + offset) % 12

                                self.rerender()
                            elif self.edit_mode == 7:
                                if event.button == 1:
                                    matches = False
                                    i = len(self.entities) - 1
                                    while i >= 0:
                                        ent = self.entities[i]
                                        if ent.is_alive() and ent.pos[0] == tile[0] and ent.pos[1] == tile[1]:
                                            matches = True
                                            break
                                        i -= 1
                                    if not matches:
                                        if self.main.keys[K_LCTRL] or self.main.keys[K_RCTRL]:
                                            self.entities.append(EdgeButton(self, tile))
                                        else:
                                            self.entities.append(Button(self, tile))
                                elif event.button == 3:
                                    i = len(self.entities) - 1
                                    while i >= 0:
                                        ent = self.entities[i]
                                        if ent.is_alive() and "button" in ent.TYPES and ent.pos[0] == tile[0] and ent.pos[1] == tile[1]:
                                            ent.kill()
                                        i -= 1
                                elif event.button == 4 or event.button == 5:
                                    if event.button == 4:
                                        offset = 1
                                    else:
                                        offset = -1

                                    for ent in self.entities:
                                        if ent.is_alive() and "button" in ent.TYPES and ent.pos[0] == tile[0] and ent.pos[1] == tile[1]:
                                            ent.group += offset
                                            ent.group %= 12
                            elif self.edit_mode == 4:
                                if event.button == 1:
                                    matches = False
                                    i = len(self.entities) - 1
                                    while i >= 0:
                                        ent = self.entities[i]
                                        if ent.is_alive() and ent.pos[0] == tile[0] and ent.pos[1] == tile[1]:
                                            matches = True
                                            if "mine" in ent.TYPES:
                                                ent.explode()
                                                self.last_prerendered_frame = long(-1)
                                            break
                                        i -= 1
                                    if not matches:
                                        self.entities.append(Mine(self, tile))
                                        self.last_prerendered_frame = long(-1)
                                elif event.button == 3:
                                    i = len(self.entities) - 1
                                    while i >= 0:
                                        ent = self.entities[i]
                                        if ent.is_alive() and "mine" in ent.TYPES and ent.pos[0] == tile[0] and ent.pos[1] == tile[1]:
                                            ent.kill()
                                            self.last_prerendered_frame = long(-1)
                                        i -= 1
                            elif self.edit_mode == 5:
                                if event.button == 1:
                                    matches = False
                                    i = len(self.entities) - 1
                                    while i >= 0:
                                        ent = self.entities[i]
                                        if ent.is_alive() and ent.pos[0] == tile[0] and ent.pos[1] == tile[1]:
                                            matches = True
                                            break
                                        i -= 1
                                    if not matches:
                                        self.entities.append(Turret(self, tile))
                                        self.last_prerendered_frame = long(-1)
                                elif event.button == 3:
                                    i = len(self.entities) - 1
                                    while i >= 0:
                                        ent = self.entities[i]
                                        if ent.is_alive() and "turret" in ent.TYPES and ent.pos[0] == tile[0] and ent.pos[1] == tile[1]:
                                            ent.kill()
                                            self.last_prerendered_frame = long(-1)
                                        i -= 1
                            elif self.edit_mode == 6:
                                if event.button == 1:
                                    matches = False
                                    i = len(self.entities) - 1
                                    while i >= 0:
                                        ent = self.entities[i]
                                        if ent.is_alive() and ent.pos[0] == tile[0] and ent.pos[1] == tile[1]:
                                            matches = True
                                            break
                                        i -= 1
                                    if not matches:
                                        self.entities.append(Spawner(self, tile))
                                elif event.button == 3:
                                    i = len(self.entities) - 1
                                    while i >= 0:
                                        ent = self.entities[i]
                                        if ent.is_alive() and "spawner" in ent.TYPES and ent.pos[0] == tile[0] and ent.pos[1] == tile[1]:
                                            ent.kill()
                                        i -= 1
                                elif event.button == 4 or event.button == 5:
                                    if event.button == 4:
                                        offset = 1
                                    else:
                                        offset = -1

                                    for ent in self.entities:
                                        if ent.is_alive() and "spawner" in ent.TYPES and ent.pos[0] == tile[0] and ent.pos[1] == tile[1]:
                                            ent.delay_time += offset
                                            ent.delay_time = max(min(ent.delay_time, 60), 1)

            if not self.paused or self.step_once:
                self.debug_data = []

                #performs collision optimization
                self.quadtree.reset()

                for npc in self.characters:
                    if npc.is_alive():
                        self.quadtree.add_entity(npc)

                for ent in self.entities:
                    if ent.is_alive():
                        self.quadtree.add_entity(ent)

                self.quadtree.test_collisions()

                #then performs normal update

                #tiles
                for row in self.grid:
                    for tile in row:
                        tile.update()

                #h walls
                for row in self.h_walls:
                    for wall in row:
                        wall.update()

                #v walls
                for row in self.v_walls:
                    for wall in row:
                        wall.update()

                self.random.update()
                self.id_manager.update()

                for npc in self.characters:
                    npc.update()

                for ent in self.entities:
                    ent.update()

                for gib in self.gibs:
                    gib.update()

    def move(self):
        if (not self.paused or self.step_once) and not self.main.paused:
            self.group_status = list(self.next_group_status)

            #tiles
            for row in self.grid:
                for tile in row:
                    tile.move()

            #h walls
            for row in self.h_walls:
                for wall in row:
                    wall.move()

            #v walls
            for row in self.v_walls:
                for wall in row:
                    wall.move()

            self.timemachine.update_entity(int(self.ID), self.pickle())

            self.random.move()
            self.timemachine.update_entity(int(self.random.ID), self.random.pickle())

            self.id_manager.move()
            self.timemachine.update_entity(int(self.id_manager.ID), self.id_manager.pickle())

            i = 0
            while i < len(self.characters):
                npc = self.characters[i]
                npc.move()
                self.timemachine.update_entity(int(npc.ID), npc.pickle())

                #if npc.ID == 1:
                #    print self.timemachine.entities[npc.ID].tracks["true_pos"]

                if not npc.is_alive():
                    self.characters.pop(i)
                else:
                    i += 1

            i = 0
            while i < len(self.entities):
                ent = self.entities[i]
                ent.move()
                self.timemachine.update_entity(int(ent.ID), ent.pickle())
                if not ent.is_alive():
                    self.entities.pop(i)
                else:
                    i += 1

            i = 0
            while i < len(self.gibs):
                gib = self.gibs[i]
                gib.move()
                self.timemachine.update_entity(int(gib.ID), gib.pickle())
                if not gib.is_alive():
                    self.gibs.pop(i)
                else:
                    i += 1

            self.framenumber += 1

            if self.step_once:
                self.preview_framenumber = long(self.framenumber)

    def rerender(self, fullrerender=False):
        if not fullrerender:
            rerender_list = []

            #first checks if any tile needs to rerender
            #this will disable any neighboring walls for rerendering
            for row in self.grid:
                for tile in row:
                    if tile.needs_to_rerender:
                        tile.needs_to_rerender = False
                        self.v_walls[tile.pos[1]][tile.pos[0]].needs_to_rerender = False
                        self.h_walls[tile.pos[1]][tile.pos[0]].needs_to_rerender = False
                        self.v_walls[tile.pos[1]][tile.pos[0] + 1].needs_to_rerender = False
                        self.h_walls[tile.pos[1] + 1][tile.pos[0]].needs_to_rerender = False

                        rect = pygame.Rect(((tile.pos[0] * self.scale),
                                            (tile.pos[1] * self.scale),
                                            self.scale,
                                            self.scale))
                        rect = rect.inflate(self.scale * TILE_SHADOW_SIZE + 2, self.scale * TILE_SHADOW_SIZE + 2)
                        rerender_list.append(rect)

            wall_width = max(int(self.scale * WALL_THICKNESS), 1)
            wall_offset = int((wall_width / 2.0 - 0.5))

            #h walls
            for row in self.h_walls:
                for wall in row:
                    if wall.needs_to_rerender:
                        rect = pygame.Rect((wall.pos[0] * self.scale) - wall_offset,
                                           (wall.pos[1] * self.scale) - (wall_width / 2),
                                           self.scale + (wall_offset * 2) + 1,
                                           wall_width + 1)
                        rect.inflate_ip(2, 2)
                        rerender_list.append(rect)

            #v walls
            for row in self.v_walls:
                for wall in row:
                    if wall.needs_to_rerender:
                        rect = pygame.Rect((wall.pos[0] * self.scale) - (wall_width / 2),
                                           (wall.pos[1] * self.scale) - wall_offset,
                                           wall_width + 1,
                                           self.scale + (wall_offset * 2) + 1)
                        rect.inflate_ip(2, 2)
                        rerender_list.append(rect)

            #goes through the list and patches the surface
            for rect in rerender_list:
                self.surface.set_clip(rect)

                #self.surface.fill((0,0,0,0))
                self.surface.fill(self.bg_color)

                #determines which things should be rerendered
                left = (rect.left - self.pos[0]) / self.scale
                top = (rect.top - self.pos[1]) / self.scale
                right = int(math.ceil((rect.right - self.pos[0]) / float(self.scale))) + 1
                bottom = int(math.ceil((rect.bottom - self.pos[1]) / float(self.scale))) + 1

                for y in xrange(top, min(bottom, self.grid_size[1])):
                    for x in xrange(left, min(right, self.grid_size[0])):
                        self.grid[y][x].rerender_shadow()

                for y in xrange(top, min(bottom, self.grid_size[1])):
                    for x in xrange(left, min(right, self.grid_size[0])):
                        self.grid[y][x].rerender()

                for y in xrange(top, min(bottom, self.grid_size[1] + 1)):
                    for x in xrange(left, min(right, self.grid_size[0])):
                        self.h_walls[y][x].rerender()

                for y in xrange(top, min(bottom, self.grid_size[1])):
                    for x in xrange(left, min(right, self.grid_size[0] + 1)):
                        self.v_walls[y][x].rerender()

                if SHOW_GRID:
                    for x in xrange(left, min(right, self.grid_size[0]) + 1):
                        s = pygame.Surface((2, self.grid_size[1] * self.scale))
                        s.fill(GRID_COLOR)
                        s.set_alpha(GRID_ALPHA)
                        self.surface.blit(s, (x * self.scale, 0))
                    for y in xrange(top, min(bottom, self.grid_size[1] + 1)):
                        s = pygame.Surface((self.grid_size[0] * self.scale, 2))
                        s.fill(GRID_COLOR)
                        s.set_alpha(GRID_ALPHA)
                        self.surface.blit(s, (0, y * self.scale))

                if DEBUG_WORLD_RERENDER:
                    pygame.draw.rect(self.surface, (255, 0, 0), rect, 1)

            self.surface.set_clip(None)

        else:
            #tile shadows
            for row in self.grid:
                for tile in row:
                    if tile.needs_to_rerender:
                        tile.rerender_shadow()

            #tiles
            for row in self.grid:
                for tile in row:
                    if tile.needs_to_rerender:
                        tile.rerender()

            #h walls
            for row in self.h_walls:
                for wall in row:
                    if wall.needs_to_rerender:
                        wall.rerender()

            #v walls
            for row in self.v_walls:
                for wall in row:
                    if wall.needs_to_rerender:
                        wall.rerender()

    def render(self):
        #print self.framenumber, self.preview_framenumber, self.paused
        if not self.paused or (self.paused and long(self.preview_framenumber) == self.framenumber):
            self.main.screen.blit(self.surface, self.pos)

            #tiles
            for row in self.grid:
                for tile in row:
                    tile.render()

            #h walls
            for row in self.h_walls:
                for wall in row:
                    wall.render()

            #v walls
            for row in self.v_walls:
                for wall in row:
                    wall.render()

            for g in self.gibs:
                if not g.render_above:
                    g.render()

            if self.paused and self.last_prerendered_frame != self.framenumber and long(self.preview_framenumber) == self.framenumber:
                self.last_prerendered_frame = long(self.framenumber)
                self.prerender_surface.fill((0,0,0,0))

                for e in self.entities:
                    e.prerender()
                for n in self.characters:
                    n.prerender()

                for e in self.entities:
                    e.prerender_outline()
                for n in self.characters:
                    n.prerender_outline()

            if self.paused and not self.main.paused:
                self.main.screen.blit(self.prerender_surface, self.pos)

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

            for data in self.debug_data:
                if data[0] == "line":
                    color = data[1]
                    p1 = data[2]
                    p2 = data[3]
                    width = data[4]

                    p1 = (p1[0] * self.scale + self.pos[0], p1[1] * self.scale + self.pos[1])
                    p2 = (p2[0] * self.scale + self.pos[0], p2[1] * self.scale + self.pos[1])

                    pygame.draw.line(self.main.screen, color, p1, p2, width)
                elif data[0] == "rect":
                    color = data[1]
                    rect = list(data[2])
                    width = data[3]

                    rect[0] = rect[0] * self.scale + self.pos[0]
                    rect[1] = rect[1] * self.scale + self.pos[1]
                    rect[2] = rect[2] * self.scale
                    rect[3] = rect[3] * self.scale

                    pygame.draw.rect(self.main.screen, color, rect, width)
                elif data[0] == "circle":
                    color = data[1]
                    p = data[2]
                    radius = data[3]
                    width = data[4]

                    p = (int(p[0] * self.scale + self.pos[0]), int(p[1] * self.scale + self.pos[1]))
                    radius = max(int(radius * self.scale), 1)

                    pygame.draw.circle(self.main.screen, color, p, radius, width)
                elif data[0] == "text":
                    font = data[1]
                    s = data[2]
                    color = data[3]
                    p = data[4]

                    p = (int(p[0] * self.scale + self.pos[0]), int(p[1] * self.scale + self.pos[1]))

                    surface = font.render(s, True, color)
                    rect = surface.get_rect(center=p)

                    self.main.screen.blit(surface, rect)
        else:
            self.scrub_preview.render()

        if self.paused and not self.main.paused:
            if self.framenumber == long(self.preview_framenumber):
                libs.viseffect.draw_letterboxing(self.main.screen, self.main.screen_size[1] * 0.1, 64)
                libs.HUD.drawPause(self.main)
                libs.HUD.drawTapeTime(self.main, long(self.preview_framenumber), 1.0)
            else:
                libs.viseffect.static(self.main.screen, 10, 1, 1, 255, seed=long(self.preview_framenumber) + 1)

                #creates a warped line
                #libs.viseffect.tape_pull(self.main.screen, self.main.screen_size[1]*0.33, 2, 50, 3)
                #libs.viseffect.tape_pull(self.main.screen, self.main.screen_size[1]*0.66, 2, 50, 3)

                #creates a fuzzy appearance
                """
                size = lerp_lists((0,0),self.main.screen_size,0.33)
                s = pygame.transform.smoothscale(pygame.transform.smoothscale(self.main.screen, (int(size[0]),int(size[1]))),self.main.screen_size)
                self.main.screen.blit(s,(0,0),special_flags=BLEND_RGB_MAX)
                """

                size = lerp_lists((0, 0), self.main.screen_size, 0.95)
                s = pygame.transform.scale(self.main.screen, (int(size[0]), int(size[1])))
                rect = s.get_rect(center=(self.main.screen_size[0] / 2, self.main.screen_size[1] / 2))
                libs.viseffect.draw_rect_shadow(self.main.screen,
                                                rect,
                                                max((self.main.screen_size[0] - size[0]) / 2,
                                                    (self.main.screen_size[1] - size[1]) / 2,
                                                    1),
                                                255)
                self.main.screen.blit(s, rect)

                libs.HUD.drawScrub(self.main)
                p = 0
                if self.framenumber > 0:
                    p = float(self.preview_framenumber) / self.framenumber
                libs.HUD.drawTapeTime(self.main, long(self.preview_framenumber), p)

        if DEBUG_QUADTREE:
            self.quadtree.render()

        if DEBUG_TIME_MACHINE:
            self.timemachine.render_debug(self.main, self, 0, 0, (1, 8))
