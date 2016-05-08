from Wall import*

class EmptyWall(Wall):
    def init(self):
        self.is_solid = False

    def rerender(self):
        self.needs_to_rerender = False