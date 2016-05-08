
class LevelEditorGUI(object):
    tool_list = []
    npc_list = []
    entity_list = []

    def __init__(self, world):
        self._world = world

        self.has_focus = False

        self.current_tool = None
        self.selected = None

    def update(self):
        pass

    def move(self):
        pass

    def render(self):
        pass