import pygame as pg
from pygame import Vector2
from settings import *
from weapons import *

class Mob(pg.sprite.Sprite):
    def __init__(self, game, target, x, y, weapon, hitpoints, color, speed):
        self.groups = game.all_sprites, game.mobs, game.active_sprites
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # set game class
        self.game = game
        self.target = target
        # Set dimensions 
        self.image = pg.Surface((TILESIZE, TILESIZE))
        # Give color
        self.image.fill(color)
        self.color = color
        # Rectangular area of wall
        self.vx, self.vy = 0, 0
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect = self.image.get_rect(center=(self.x, self.y))

        self.speed = speed
        self.hitpoints = hitpoints
        match weapon:
            case 'Pistol':
                self.weapon = Pistol(self.game, self, self.target.rect, MOB_COOLDOWN)
            case 'Shotgun':
                self.weapon = Shotgun(self.game, self, self.target.rect, MOB_COOLDOWN)
            case 'Rifle':
                self.weapon = Rifle(self.game, self, self.target.rect, MOB_COOLDOWN)
        self.weapon.enabled = True

    def update(self):
        # Move toward player
        self.vx, self.vy = (Vector2(self.target.rect.center) - Vector2(self.x, self.y)) / TILESIZE * self.speed
        
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.rect.x = self.x
        self.collide_with_walls('x')
        self.rect.y = self.y
        self.collide_with_walls('y')

        # Shoot at player
        self.weapon.shoot(REDORANGE)
        if self.hitpoints <= 0:
            self.weapon.dead = True
            self.kill()

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
    def die(self):
        for _ in range(20):
            Particle(self.game, self.x, self.y, 20, 120, 360, 2, RED)
        self.weapon.dead = True
        self.kill()

class Troop(Mob):
    def __init__(self, game, target, x, y):
        weapon = 'Pistol'
        super().__init__(game, target, x, y, weapon, hitpoints=30, color=RED, speed=5)

class Sentinel(Mob):
    def __init__(self, game, target, x, y):
        weapon = 'Shotgun'
        super().__init__(game, target, x, y, weapon, hitpoints=100, color=BLUE, speed=8)