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
    def __init__(self, game, x, y, maxSize, maxDist, maxAngle, dur, color, randSize=True, decay=True, fade=False, rotation=0):
        # Assigning sprite groups
        self.groups = game.all_sprites, game.active_sprites, game.particles
        # Initializing superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.color = color

        self.rotate = bool(rotation)
        self.rot = rotation

        # Generating random particle dimensions and color
        if randSize:
            dim = rand.random() * maxSize
        else:
            dim = maxSize
        
        if not self.rotate:
            self.image = pg.transform.scale(pg.image.load('./assets/particle.png'), (dim, dim))
            self.image.fill(color)
        else:
            if color == RED:
                self.image = pg.transform.scale(pg.image.load('./assets/red.png'), (dim, dim))
            elif color == ORANGE:
                self.image = pg.transform.scale(pg.image.load('./assets/orange.png'), (dim, dim))
            elif color == YELLOW:
                self.image = pg.transform.scale(pg.image.load('./assets/yellow.png'), (dim, dim))
            else:
                self.image = pg.transform.scale(pg.image.load('./assets/particle.png'), (dim, dim))
            self.image = pg.transform.rotate(self.image, self.rot)

        self.fade = fade
        self.decay = decay
        self.x = x
        self.y = y
        self.rect = self.image.get_rect()
        

        # Setting particle target position
        self.target = Vector2(self.x, self.y) + Vector2(rand.random()*maxDist*10, 0).rotate(rand.randint(-maxAngle, maxAngle))
        # Setting particle duration
        self.max_dur = dur
        self.dur = self.max_dur

        # Initializing velocity components
        self.vx, self.vy = 0, 0
        # Setting particle speed
        self.norm_speed = 1
        self.speed = self.norm_speed

        

    # Update method
    def update(self):
        # If particle still exists and has non-zero dimensions
        if self.dur > 0 and self.image.get_width() > 0:
            if self.fade:
                self.image.set_alpha(self.dur/self.max_dur*255)
            # Decrease particle duration based on delta time
            self.dur -= self.game.dt

            # Calculate velocity components towards target
            self.vx, self.vy = (self.target - Vector2(self.x, self.y)) * self.speed
            
            # Update particle position
            self.x += (self.vx) * self.game.dt / 10
            self.y += (self.vy) * self.game.dt / 10
            self.rect.x = self.x
            self.rect.y = self.y

            self.new_image = self.image.copy()

            # Scale down particle size over time
            if self.decay:
                self.new_image=pg.transform.scale(self.new_image, (max(0, self.new_image.get_width()-self.dur/(50 + 10*self.game.slowmo)), 
                                                    max(0, self.new_image.get_height()-self.dur/(50 + 10*self.game.slowmo))))

            # if self.rotate:
            #     self.new_image = pg.transform.rotate(self.new_image, self.rot)
            #     self.rect = self.new_image.get_rect(center=self.rect.center)

            self.image = self.new_image

            # self.image.fill(self.color)

            
        else:
            # Kill the particle if duration is over
            self.kill()
