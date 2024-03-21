# Importing necessary modules
import pygame as pg
from pygame.sprite import Sprite
from pygame import Vector2
import random as rand
from settings import *
from math import floor

# Defining the Particle class
class Particle(Sprite):
    # Constructor method
    def __init__(self, game, x, y, maxSize, maxDist, maxAngle, dur, color):
        # Assigning sprite groups
        self.groups = game.all_sprites, game.active_sprites, game.particles
        # Initializing superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        # Generating random particle dimensions and color
        dim = rand.random() * maxSize
        self.image = pg.Surface((dim, dim))
        self.image.fill(color)
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(center=(self.x, self.y))

        # Setting particle target position
        self.target = Vector2(self.x, self.y) + Vector2(rand.random()*maxDist, 0).rotate(rand.randint(-maxAngle, maxAngle))
        # Setting particle duration
        self.dur = dur

        # Initializing velocity components
        self.vx, self.vy = 0, 0
        # Setting particle speed
        self.speed = 5

    # Update method
    def update(self):
        # If particle still exists and has non-zero dimensions
        if self.dur > 0 and self.image.get_width() > 0:
            # Decrease particle duration based on delta time
            self.dur -= self.game.dt

            # Calculate velocity components towards target
            self.vx, self.vy = (self.target - Vector2(self.x, self.y)) * self.speed
            
            # Update particle position
            self.x += self.vx * self.game.dt
            self.y += self.vy * self.game.dt
            self.rect.x = self.x
            self.rect.y = self.y

            # Scale down particle size over time
            self.image=pg.transform.scale(self.image, (max(0, self.image.get_width()-self.dur/10), 
                                                       max(0, self.image.get_height()-self.dur/10)))
        else:
            # Kill the particle if duration is over
            self.kill()
