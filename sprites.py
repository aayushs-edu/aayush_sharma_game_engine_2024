# This file was created by: Aayush Sharma
# This code was inspired by Zelda and informed by Chris Bradfield

# Import libraries/settings
import pygame as pg
from settings import *
from pygame import Vector2
import random as rand
import os
from weapons import *
from particles import *
from mobs import *

# List of buttons to switch weapons
loadoutButtons = [pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5]

# Player Sprite -- inherits from pygame Sprite class
class Player(pg.sprite.Sprite):
    # Init Player
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.player, game.active_sprites
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # set game class
        self.game = game
        # Set dimensions 
        self.image = pg.Surface((TILESIZE, TILESIZE))
        # Give color
        self.image.fill(GREEN)
        self.color = GREEN
        # Rectangular area of player
        self.rect = self.image.get_rect()

        self.speed = 300
        self.max_hitpoints = 100000000000
        self.hitpoints = self.max_hitpoints
        self.dashing = False
        self.dashLeft = 0.1
        self.dashCooldown = 1
        self.dashCoolLeft = 0

        self.vx, vy = 0, 0
        self.x = x * TILESIZE
        self.y = y * TILESIZE

        self.moneybag = 0
        # Loadout as a list of weapons
        self.loadout : list[Gun] = [
            Pistol(self.game, self, 'Mouse', PISTOL_COOLDOWN), 
            Shotgun(self.game, self, 'Mouse', SHOTGUN_COOLDOWN), 
            Rifle(self.game, self, 'Mouse', RIFLE_COOLDOWN), 
            Sniper(self.game, self, 'Mouse', SNIPER_COOLDOWN)
        ]
        self.activeWeapon = self.loadout[0]
        self.activeWeapon.enabled = True

        self.powerups = []
        self.powered_up = False

        

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
    
    # Function to handle collision with walls
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
    def collide_with_group(self, group):
        hits = pg.sprite.spritecollide(self, group, False)
        if hits:
            if hits[0].__class__.__name__ == "Coin" and hits[0].collectable:
                self.moneybag += 1
                hits[0].kill()
            if hits[0].__class__.__name__ == 'Speed' and hits[0].collectable:
                if not hits[0].enabled:
                    print('POWERED UP')
                    hits[0].enable()
                    self.powerups.append(hits[0])
            if hits[0].__class__.__name__ == 'Health' and hits[0].collectable:
                if not hits[0].enabled:
                    hits[0].enable()
            if hits[0].__class__.__name__ == 'Mob' and self.dashing:
                hits[0].die()
            if hits[0].__class__.__bases__[0].__name__ == 'Gun' and hits[0] not in self.loadout:
                if hits[0].dead:
                    print('Pickup')
                    self.pickupWeapon = hits[0]
        else: self.pickupWeapon = None

    def update(self):
        # Handle powerups
        if self.powerups:
            self.powered_up = True
            for p in self.powerups:
                if p.forever:
                    self.powerups.remove(p)
                    continue
                if p.dur <= 0:
                    p.disable()
                    self.powerups.remove(p)
        else: self.powered_up = False

        # Handle dashing
        if self.dashing:
            pg.display.flip()
            Particle(self.game, self.x, self.y, TILESIZE, 0, 0, 0.2, GREEN, randSize=False, decay=False, fade=True)
            self.dashLeft -= self.game.dt
            if self.dashLeft <= 0:
                self.dashing = False
                self.dashLeft = 0.2
        else:
            self.dashCoolLeft -= self.game.dt

        # Visual indication of powerup
        if self.powered_up:
            self.image.fill(YELLOW)
            Particle(self.game, self.x, self.y, TILESIZE, 0, 0, 0.2, YELLOW, randSize=False, decay=False, fade=True)
        else:
            self.image.fill(GREEN)

        self.get_keys()
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.rect.x = self.x
        # Add collision later
        self.collide_with_walls('x')
        self.rect.y = self.y
        # Add collision later
        self.collide_with_walls('y')
        self.collide_with_group(self.game.coins)
        self.collide_with_group(self.game.powerups)
        self.collide_with_group(self.game.mobs)
        self.collide_with_group(self.game.guns)
        if self.hitpoints <= 0:
            self.game.playing = False
            print('dead')

    def get_keys(self):
        self.vx, self.vy = 0, 0
        clicks = pg.mouse.get_pressed()
        keys = pg.key.get_pressed()
        if clicks[0]:
            self.activeWeapon.shoot(ORANGE)
        # Drop weapon
        if keys[pg.K_q]:
            if self.activeWeapon in self.loadout: self.loadout.remove(self.activeWeapon)
            self.activeWeapon.dead=True
        # Pickup weapon
        if keys[pg.K_z] and self.pickupWeapon and len(self.loadout) < 5:
            self.activeWeapon.enabled = False
            self.pickupWeapon.dead = False
            self.pickupWeapon.holder = self
            self.pickupWeapon.target = 'Mouse'
            self.pickupWeapon.cooldown = PISTOL_COOLDOWN
            self.loadout.append(self.pickupWeapon)
            self.activeWeapon = self.loadout[-1]
            self.activeWeapon.enabled = True
            self.pickupWeapon = None
        # Spawn mobs
        if keys[pg.K_r]:
            Troop(self.game, self, 3, 3)
            print('Spawned mob')
        # Dash
        if keys[pg.K_SPACE] and not self.dashing and not self.powered_up and self.dashCoolLeft <= 0:
            print('DASH')
            self.dashing = True
            self.dashCoolLeft = self.dashCooldown
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            # Make speed faster when dashing
            self.vx = -self.speed * (self.dashing*2 + 1)
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vx = self.speed * (self.dashing*2 + 1)
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vy = -self.speed * (self.dashing*2 + 1)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vy = self.speed * (self.dashing*2 + 1)

        # SWITCH WEAPONS -- number buttons map to weapons
        for key in loadoutButtons:
            idx = loadoutButtons.index(key)
            if keys[key] and idx < len(self.loadout):
                if self.activeWeapon is not self.loadout[idx]:
                    self.activeWeapon.enabled = False
                    self.activeWeapon = self.loadout[idx]
                    self.activeWeapon.enabled = True
                    pg.mixer.Sound.play(self.game.gun_cock)
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
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
    
    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y

