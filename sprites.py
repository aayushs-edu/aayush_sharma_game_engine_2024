# This file was created by: Aayush Sharma
# This code was inspired by Zelda and informed by Chris Bradfield

# Import libraries/settings
import pygame as pg
from settings import *
import math
from pygame import Vector2
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


# Player Sprite -- inherits from pygame Sprite class
class Player(pg.sprite.Sprite):
    # Init Player
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # set game class
        self.game = game
        # Set dimensions 
        self.image = pg.Surface((TILESIZE, TILESIZE))
        # Give color
        self.image.fill(GREEN)
        # Rectangular area of player
        self.rect = self.image.get_rect()

        self.speed = 300
        self.hitpoints = 100

        self.vx, vy = 0, 0
        self.x = x * TILESIZE
        self.y = y * TILESIZE

        self.moneybag = 0
        self.loadout : list[Gun] = [Gun(self.game, self.rect, 'Mouse', PLAYER_COOLDOWN)]

    # Function to move player
    # def move(self, dx=0, dy=0):
    #     if not self.colliding(dx, dy):
    #         self.x += dx
    #         self.y += dy

    # def colliding(self, dx=0, dy=0):
    #     for wall in self.game.walls:
    #         if wall.x == self.x + dx and wall.y == self.y + dy:
    #             return True
    #     return False
        
    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vx > 0:
                    self.x = hits[0].rect.left - self.rect.width
                if self.vx < 0:
                    self.x = hits[0].rect.right
                self.vx = 0
                self.rect.x = self.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vy > 0:
                    self.y = hits[0].rect.top - self.rect.height
                if self.vy < 0:
                    self.y = hits[0].rect.bottom
                self.vy = 0
                self.rect.y = self.y
    
    # Method to collide with any group
    def collide_with_group(self, group, kill):
        hits = pg.sprite.spritecollide(self, group, kill)
        if hits:
            if hits[0].__class__.__name__ == "Coin":
                self.moneybag += 1
            if hits[0].__class__.__name__ == 'PowerUp':
                print('POWERUP')
                self.speed += 50

    def update(self):
        self.get_keys()
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.rect.x = self.x
        # Add collision later
        self.collide_with_walls('x')
        self.rect.y = self.y
        # Add collision later
        self.collide_with_walls('y')
        self.collide_with_group(self.game.coins, True)
        self.collide_with_group(self.game.powerups, True)

    def get_keys(self):
        self.vx, self.vy = 0, 0
        clicks = pg.mouse.get_pressed()
        keys = pg.key.get_pressed()
        if clicks[0]:
            self.loadout[0].shoot()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.vx = -self.speed
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vx = self.speed
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vy = -self.speed
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vy = self.speed
        if self.vx != 0 and self.vy != 0:
            self.vx *= 0.7071
            self.vy *= 0.7071

    


# Walls Sprites
class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # set game class
        self.game = game
        # Set dimensions 
        self.image = pg.Surface((TILESIZE, TILESIZE))
        # Give color
        self.image.fill(GRAY)
        # Rectangular area of wall
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

# Coin Sprites
class Coin(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.coins
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # set game class
        self.game = game
        # Set dimensions 
        self.image = pg.Surface((TILESIZE, TILESIZE))
        # Give color
        self.image.fill(YELLOW)
        # Rectangular area of wall
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

class PowerUp(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.powerups
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # set game class
        self.game = game
        # Set dimensions 
        self.image = pg.Surface((TILESIZE, TILESIZE))
        # Give color
        self.image.fill(BLUE)
        # Rectangular area of wall
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        

class Gun(pg.sprite.Sprite):
    def __init__(self, game, holder, target, cooldown):
        self.groups = game.all_sprites, game.guns
        self.game = game
        self.holder = holder
        self.target = target
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # Set dimensions 

        self.image_orig = pg.transform.scale(pg.image.load('./assets/pistol.png').convert_alpha(), (35, 25))
        self.image = self.image_orig

        self.pivot = Vector2(self.holder.center)
        self.pos = self.pivot + (10, 0)
        self.rect = self.image.get_rect(center=self.pos)

        self.flipped_img = pg.transform.flip(self.image_orig, False, True)
        self.unflipped_img = self.image_orig

        self.shooting_point = Vector2(0, 0)

        # Shooting
        self.cooldown = cooldown
        self.cool_dur = 0

        self.enabled = True

    def update(self):
        if self.enabled:
            # Stick to player
            self.pivot = Vector2(self.holder.center)
            self.pos = self.pivot + (10, 0)

            if self.target == 'Mouse': self.rotate(Vector2(pg.mouse.get_pos()))
            else: self.rotate(self.target.center)

            # Cooldown
            if self.cool_dur > 0:
                self.cool_dur -= 2 * self.game.dt

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
            Bullet(self.game, *self.shooting_point, angle)

            self.cool_dur = self.cooldown

# Bullet Sprites
class Bullet(pg.sprite.Sprite):
    def __init__(self, game, x, y, angle):
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
            if hits[0].__class__.__name__ == "Mob":
                hits[0].kill()
                hits[0].weapon.enabled = False
            elif hits[0].__class__.__name__ == 'Wall':
                self.kill()

class Mob(pg.sprite.Sprite):
    def __init__(self, game, target, x, y):
        self.groups = game.all_sprites, game.mobs
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # set game class
        self.game = game
        self.target = target
        # Set dimensions 
        self.image = pg.Surface((TILESIZE, TILESIZE))
        # Give color
        self.image.fill(RED)
        # Rectangular area of wall
        self.rect = self.image.get_rect()
        self.vx, vy = 0, 0
        self.x = x * TILESIZE
        self.y = y * TILESIZE

        self.speed = 20

        self.weapon = Gun(self.game, self.rect, self.target.rect, MOB_COOLDOWN)

    def update(self):
        self.vx, self.vy = (Vector2(self.target.rect.center) - Vector2(self.x, self.y)) / TILESIZE * self.speed
        
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.rect.x = self.x
        self.collide_with_walls('x')
        self.rect.y = self.y
        self.collide_with_walls('y')

        self.weapon.shoot()

    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vx > 0:
                    self.x = hits[0].rect.left - self.rect.width
                if self.vx < 0:
                    self.x = hits[0].rect.right
                self.vx = 0
                self.rect.x = self.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vy > 0:
                    self.y = hits[0].rect.top - self.rect.height
                if self.vy < 0:
                    self.y = hits[0].rect.bottom
                self.vy = 0
                self.rect.y = self.y
    
class ParticleSplash:
    def __init__(self, screen, x, y, duration):
        self.screen = screen
        self.x = x
        self.y = y
        self.duration = duration
        self.particles = []

    def emit(self):
        if self.particles:
            self.delete_particles()
            for particle in self.particles:
                particle[0][1] += particle[2][0]
                particle[0][0] += particle[2][1]
                particle[1] -= 0.2
                pg.draw.circle(self.screen,pg.Color('White'),particle[0], int(particle[1]))
                print('added particle')

    def add_particles(self):
        radius = 100
        direction_x = rand.randint(-3,3)
        direction_y = rand.randint(-3,3)
        particle_circle = [[self.x,self.y],radius,[direction_x,direction_y]]
        self.particles.append(particle_circle)

    def delete_particles(self):
        particle_copy = [particle for particle in self.particles if particle[1] > 0]
        self.particles = particle_copy

        
