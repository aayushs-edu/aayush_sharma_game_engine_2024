# This file was created by: Aayush Sharma
# This code was inspired by Zelda and informed by Chris Bradfield

# Import libraries/settings
import pygame as pg
from settings import *
from pygame import Vector2
import random as rand
from os import path
import os
from weapons import *
from particles import *
from mobs import *

# List of buttons to switch weapons
loadoutButtons = [pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5]
img_folder = path.join(path.dirname(__file__), 'assets')

class Spritesheet:
    # utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # grab an image out of a larger spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        # image = pg.transform.scale(image, (width, height))
        image = pg.transform.scale(image, (width, height))
        return image

# Player Sprite -- inherits from pygame Sprite class
class Player(pg.sprite.Sprite):
    # Init Player
    def __init__(self, game, x, y, color, controllable=True):
        
        self.groups = game.all_sprites, game.player, game.active_sprites
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # set game class
        self.game = game
        # Set dimensions 
        self.image = pg.Surface((TILESIZE, TILESIZE))
        # Give color
        self.image.fill(color)
        self.color = color
        # Rectangular area of player
        self.rect = self.image.get_rect()

        self.norm_speed = 300
        self.speed = self.norm_speed
        self.max_hitpoints = 1000
        self.hitpoints = self.max_hitpoints
        self.dashing = False
        self.dashLeft = 0.1
        self.dashCooldown = 1
        self.dashCoolLeft = 0

        self.controllable = controllable

        self.vx, self.vy = 0, 0
        self.x = x * TILESIZE
        self.y = y * TILESIZE

        self.moneybag = 0
        # Loadout as a list of weapons
        self.loadout : list[Gun] = [
            Pistol(self.game, self, 'Mouse' if self.controllable else 'Idle', PISTOL_COOLDOWN)
        ]
        self.explosives : list[Grenade] = [
            Grenade(self.game, self, 300, 150),
            Grenade(self.game, self, 300, 150),
            Grenade(self.game, self, 300, 150),
            Grenade(self.game, self, 300, 150),
        ]
        self.grenade_mode = False
        self.activeWeapon = self.loadout[0]
        self.activeWeapon.enabled = True
        self.prevWeapon = self.activeWeapon

        self.powerups = []
        self.powered_up = False

        self.current_frame = 0
        self.last_update = 0
    
    def get_data(self) -> dict:
        return {
            'x': self.x,
            'y': self.y,
            'hitpoints': self.hitpoints,
            'moneybag': self.moneybag,
            'powerups': self.powerups,
            'powered_up': self.powered_up,
            'weapon' : self.activeWeapon.get_data(),
            # 'loadout': self.loadout,
            # 'explosives': self.explosives,	
            # 'activeWeapon': self.activeWeapon,
            # 'prevWeapon': self.prevWeapon,
            'grenade_mode': self.grenade_mode
        }   
    
    def load_data(self, data : dict):
        if data.__class__.__name__ != 'dict': return
        self.x = data.get('x')
        self.y = data.get('y')
        self.hitpoints = data.get('hitpoints')
        self.moneybag = data.get('moneybag')
        self.powerups = data.get('powerups')
        self.powered_up = data.get('powered_up')
        self.activeWeapon.load_data(data.get('weapon'))
        # self.loadout = data.get('loadout')
        # self.explosives = data.get('explosives')
        # self.activeWeapon = data.get('activeWeapon')
        # self.prevWeapon = data.get('prevWeapon')
        self.grenade_mode = data.get('grenade_mode')
    
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
            if hits[0].__class__.__bases__[0].__name__ == 'PowerUp' and hits[0].collectable:
                if not hits[0].enabled:
                    print('POWERED UP')
                    hits[0].enable()
                    self.powerups.append(hits[0])
            if hits[0].__class__.__name__ == 'Mob' and self.dashing:
                hits[0].die()
            if hits[0].__class__.__bases__[0].__name__ == 'Gun' and hits[0] not in self.loadout:
                if hits[0].dead:
                    print('Pickup')
                    self.pickupWeapon = hits[0]
        else: self.pickupWeapon = None

    def update(self):
        if self.game.shop.open_shop: return
        # Handle powerups
        if self.powerups:
            self.image.fill(YELLOW)
            if self.powerups[0].__class__.__name__ == 'Speed': Particle(self.game, self.x, self.y, TILESIZE, 0, 0, 0.2, YELLOW, randSize=False, decay=False, fade=True)
            self.powered_up = True
            for p in self.powerups:
                print(p.__class__.__name__)
                if p.forever:
                    self.powerups.remove(p)
                    continue
                if p.dur <= 0:
                    p.disable()
                    self.powerups.remove(p)
        else:
            self.image.fill(GREEN)
            self.powered_up = False

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
        # if self.powered_up:
        #     self.image.fill(YELLOW)
        #     Particle(self.game, self.x, self.y, TILESIZE, 0, 0, 0.2, YELLOW, randSize=False, decay=False, fade=True)
        # else:
        #     self.image.fill(GREEN)

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
        if keys[pg.K_f]:
            self.game.rot = 5
        if clicks[0] and self.controllable:
            if self.grenade_mode:
                if hasattr(self.prevWeapon, 'detonating'):
                    if not self.prevWeapon.detonating:
                        self.activeWeapon.shoot(ORANGE)
                        self.activeWeapon.enabled = False
                        self.prevWeapon = self.explosives.pop(0)
                        if self.explosives:
                            self.activeWeapon = self.explosives[0]
                        else:
                            self.grenade_mode = False
                            self.activeWeapon = self.loadout[0]
                        self.activeWeapon.enabled = True
                else:
                    self.activeWeapon.shoot(ORANGE)
                    self.activeWeapon.enabled = False
                    self.prevWeapon = self.explosives.pop(0)
                    if self.explosives:
                        self.activeWeapon = self.explosives[0]
                    else:
                        self.grenade_mode = False
                        self.activeWeapon = self.loadout[0]
                    self.activeWeapon.enabled = True
            else:
                if self.controllable:
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
        # Grenade
        if keys[pg.K_LSHIFT] and not self.grenade_mode and self.explosives:
            self.grenade_mode = True
            self.prevWeapon = self.activeWeapon
            self.activeWeapon.enabled = False
            self.activeWeapon = self.explosives[0]
            self.activeWeapon.enabled = True
        
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
                    if self.activeWeapon.__class__.__name__ == 'Sniper':
                        self.game.camera.zoom_scale = 0.9
                    else:
                        self.game.camera.zoom_scale = 1
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

