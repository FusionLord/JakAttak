
import pygame

##################################

class Cutscene():
    def __init__(self, main):
        self.main = main

        self.alive = True
        self.pausable = True

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

    def is_alive(self):
        return self.alive

    def kill(self, force = [0,0]):
        self.alive = False
        self.cleanup()


    def update(self):
        pass

    def move(self):
        pass

    def render(self):
        pass