# Coin Sprites
class Coin(pg.sprite.Sprite):
    def __init__(self, game, x, y, delay):
        self.groups = game.all_sprites, game.coins, game.active_sprites
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # set game class
        self.game = game
        # Set dimensions 
        self.frame = 0
        self.frameDelay = 0.1
        # Coin frames
        self.coin_images = os.listdir('./assets/coin/')
        self.image = pg.transform.scale(pg.image.load(f'./assets/coin/{self.coin_images[0]}'), (TILESIZE, TILESIZE))
        # Rectangular area of wall
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        self.delay = delay
        self.collectable = False
    
    def update(self):
        # ANIMATION -- loop through frames
        if self.frameDelay <= 0:
            self.frame = (self.frame + 1) % 5
            self.image = pg.transform.scale(pg.image.load(f'./assets/coin/{self.coin_images[self.frame]}'), (TILESIZE, TILESIZE))
            self.frameDelay = 0.1
        # For lootbox -- only make collectable when it goes to intended spot
        if (self.rect.x, self.rect.y) != (self.x, self.y):
                self.rect.x += (self.x - self.rect.x) * (1 if self.collectable else 0.2)
                self.rect.y += (self.y - self.rect.y) * (1 if self.collectable else 0.2)
        # Delay for collectability
        self.delay = max(0, self.delay - self.game.dt)
        if self.delay <= 0:
            self.collectable = True
        self.frameDelay -= self.game.dt