class Slowmo(PowerUp):
    def __init__(self, game, x, y, delay):
        # Set dimensions 
        self.image = pg.transform.scale(pg.image.load('./assets/clock.png'), (TILESIZE*1.5, TILESIZE*1.5))
        super().__init__(game, x, y, delay, 5, self.image)

    # Effect of powerup
    def effect(self):
        if not self.game.slowmo:
            self.game.camera.zoom_scale = 1.6
            self.game.slowmo = True
            for sprite in self.game.active_sprites.sprites():
                if hasattr(sprite, 'speed'):
                    sprite.speed /= 2
    
    # Disable powerup
    def disable(self):
        self.kill()
        print('done')
        self.game.camera.zoom_scale = 1
        self.game.slowmo = False
        for sprite in self.game.active_sprites.sprites():
            if hasattr(sprite, 'speed'):
                sprite.speed = sprite.norm_speed
        

# Inherits from PowerUp
class Health(PowerUp):
    def __init__(self, game, x, y, delay):
        
        # Set dimensions 
        self.image = pg.transform.scale(pg.image.load('./assets/potions/health1.png'), (TILESIZE, TILESIZE))
        super().__init__(game, x, y, delay, -1, self.image)

    def effect(self):
        print('HEALTH')
        # Give player 20 health, max 100
        self.game.player1.hitpoints = min(self.game.player1.max_hitpoints, self.game.player1.hitpoints + 20)
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

