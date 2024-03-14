import pygame as pg
from pygame import Vector2
import math
from settings import *
import random as rand
from particles import *
import numpy as np

# Rotate function to be used for guns
def rotate_img_on_pivot(img, angle, pivot, origin):
    surf = pg.transform.rotate(img, angle)

    offset = pivot + (origin - pivot).rotate(-angle)
    rect = surf.get_rect(center = offset)

    return surf, rect

def rotate_point_on_pivot(angle, pivot, origin):
    new_pt = pivot + (origin - pivot).rotate(-angle)
    return new_pt

class Gun(pg.sprite.Sprite):
    def __init__(self, game, holder, target, cooldown, img, sound):
        self.groups = game.all_sprites, game.guns
        self.game = game
        self.holder = holder
        self.target = target
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # Set dimensions 

        self.img_overlay = img
        self.image_orig = img
        self.image = self.image_orig

        self.pivot = Vector2(self.holder.rect.center)
        self.pos = self.pivot + (20, 0)
        self.rect = self.image.get_rect(center=self.pos)

        self.alpha = 255

        self.shooting_point = Vector2(0, 0)

        # Shooting
        self.cooldown = cooldown
        self.cool_dur = 0

        self.enabled = False
        self.dead = False
        self.disabledLifetime = 5

        self.flipped = False
        self.angle = 0

        self.sound = sound
        pg.mixer.Sound.play(self.game.gun_cock)

    def update(self):
        if self.dead:
            if self.disabledLifetime <= 0:
                self.fade()
            else:
                self.disabledLifetime -= self.game.dt
        else:
            if not self.enabled:
                self.image = self.image.copy()
                self.image.fill((255, 255, 255, 0), special_flags=pg.BLEND_RGBA_MULT)
            else:
                self.image = self.image_orig
                # Stick to player
                self.pivot = Vector2(self.holder.rect.center)
                self.pos = self.pivot + (20, 0)

                if self.target == 'Mouse': self.rotate(Vector2(pg.mouse.get_pos()))
                else: self.rotate(self.target.center)

                # Cooldown
                if self.cool_dur > 0:
                    self.cool_dur -= 2 * self.game.dt
            

    def rotate(self, target):
        offset = Vector2(target) - self.pivot
        self.angle = -math.degrees(math.atan2(offset.y, offset.x))

        if target[0] < self.pivot.x and not self.flipped:
            self.flipped = True
            self.image_orig = pg.transform.flip(self.image_orig, False, True)
        elif target[0] > self.pivot.x and self.flipped: 
            self.flipped = False
            self.image_orig = pg.transform.flip(self.image_orig, False, True)
        self.shooting_point = rotate_point_on_pivot(self.angle, Vector2(self.pivot), self.pivot + (max(self.image.get_width(), self.image.get_height()), -5 * (-1 if self.flipped else 1)))
        pg.draw.line(self.game.screen, (255, 0, 0), (self.pivot.x, self.pivot.y), (self.shooting_point.x, self.shooting_point.y))
        pg.display.flip()
        self.image, self.rect = rotate_img_on_pivot(self.image_orig, self.angle, Vector2(self.pivot), Vector2(self.pos))
        
    def shoot(self, color):
        if self.cool_dur <= 0:
            Bullet(self.game, *self.shooting_point, self.angle, self.holder, color)

            # recoil (TODO)
            
            pDir = -1 if self.flipped else 1
            for _ in range(5):
                Particle(self.game, *self.shooting_point, 15, 100*pDir, 40, 5, color)

            self.cool_dur = self.cooldown
            pg.mixer.Sound.play(self.sound)
    
    def fade(self):
        self.alpha = max(0, self.alpha-2)  # alpha should never be < 0.
        self.image = self.image.copy()
        self.image.fill((255, 255, 255, self.alpha), special_flags=pg.BLEND_RGBA_MULT)
        if self.alpha <= 0:  # Kill the sprite when the alpha is <= 0.
            self.kill() 

class Pistol(Gun):
    def __init__(self, game, holder, target, cooldown):
        self.image = pg.transform.scale(pg.image.load('./assets/pistol.png').convert_alpha(), (35, 25))
        sound = game.pistol_shot
        super().__init__(game, holder, target, cooldown, self.image, sound)

class Shotgun(Gun):
    def __init__(self, game, holder, target, cooldown):
        self.image = pg.transform.scale(pg.image.load('./assets/shotgun.png').convert_alpha(), (44, 16))
        sound = game.shotgun_shot
        super().__init__(game, holder, target, cooldown, self.image, sound)
    
    def shoot(self, color):
        if self.cool_dur <= 0:
            for angle in np.random.normal(loc=self.angle, scale=10.0, size=5):
                Bullet(self.game, *self.shooting_point, angle, self.holder, color) 

            pDir = -1 if self.flipped else 1
            for _ in range(5):
                Particle(self.game, *self.shooting_point, 15, 100*pDir, 40, 5, color)

            self.cool_dur = self.cooldown

            pg.mixer.Sound.play(self.sound)


# Bullet Sprites
class Bullet(pg.sprite.Sprite):
    def __init__(self, game, x, y, angle, shooter, color):
        self.groups = game.all_sprites, game.bullets
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # set game class
        self.game = game
        # Set dimensions 
        # self.image = pg.transform.rotozoom(pg.image.load('./assets/bullet1.png'), angle+45, 2)
        self.image = pg.Surface((10, 10))
        self.image.fill(color)

        self.rect = self.image.get_rect(center=(x, y))
        self.x = x
        self.y = y

        self.shooter = shooter
        self.color = color

        self.angle = angle
        self.speed = 20

        self.vx = math.cos(self.angle * math.pi/180) * self.speed
        self.vy = math.sin(self.angle * math.pi/180) * self.speed
    
    def update(self):
        self.x += self.vx
        self.y -= self.vy

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        self.collide()

    def collide(self):
        hits = pg.sprite.spritecollide(self, self.game.all_sprites, False)
        if hits:
            for _ in range(10):
                Particle(self.game, self.x, self.y, 10, 60, 360, 1, self.color)

            if hits[0].__class__.__name__ == "Mob" and not self.shooter.__class__.__name__ == "Mob":
                for _ in range(10):
                    Particle(self.game, self.x, self.y, 20, 120, 360, 1, RED)
                hits[0].kill()
                hits[0].weapon.dead = True
                self.kill()
            elif hits[0].__class__.__name__ == "Player" and self.shooter.__class__.__name__ == "Mob":
                for _ in range(10):
                    Particle(self.game, self.x, self.y, 20, 120, 360, 1, GREEN)
                hits[0].hitpoints -= 20
                print(hits[0].hitpoints)
                self.kill()
            elif hits[0].__class__.__name__ == 'Wall':
                self.kill()
                for _ in range(10):
                    Particle(self.game, self.x, self.y, 12, 80, 360, 1, YELLOW)