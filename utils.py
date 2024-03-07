# this 'cooldown' class is designed to help us control time
import pygame as pg

from math import floor

class Timer():
    # sets all properties to zero when instantiated...
    def __init__(self, game):
        self.game = game
        self.current_time = 0
        self.event_time = 0
        self.cd = 0
        # ticking ensures the timer is counting...
    # must use ticking to count up or down
    def ticking(self):
        self.current_time = floor((pg.time.get_ticks())/1000)
        if self.cd > 0:
            self.countdown()
    # resets event time to zero - cooldown reset
    def get_countdown(self):
        return floor(self.cd)
    def countdown(self):
        if self.cd > 0:
            self.cd = self.cd - self.game.dt
    def event_reset(self):
        self.event_time = floor((pg.time.get_ticks())/1000)
    # sets current time
    def get_current_time(self):
        self.current_time = floor((pg.time.get_ticks())/1000)