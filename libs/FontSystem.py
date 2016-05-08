import pygame

##################################

class FontSystem(object):
    DEFAULT = "Analogawesome.ttf"

    def __init__(self):
        self.__fonts = {}

    def get_font(self, name, size):
        name = "data/fonts/"+name
        id = name+": "+str(int(size))
        if id not in self.__fonts:
            return self.__load_and_add_font(name,size)
        return self.__fonts[id]

    def __load_and_add_font(self,name,size):
        id = name+": "+str(int(size))
        font = pygame.font.Font(name,size)
        self.__fonts[id] = font
        return font
