
import pygame

##################################

class Menu():
    def __init__(self, main):
        self.main = main

        self.init()

    def init(self):
        #this is for child classes
        pass

    def cleanup(self):
        pass

    def play_sound(self, sound, mul=1.0, pan=0.5, force=False):
        channel = pygame.mixer.find_channel(force)

        if channel:
            channel.set_volume((1.0-pan)*mul,(pan)*mul)
            channel.play(sound)

        return channel

    def update(self):
        pass

    def move(self):
        pass

    def render(self):
        pass
