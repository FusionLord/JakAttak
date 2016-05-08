import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

import pygame

from libs.common import *

### CLASSES ###

class QuadLeaf(object):
    def __init__(self, world, rect, quadtree, level):
        self.world = world
        self.rect = rect
        self.quadtree = quadtree
        self.level = level

        quadtree.levels[level].append(self)
        self.branches = None
        self.entities = []#a list of collidable objects on this leaf

    def __str__(self):
        if self.branches != None:
            s = "["
            for b in self.branches:
                s += str(b)
            s += "]"
            return s
        else:
            return "[]"

    def subdivide(self):
        self.branches = []
        for rect in self.rect.quad_split():
            b = QuadLeaf(self.world, rect, self.quadtree, self.level + 1)
            self.branches.append(b)

        #the first thing it has to check is if the object fits in any branches
        for b in self.branches:
            fits = None
            for obj in self.entities:
                if b.rect.contains(obj.get_collision_rect()):
                    fits = b
            if fits == None:
                #doesn't fit in any of the branches, stays on this level
                for b in self.branches:
                    b.test_collisions(obj)
            else:
                #it DOES fit in a branch, hand it to the branch
                fits.add_entity(obj)

    def test_collisions(self, obj):
        for obj2 in self.entities:
            if obj2.get_collision_rect().colliderect(obj.get_collision_rect()):
                if (obj, obj2) not in self.quadtree.collisions and (obj2, obj) not in self.quadtree.collisions:
                    self.quadtree.collisions.append((obj, obj2))

        if self.level == self.quadtree.level_limit - 1:
            return

        if self.branches != None:
            for b in self.branches:
                b.test_collisions(obj)

    def add_entity(self, obj):
        for obj2 in self.entities:
            if obj2.get_collision_rect().colliderect(obj.get_collision_rect()):
                if (obj, obj2) not in self.quadtree.collisions and (obj2, obj) not in self.quadtree.collisions:
                    self.quadtree.collisions.append((obj, obj2))

        if self.level == self.quadtree.level_limit - 1:#if it's hit the limit of levels
            self.entities.append(obj)
            return

        if self.branches == None:
            self.entities.append(obj)
            if len(self.entities) == self.quadtree.bucket_limit:
                self.subdivide()
        else:
            fits = None
            for b in self.branches:
                if b.rect.contains(obj.get_collision_rect()):
                    fits = b
            if fits == None:
                #doesn't fit in any of the branches, stays on this level
                for b in self.branches:
                    b.test_collisions(obj)
                self.entities.append(obj)
            else:
                #it DOES fit in a branch, hand it to the branch
                fits.add_entity(obj)

    def render(self):
        pygame.draw.rect(self.world.main.screen, (127, 127, 127), (self.rect*self.world.scale).get_rect().move(self.world.pos[0],self.world.pos[1]), 1)
        if self.branches != None:
            for b in self.branches:
                b.render()

        for ent in self.entities:
            pygame.draw.rect(self.world.main.screen, (255,255,255), (ent.get_collision_rect()*self.world.scale).get_rect().move(self.world.pos[0],self.world.pos[1]), 1)



class QuadTree(object):
    def __init__(self, world, world_rect, level_limit = 3, bucket_limit = 3):
        self.world = world
        self.world_rect = world_rect

        self.level_limit = level_limit
        self.bucket_limit = bucket_limit

        self.levels = []
        for x in xrange(self.level_limit):
            self.levels.append([])
        self.branches = []
        if self.level_limit > 0:
            for rect in self.world_rect.quad_split():
                b = QuadLeaf(self.world, rect, self, 0)
                self.branches.append(b)
        self.entities = []#a list of all collidable objects on the main level
        self.collisions = []

    def reset(self):
        self.__init__(self.world, self.world_rect, self.level_limit, self.bucket_limit)

    def __str__(self):
        if len(self.branches) > 0:
            s = "["
            for b in self.branches:
                s += str(b)
            s += "]"
            return s
        else:
            return "[]"

    def add_entity(self, obj):
        for obj2 in self.entities:
            if obj2.get_collision_rect().colliderect(obj.get_collision_rect()):
                if (obj, obj2) not in self.collisions and (obj2, obj) not in self.collisions:
                    self.collisions.append((obj, obj2))

        if self.level_limit <= 0:
            self.entities.append(obj)
            return

        #the first thing it has to check is if the object fits in any branches
        fits = None
        for b in self.branches:
            if b.rect.contains(obj.get_collision_rect()):
                fits = b
        if fits == None:
            #doesn't fit in any of the branches, stays on main level
            self.entities.append(obj)
            for b in self.branches:
                b.test_collisions(obj)
        else:
            #it DOES fit in a branch, hand it to the branch
            fits.add_entity(obj)

    def test_collisions(self):
        #this means that each object will need a collide command
        for c in self.collisions:
            match = True
            if c[0].COLLISION_FILTER != None:
                for t in c[0].COLLISION_FILTER:
                    if not (t in c[1].TYPES):
                        match = False
                        break
            if match:
                c[0].collisions.append(c[1])


            match = True
            if c[1].COLLISION_FILTER != None:
                for t in c[1].COLLISION_FILTER:
                    if not (t in c[0].TYPES):
                        match = False
                        break
            if match:
                c[1].collisions.append(c[0])

    def render(self):
        for branch in self.branches:
            branch.render()

        for ent in self.entities:
            pygame.draw.rect(self.world.main.screen, (255,255,255), (ent.get_collision_rect()*self.world.scale).get_rect().move(self.world.pos[0],self.world.pos[1]), 1)
      
     
