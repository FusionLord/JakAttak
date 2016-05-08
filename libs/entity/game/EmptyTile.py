from Tile import*

class EmptyTile(Tile):
    def init(self):
        self.has_shadow = False

    def rerender_shadow(self):
        pass

    def rerender(self):
        self.needs_to_rerender = False