class Shop(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.active_sprites
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # set game class
        self.game = game
        # Set dimensions
        self.image = pg.transform.scale(pg.image.load('./assets/shop.png'), (TILESIZE*1.5, TILESIZE*1.5))

        # Background
        self.bg_image = pg.transform.scale(pg.image.load('./assets/shop_bg.jpg'), (TILESIZE*4, TILESIZE*4))
        self.bg_rect = self.bg_image.get_rect()
        self.bg_width = self.bg_image.get_width()
        self.bg_height = self.bg_image.get_height()
        self.bg_loc = -HEIGHT

        # Decorations
        self.board_img = pg.transform.scale(pg.image.load('./assets/shop_board.png'), (TILESIZE*6, TILESIZE*5))
        self.button_img = pg.transform.scale(pg.image.load('./assets/button.png'), (TILESIZE*3.5, TILESIZE*3.5))

        # Rectangular area of wall
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.open_shop = False

        self.margin = 300
        self.shop_items = [
            ['pistol', 1, ShopButton(self.game, 0, 0, self.button_img, Pistol(self.game, self.game.player1, 'Mouse', PISTOL_COOLDOWN), 1)],
            ['shotgun', 5, ShopButton(self.game, 0, 0, self.button_img, Shotgun(self.game, self.game.player1, 'Mouse', SHOTGUN_COOLDOWN), 5)],
            ['rifle', 15, ShopButton(self.game, 0, 0, self.button_img, Rifle(self.game, self.game.player1, 'Mouse', RIFLE_COOLDOWN), 15)],
            ['sniper', 30, ShopButton(self.game, 0, 0, self.button_img, Sniper(self.game, self.game.player1, 'Mouse', SNIPER_COOLDOWN), 30)],
            ['rocket-launcher', 100, ShopButton(self.game, 0, 0, self.button_img, RocketLauncher(self.game, self.game.player1, 'Mouse', SHOTGUN_COOLDOWN), 100)]
        ]

    # Input parameter is whether the user is pressing E or not (True or False)
    def checkNearby(self):
        # Check if player is in proximity
        hits = pg.sprite.spritecollide(self, self.game.player, False)
        if hits:
            keys = pg.key.get_pressed()
            if keys[pg.K_e]:
                self.open_shop = True


    def open(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE]:
            self.game.screen.fill(BGCOLOR)
            self.open_shop = False

        self.draw_bg_tiles(self.bg_loc)
        self.game.screen.blit(self.board_img, (WIDTH-self.board_img.get_width(), 10 + self.bg_loc))
        idx = 0
        for i in range(self.margin, WIDTH-self.margin, 200):
            for j in range(200, HEIGHT-200, 200):
                # Wooden frame
                frame = pg.draw.rect(self.game.screen, (240, 152, 70), (i, j + self.bg_loc, 100, 100), 8)

                # Weapon img
                if idx < len(self.shop_items):
                    curr_weapon = self.shop_items[idx][0]
                    weapon = pg.image.load(f'assets/{curr_weapon}.png')
                    weapon_img = pg.transform.rotate(pg.transform.scale(weapon, Vector2(weapon.get_width(), weapon.get_height()).normalize() * 80), 40)
                    weapon_rect = weapon_img.get_rect(center=frame.center)
                    self.game.screen.blit(weapon_img, weapon_rect)

                    # Button
                    self.shop_items[idx][2].draw(frame.centerx - 55, frame.centery + 30 + self.bg_loc)

                    # Coin img
                    coin_img = pg.transform.scale(pg.image.load('./assets/coin/coin1.png'), (TILESIZE, TILESIZE))
                    self.game.screen.blit(coin_img, (frame.centerx + 5, frame.centery + 70 + self.bg_loc))

                    # Price
                    self.game.draw_text(self.game.screen, str(self.shop_items[idx][1]), 'space.ttf', 24, WHITE, frame.centerx - 20, frame.centery + 87 + self.bg_loc)

                    idx += 1

        if self.bg_loc < -20:
            self.bg_loc += 8 * math.log(-self.bg_loc)
    
    def draw_bg_tiles(self, top):
        for i in range(WIDTH//self.bg_width):
            for j in range((HEIGHT)//self.bg_width + 1):
                self.game.screen.blit(self.bg_image, (self.bg_width*i, (self.bg_height*j + top)))

    def update(self):
        if not self.open_shop: self.checkNearby()

class ShopButton():
    def __init__(self, game, x, y, image, item, price) -> None:
        self.game = game

        self.image = image
        self.normal_img = image
        self.faded_img = self.image.copy()
        self.faded_img.fill((255, 255, 255, 80), special_flags=pg.BLEND_RGBA_MULT)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.item = item
        self.price = price
        self.purchased = False
    
    def draw(self, x, y):
        # Draw button on screen
        self.rect.x = x
        self.rect.y = y

        # Mouse
        pos = pg.mouse.get_pos()

        if self.rect.collidepoint(pos):
            self.image = self.faded_img
            if pg.mouse.get_pressed()[0] and not self.purchased and self.game.player1.moneybag >= self.price:
                self.purchased = True
                self.game.player1.loadout.append(self.item)
                self.game.player1.moneybag -= self.price
                pg.mixer.Sound.play(self.game.purchase_sound)
        else:
            self.image = self.normal_img

        self.game.screen.blit(self.image, self.rect)