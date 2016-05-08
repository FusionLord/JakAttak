#from collections import OrderedDict
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

##################################

from libs.entity.Entity import*
from libs.TimeMachine.PickledEntity import*
from libs.TimeMachine.TimeValue import*
from libs.common import*
from libs.locals import*
import libs.HUD

##################################

class TimeMachine(object):
    def __init__(self):
        self.entities = {}#OrderedDict()

    def get_frame(self, frame):
        pickles = {}
        for key in self.entities:
            ent = self.entities[key]
            if ent.startframe <= frame and ((ent.endframe == None) or (ent.endframe >= frame)):
                pickle = PickledEntity(ent.ID, ent.startframe, ent.type)
                for track in ent.tracks:
                    T = ent.tracks[track]

                    end = ent.endframe

                    i = len(T) - 1
                    while i >= 0:
                        var = T[i]
                        if var.frame <= frame and ((end == None) or (end >= frame)):
                            break
                        i -= 1

                    value = var.get_value_at(frame)

                    pickle.update_value(track,TimeValue(value, frame))

                pickles[key] = pickle
        return pickles

    def update_entity(self, id, pickle):
        if str(id) in self.entities:
            self.entities[str(id)].update_values(pickle)
        else:
            self.entities[str(id)] = pickle

    def clear_everything_after_this_frame(self, frame):
        keys = []
        for key in self.entities:
            keys.append(key)
        for key in keys:
            if self.entities[key].startframe > frame:
                self.entities.pop(key, None)
            else:
                self.entities[key].clear_everything_after_this_frame(frame)

    def render_debug(self, main, world, horiz_offset, verti_offset, scale = (1,10)):
        ENT_COLOR = HSVtoRGB(300,50,75)
        VAL_COLOR = HSVtoRGB(200,50,75)
        ENT_OUTLINE_COLOR = lerp_lists((0,0,0),ENT_COLOR,0.25)
        VAL_OUTLINE_COLOR = lerp_lists((0,0,0),VAL_COLOR,0.25)

        row = 0
        for key in self.entities:
            ent = self.entities[key]

            start = ent.startframe
            if ent.endframe == None:
                end = world.framenumber
            else:
                end = ent.endframe

            rect = pygame.Rect( ((start - horiz_offset)*scale[0],
                                (row - verti_offset)*scale[1],
                                ( end - start )*scale[0],
                                scale[1]) )

            pygame.draw.rect(main.screen, ENT_COLOR, rect)
            pygame.draw.rect(main.screen, ENT_OUTLINE_COLOR, rect, 1)

            text = libs.HUD.renderText(str(ent.ID)+": "+str(ent.type).upper(), main.fonts.get_font(main.fonts.DEFAULT,int(scale[1]*0.75)), antialias=True)
            main.screen.blit(text,(0,(row-verti_offset)*scale[1]))

            row += 1

            if DEBUG_TIME_MACHINE_SHOW_VARS:
                i = 0
                for track in ent.tracks:
                    T = ent.tracks[track]

                    column = int(end)

                    i = len(T) - 1
                    while i >= 0:
                        val = T[i]

                        rect = pygame.Rect( ((val.frame - horiz_offset)*scale[0],
                                    (row - verti_offset)*scale[1],
                                    ( column - val.frame )*scale[0],
                                    scale[1]) )

                        pygame.draw.rect(main.screen, VAL_COLOR, rect)
                        pygame.draw.rect(main.screen, VAL_OUTLINE_COLOR, rect, 1)

                        text = libs.HUD.renderText(str(val.value).upper(),
                                                   main.fonts.get_font(main.fonts.DEFAULT,int(scale[1]*0.75)),
                                                   color = VAL_OUTLINE_COLOR,
                                                   antialias=True)
                        main.screen.set_clip(rect)
                        main.screen.blit(text,rect)
                        main.screen.set_clip(None)

                        column = val.frame
                        i -= 1

                    text = libs.HUD.renderText(track.upper(), main.fonts.get_font(main.fonts.DEFAULT,int(scale[1]*0.75)), antialias=True)
                    main.screen.blit(text,(0,(row-verti_offset)*scale[1]))

                    row += 1

        pos = (world.framenumber-horiz_offset)*scale[0]
        pygame.draw.line(main.screen,(255,0,0),(pos,-verti_offset*scale[1]),(pos,(row-verti_offset)*scale[1]))

