import pygame as pg
from pygame import Vector2
import math
from settings import *
import random as rand

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
    def __init__(self, game, holder, target, cooldown, img):
        self.groups = game.all_sprites, game.guns
        self.game = game
        self.holder = holder
        self.target = target
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # Set dimensions 

        self.image_orig = img
        self.image = self.image_orig

        self.pivot = Vector2(self.holder.rect.center)
        self.pos = self.pivot + (10, 0)
        self.rect = self.image.get_rect(center=self.pos)

        self.flipped_img = pg.transform.flip(self.image_orig, False, True)
        self.unflipped_img = self.image_orig
        self.alpha = 255

        self.shooting_point = Vector2(0, 0)

        # Shooting
        self.cooldown = cooldown
        self.cool_dur = 0

        self.enabled = True
        self.disabledLifetime = 5

    def update(self):
        if self.enabled:
            # Stick to player
            self.pivot = Vector2(self.holder.rect.center)
            self.pos = self.pivot + (10, 0)

            if self.target == 'Mouse': self.rotate(Vector2(pg.mouse.get_pos()))
            else: self.rotate(self.target.center)

            # Cooldown
            if self.cool_dur > 0:
                self.cool_dur -= 2 * self.game.dt
        else:
            if self.disabledLifetime <= 0:
                self.fade()
            else:
                self.disabledLifetime -= self.game.dt

    def rotate(self, target):
        offset = Vector2(target) - self.pivot
        angle = -math.degrees(math.atan2(offset.y, offset.x))

        if target[0] < self.pivot.x:
            self.image_orig = self.flipped_img
        else: 
            self.image_orig = self.unflipped_img
        self.shooting_point = self.pivot + (0, -12) + Vector2(self.rect.width*0.9, 0).rotate(-(angle+15))
        self.image, self.rect = rotate_img_on_pivot(self.image_orig, angle, Vector2(self.pivot), Vector2(self.pos[0], self.pos[1]-5))
        
    def shoot(self):
        if self.cool_dur <= 0:
            if self.target == 'Mouse': 
                target = Vector2(pg.mouse.get_pos())
            else: target = self.target.center

            offset = target - self.shooting_point
            angle = -math.degrees(math.atan2(offset.y, offset.x))
            Bullet(self.game, *self.shooting_point, angle, self.holder)

            self.cool_dur = self.cooldown
    
    def fade(self):
        self.alpha = max(0, self.alpha-2)  # alpha should never be < 0.
        self.image = self.image.copy()
        self.image.fill((255, 255, 255, self.alpha), special_flags=pg.BLEND_RGBA_MULT)
        if self.alpha <= 0:  # Kill the sprite when the alpha is <= 0.
            self.kill() 

class Pistol(Gun):
    def __init__(self, game, holder, target, cooldown):
        self.image = pg.transform.scale(pg.image.load('./assets/pistol.png').convert_alpha(), (35, 25))
        super().__init__(game, holder, target, cooldown, self.image)


# Bullet Sprites
class Bullet(pg.sprite.Sprite):
    def __init__(self, game, x, y, angle, shooter):
        self.groups = game.all_sprites, game.bullets
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # set game class
        self.game = game
        # Set dimensions 
        self.image = pg.image.load('./assets/bullet.png')

        self.rect = self.image.get_rect(topleft=(x, y))
        self.x = x
        self.y = y

        self.shooter = shooter

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
            if hits[0].__class__.__name__ == "Mob" and not self.shooter.__class__.__name__ == "Mob":
                hits[0].kill()
                hits[0].weapon.enabled = False
                self.kill()
            elif hits[0].__class__.__name__ == "Player" and self.shooter.__class__.__name__ == "Mob":
                hits[0].hitpoints -= 20
                print(hits[0].hitpoints)
                self.kill()
            elif hits[0].__class__.__name__ == 'Wall':
                self.kill()