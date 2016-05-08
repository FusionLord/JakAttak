import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

from libs.common import*
from libs.entity.game.particles.Gib import*

class Flame(Gib):
    SIZE = (0.79,0.79)

    def init(self):
        self.health = int(60*0.5)
        self.max_health = int(self.health)
        
    def pickle(self):
        pickle = PickledEntity(int(self.ID), self.world.framenumber, Flame)
        pickle.update_value("alive",TimeValue(bool(self.alive), self.world.framenumber))
        pickle.update_value("health",
                            TimeValue(float(self.health),
                                      self.world.framenumber,
                                      TimeValuePattern_Increment(-1)))
        pickle.update_value("max_health",TimeValue(float(self.max_health), self.world.framenumber))
        pickle.update_value("render_above",TimeValue(float(self.render_above), self.world.framenumber))
        pickle.update_value("alpha",TimeValue(float(self.alpha), self.world.framenumber))
        pickle.update_value("start_frame",TimeValue(int(self.start_frame), self.world.framenumber))
        pickle.update_value("start_pos",TimeValue(tuple(self.start_pos), self.world.framenumber))
        if self.end_pos == None:
            pickle.update_value("end_pos",TimeValue(None, self.world.framenumber))
        else:
            pickle.update_value("end_pos",TimeValue(tuple(self.end_pos), self.world.framenumber))

        pickle.update_value("impact_pos",TimeValue(tuple(self.impact_pos), self.world.framenumber))
        pickle.update_value("mass",TimeValue(float(self.mass), self.world.framenumber))
        pickle.update_value("size",TimeValue(tuple(self.size), self.world.framenumber))
        pickle.update_value("velocity",TimeValue(tuple(self.velocity), self.world.framenumber))
        pickle.update_value("speed",TimeValue(float(self.speed), self.world.framenumber))
        pickle.update_value("restitution",TimeValue(float(self.restitution), self.world.framenumber))
        pickle.update_value("moving",TimeValue(bool(self.moving), self.world.framenumber))

        return pickle

    def unpickle(self, world, pickledentity):
        pos = pickledentity.tracks["start_pos"][0].get_value_at(None)
        size = pickledentity.tracks["size"][0].get_value_at(None)
        mass = pickledentity.tracks["mass"][0].get_value_at(None)
        velocity = pickledentity.tracks["velocity"][0].get_value_at(None)
        speed = pickledentity.tracks["speed"][0].get_value_at(None)
        restitution = pickledentity.tracks["restitution"][0].get_value_at(None)

        self.__init__(world, pos, size, mass, velocity, speed, restitution)

        self.ID = pickledentity.ID

        self.alive = pickledentity.tracks["alive"][0].get_value_at(None)
        self.health = pickledentity.tracks["health"][0].get_value_at(None)
        self.max_health = pickledentity.tracks["max_health"][0].get_value_at(None)
        self.render_above = pickledentity.tracks["render_above"][0].get_value_at(None)
        self.alpha = pickledentity.tracks["alpha"][0].get_value_at(None)
        self.start_frame = pickledentity.tracks["start_frame"][0].get_value_at(None)
        self.start_pos = pos
        self.end_pos = pickledentity.tracks["end_pos"][0].get_value_at(None)
        self.impact_pos = pickledentity.tracks["impact_pos"][0].get_value_at(None)
        self.size = pickledentity.tracks["size"][0].get_value_at(None)
        self.mass = mass
        self.velocity = velocity
        self.speed = speed
        self.restitution = restitution
        self.moving = pickledentity.tracks["moving"][0].get_value_at(None)

    def update(self):
        self.health -= 1
        if self.health <= 0:
            self.alive = False

        """
        if self.world.main.frame_number % 5 == 0 and random.randint(0,10) == 0:
            for x in xrange(1):
                pos = self.pos
                size = self.init_size
                ang = math.radians(random.randint(0,360))
                mass = 1000

                velocity = self.velocity
                speed = self.speed*random.random()*2

                restitution = 0.2

                gib = Smoke(self.world, pos, size, mass, velocity, speed, restitution)
                self.world.main.gibs.append(gib)
        """

    def render(self):
        p = min(1-(self.health/float(self.max_health)),1)

        if p < 0.1:
            color = lerp_lists((255,255,255),(255,255,0),(p)/0.1)
        elif p < 0.5:
            color = lerp_lists((255,255,0),(255,0,0),(p-0.1)/0.5)
        else:
            color = (255,0,0)

        color = (int(color[0]),int(color[1]),int(color[2]))

        if self.moving:
            pos = list(self.get_pos_at_frame(self.world.framenumber))
        else:
            pos = list(self.end_pos)

        size = lerp_lists((self.size[0],self.size[1]),(0,0),p)

        size[0] = size[0]*self.world.scale
        size[1] = size[1]*self.world.scale

        size[0] = round((size[0])/PRECISION)*PRECISION
        size[1] = round((size[1])/PRECISION)*PRECISION

        size[0] = max(size[0],PRECISION)
        size[1] = max(size[1],PRECISION)

        topleft = list(pos)

        topleft[0] = self.world.pos[0]+(topleft[0]*self.world.scale)
        topleft[1] = self.world.pos[1]+(topleft[1]*self.world.scale)

        topleft[0] -= size[0]/2.0
        topleft[1] -= size[1]/2.0

        bottomright = [topleft[0]+size[0],
                        topleft[1]+size[1]]

        topleft[0] = round((topleft[0])/PRECISION)*PRECISION
        topleft[1] = round((topleft[1])/PRECISION)*PRECISION

        bottomright[0] = round((bottomright[0])/PRECISION)*PRECISION
        bottomright[1] = round((bottomright[1])/PRECISION)*PRECISION

        new_size = (bottomright[0]-topleft[0],bottomright[1]-topleft[1])

        surface = pygame.Surface((new_size[0],new_size[1]))
        surface.fill(lerp_lists(color,(0,0,0),lerp(1,p,(self.alpha/255.0))))
        rect = surface.get_rect(topleft = (int(topleft[0]),int(topleft[1])))

        self.world.main.screen.blit(surface, rect, special_flags=BLEND_RGB_ADD)
