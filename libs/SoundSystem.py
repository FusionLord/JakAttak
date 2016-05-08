import pygame

##################################

class SoundSystem(object):
    def __init__(self):
        self.__sounds = {}

    def get_sound(self, name):
        name = "data/sounds/"+name
        if name not in self.__sounds:
            return self.__load_and_add_sound(name)
        return self.__sounds[name]

    def __load_and_add_sound(self,name):
        sound = pygame.mixer.Sound(name)
        self.__sounds[name] = sound
        return sound
