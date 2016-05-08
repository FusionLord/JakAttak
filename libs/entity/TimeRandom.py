import random

from libs.TimeMachine.PickledEntity import*
from libs.TimeMachine.TimeValue import*
from libs.TimeMachine.TimeValuePattern.patterns.TimeValuePattern_SawIncrement import*
from libs.entity.Entity import*

class TimeRandom(Entity):
    MAX_SEED = 100000
    TYPES = []

    def init(self):
        self.seed = 0
        self.R = random.Random()
        self.R.seed(self.seed)

        self.set_id()

    def pickle(self):
        pickle = PickledEntity(int(self.ID), self.world.framenumber, TimeRandom)
        pickle.update_value("alive",TimeValue(bool(self.alive), self.world.framenumber))
        pickle.update_value("seed",
                            TimeValue(int(self.seed),
                            self.world.framenumber))
        return pickle

    def unpickle(self, world, pickledentity):
        self.__init__(world, (0,0), (0,0))
        self.ID = pickledentity.ID

        self.alive = pickledentity.tracks["alive"][0].get_value_at(None)
        self.seed = pickledentity.tracks["seed"][0].get_value_at(None)

        self.R.seed(self.seed)

    def update_seed(self):
        self.seed += 1
        self.seed %= TimeRandom.MAX_SEED
        self.R.seed(self.seed)

    def rand(self):
        val = self.R.random()
        self.update_seed()
        return val

    def randint(self, a, b):
        val = self.R.randint(a, b)
        self.update_seed()
        return val

    def choice(self, seq):
        val = self.R.choice(seq)
        self.update_seed()
        return val

