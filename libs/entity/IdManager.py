from libs.TimeMachine.PickledEntity import*
from libs.TimeMachine.TimeValue import*
from libs.entity.Entity import*

class IdManager(Entity):
    TYPES = []

    def init(self):
        self.set_id()
        self.last_id = int(Entity.ENTITY_ID)

    def move(self):
        self.last_id = int(Entity.ENTITY_ID)

    def pickle(self):
        pickle = PickledEntity(int(self.ID), self.world.framenumber, IdManager)
        pickle.update_value("_alive",TimeValue(bool(self.alive), self.world.framenumber))
        pickle.update_value("last_id",
                            TimeValue(int(self.last_id),
                            self.world.framenumber))
        return pickle

    def unpickle(self, world, pickledentity):
        self.__init__(world, (0,0), (0,0))
        self.ID = pickledentity.ID

        self.alive = pickledentity.tracks["_alive"][0].get_value_at(None)
        self.last_id = pickledentity.tracks["last_id"][0].get_value_at(None)

        Entity.ENTITY_ID = int(self.last_id)

