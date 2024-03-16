import pygame as pg

from pygame.sprite import Sprite
from pygame import Vector2

import random as rand

from settings import *
from math import floor

class Particle(Sprite):
    def __init__(self, game, x, y, maxSize, maxDist, maxAngle, dur, color):
        self.groups = game.all_sprites, game.active_sprites, game.particles
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        dim = rand.random() * maxSize
        self.image = pg.Surface((dim, dim))
        self.image.fill(color)
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.target = Vector2(self.x, self.y) + Vector2(rand.random()*maxDist, 0).rotate(rand.randint(-maxAngle, maxAngle))
        self.dur = dur

        self.vx, self.vy = 0, 0
        self.speed = 5

    def update(self):
        if self.dur > 0 and self.image.get_width() > 0:
            self.dur -= self.game.dt

            self.vx, self.vy = (self.target - Vector2(self.x, self.y)) * self.speed
            
            self.x += self.vx * self.game.dt
            self.y += self.vy * self.game.dt
            self.rect.x = self.x
            self.rect.y = self.y
            self.image=pg.transform.scale(self.image, (max(0, self.image.get_width()-self.dur/10), max(0, self.image.get_height()-self.dur/10)))
        else: self.kill()