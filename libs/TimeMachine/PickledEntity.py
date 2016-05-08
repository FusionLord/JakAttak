class PickledEntity(object):
    def __init__(self, id, startframe, type):
        self.ID = int(id)
        self.startframe = int(startframe)
        self.endframe = None
        self.tracks = {}
        self.type = type

    def __str__(self):
        return "PickledEntity[#"+str(self.ID)+"]("+str(self.startframe)+")("+str(self.endframe)+")"

    def __repr__(self):
        return "[#"+str(self.ID)+"]("+str(self.startframe)+")("+str(self.endframe)+")"

    def update_value(self, var_name, value):
        if self.endframe == None and var_name == "alive" and value.value == False:
            self.endframe = int(value.frame)
        if var_name in self.tracks:
            track = self.tracks[var_name]
        else:
            track = [value]
            self.tracks[var_name] = track
            return
        #checks if there's any notible change
        is_as_estimated = track[-1].compare(value)
        if is_as_estimated:
            pass
        else:
            self.tracks[var_name] = track + [value]

    def update_values(self, pickle):
        for track in pickle.tracks:
            self.update_value(track,pickle.tracks[track][-1])

    def clear_everything_after_this_frame(self, frame):
        if self.endframe != None and self.endframe > frame:
            self.endframe = None

        if not (self.endframe != None and self.endframe <= frame):
            for track in self.tracks:
                T = self.tracks[track]
                i = 0
                while i < len(T):
                    if T[i].frame >= frame:
                        if T[i].frame == frame:
                            i += 1
                        break
                    i += 1
                if i < len(T):
                    self.tracks[track] = T[:i]