class PowerUp(pg.sprite.Sprite):
    def __init__(self, game, x, y, delay, dur, img):
        self.groups = game.all_sprites, game.powerups, game.active_sprites
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # set game class
        self.game = game
        # Set dimensions 
        # Rectangular area of wall
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.image = img
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        self.delay = delay
        self.collectable = False
        self.dur = dur
        self.forever = True if dur < 0 else False
        self.enabled = False
    
    def update(self):
        if self.enabled:
            self.dur -= self.game.dt
        # For lootbox -- only make collectable when it goes to intended spot
        if (self.rect.x, self.rect.y) != (self.x, self.y):
                self.rect.x += (self.x - self.rect.x) * (1 if self.collectable else 0.2)
                self.rect.y += (self.y - self.rect.y) * (1 if self.collectable else 0.2)
        # Delay for collectability
        self.delay = max(0, self.delay - self.game.dt)
        if self.delay <= 0:
            self.collectable = True
    
    def enable(self):
        self.enabled = True
        self.effect()
        self.image.fill((255, 255, 255, 0), special_flags=pg.BLEND_RGBA_MULT)

class Speed(PowerUp):
    def __init__(self, game, x, y, delay):
        
        # Set dimensions 
        self.image = pg.transform.scale(pg.image.load('./assets/lightning.png'), (TILESIZE, TILESIZE))
        super().__init__(game, x, y, delay, 5, self.image)

    # Effect of powerup
    def effect(self):
        self.game.player1.speed += 100
    
    # DIsable powerup
    def disable(self):
        print('done')
        self.game.player1.speed -= 100
        self.kill()

# Inherits from PowerUp
class Health(PowerUp):
    def __init__(self, game, x, y, delay):
        
        # Set dimensions 
        self.image = pg.transform.scale(pg.image.load('./assets/potions/health1.png'), (TILESIZE, TILESIZE))
        super().__init__(game, x, y, delay, -1, self.image)

    def effect(self):
        print('HEALTH')
        # Give player 20 health, max 100
        self.game.player1.hitpoints = min(100, self.game.player1.hitpoints + 20)
        self.kill()
                
class Lootbox(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.active_sprites
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # set game class
        self.game = game
        # Set dimensions
        self.image = pg.transform.scale(pg.image.load('./assets/chest/chest1.png'), (TILESIZE*2.5, TILESIZE*2.5))
        # Give color
        # Rectangular area of wall
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE - self.image.get_width()/2
        self.rect.y = y * TILESIZE - self.image.get_height()/2
        self.alpha = 255
        self.fading = False

        # Possible items
        self.items = ['Coin', 'PowerUp', 'Health']

    # Input parameter is whether the user is pressing E or not (True or False)
    def checkNearby(self):
        # Check if player is in proximity
        hits = pg.sprite.spritecollide(self, self.game.player, False)
        if hits:
            keys = pg.key.get_pressed()
            if keys[pg.K_e]:
                self.image = pg.transform.scale(pg.image.load('./assets/chest/chest11.png'), (TILESIZE*2.5, TILESIZE*2.5))
                self.open()
                self.fading = True
            

    def fade(self):
        self.alpha = max(0, self.alpha-2)  # alpha should never be < 0.
        self.image = self.image.copy()
        self.image.fill((255, 255, 255, self.alpha), special_flags=pg.BLEND_RGBA_MULT)
        if self.alpha <= 0:  # Kill the sprite when the alpha is <= 0.
            self.kill()  

    def open(self):
        # Choose random items
        items = rand.choices(self.items, k=2)
        print(items)
        for item in items:
            # Throw item in random direction
            vec = pg.Vector2(TILESIZE, TILESIZE).rotate(rand.random() * 360)
            # Instantiate item based on choice
            if item == 'Coin': 
                coin = Coin(self.game, self.x, self.y, 1)      
                coin.x += vec[0]
                coin.y += vec[1]
            elif item == 'PowerUp': 
                powerup = Speed(self.game, self.x, self.y, 1)
                powerup.x -= vec[0]
                powerup.y -= vec[1]
            elif item == 'Health': 
                powerup = Health(self.game, self.x, self.y, 1)
                powerup.x -= vec[0]
                powerup.y -= vec[1]
            
    
    def update(self):
        if self.fading: self.fade()
        else: self.checkNearby()

