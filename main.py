# Final: Boss with 3 phases

# Importing necessary modules
import pygame as pg
from settings import *
from random import randint
from sprites import *
from mobs import *
from camera import *
import numpy as np
import sys
import os

# Creating the game class
class Game:
    # Initializer -- sets up the game
    def __init__(self):
        # Initializes pygame
        pg.init()
        pg.mixer.init()
        # Settings -- set canvas width, height, and title
        self.screen = pg.display.set_mode((WIDTH, HEIGHT)) 
        pg.display.set_caption(TITLE)
        # Setting up pygame clock
        self.clock = pg.time.Clock()
        self.load_data()

        self.rot = 1
        self.slowmo = False

    # Method to load game data
    def load_data(self):
        # Getting file paths
        game_folder = os.path.dirname(__file__)
        asset_folder = os.path.join(game_folder, 'assets')
        self.map_data = []

        # Overlay images
        self.bulletOverlay = pg.transform.rotozoom(pg.image.load('./assets/bulletOverlay.png'), -90, 0.04)
        self.bulletTrans = self.bulletOverlay.copy()
        self.bulletTrans.fill((255, 255, 255, 60), special_flags=pg.BLEND_RGBA_MULT)

        # Loading sounds
        self.soundDir = os.path.join(asset_folder, 'sounds')
        self.gun_cock = pg.mixer.Sound(os.path.join(self.soundDir, 'gun-cock.ogg'))
        self.gun_cock.set_volume(0.5)
        self.pistol_shot = pg.mixer.Sound(os.path.join(self.soundDir, 'pistol.ogg'))
        self.pistol_shot.set_volume(0.1)
        self.shotgun_shot = pg.mixer.Sound(os.path.join(self.soundDir, 'shotgun.ogg'))
        self.shotgun_shot.set_volume(0.1)
        self.sniper_shot = pg.mixer.Sound(os.path.join(self.soundDir, 'sniper.ogg'))
        self.sniper_shot.set_volume(0.1)
        self.pistol_reload = pg.mixer.Sound(os.path.join(self.soundDir, 'pistol-reload.ogg'))
        self.pistol_reload.set_volume(0.1)
        self.shotgun_reload = pg.mixer.Sound(os.path.join(self.soundDir, 'shotgun-reload.ogg'))
        self.shotgun_reload.set_volume(0.1)
        self.purchase_sound = pg.mixer.Sound(os.path.join(self.soundDir, 'purchase.mp3'))
        self.purchase_sound.set_volume(0.1)
        self.slow_gunshot = pg.mixer.Sound(os.path.join(self.soundDir, 'slow-gun.mp3'))
        self.slow_gunshot.set_volume(0.1)
        self.explosion = pg.mixer.Sound(os.path.join(self.soundDir, 'explosion.mp3'))
        self.explosion.set_volume(0.5)
        self.music = pg.mixer.music.load(os.path.join(self.soundDir, 'music4.mp3'))
        pg.mixer.music.set_volume(0.08)
        # Reading map data from file
        with open(os.path.join(game_folder, 'map.txt'), 'r') as f:
            for line in f:
                self.map_data.append(line)
    
    # Method to initialize a new game
    def new(self):
        # Playing background music
        pg.mixer.music.play(-1)
        
        # Creating sprite groups
        self.all_sprites = pg.sprite.Group()
        self.active_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.coins = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.guns = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.particles = pg.sprite.Group()
        self.player = pg.sprite.Group()
        self.cameras = pg.sprite.Group()
        # Iterating over map data to create game objects
        for row, tiles in enumerate(self.map_data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                if tile == 'P':
                    self.player1 = Player(self, col, row)
                    self.camera = CameraGroup(self)
                if tile == 'C':
                    Coin(self, col, row, 0)
                if tile == 'U':
                    Speed(self, col, row, 0)
                if tile == 'H':
                    Health(self, col, row, 0)
                if tile == 'M':
                    Troop(self, self.player1, col, row)
                    pass
                if tile == 'S':
                    Sentinel(self, self.player1, col, row)
                    pass
                if tile == 'L':
                    Lootbox(self, col, row)
                if tile == 'B':
                    Boss(self, self.player1, col, row, 1000)
                if tile == 'S':
                    Slowmo(self, col, row, 0)
                if tile == 's':
                    self.shop = Shop(self, col, row)
    
    # Method to draw game elements
    def draw(self):
        self.screen.fill(BGCOLOR)
        if self.shop.open_shop:
            self.shop.open()
            self.drawWeaponOverlay()
            self.draw_text(self.screen, "Coins " + str(self.player1.moneybag), 'space.ttf', 24, WHITE, WIDTH/2, 50)
            self.drawHealthBar()
        else:
            self.draw_grid()
            self.camera.update()
            self.camera.custom_draw(self.player1)
            self.draw_text(self.screen, "Coins " + str(self.player1.moneybag), 'space.ttf', 24, WHITE, WIDTH/2, 50)
            self.drawAmmoOverlay()
            self.drawWeaponOverlay()
        pg.display.flip()
        pg.display.update()

    def drawHealthBar(self):
        pg.draw.rect(self.camera.display_surface, SOFTGRAY, pg.Rect(30, 30, 100, 20))
        pg.draw.rect(self.camera.display_surface, RED, pg.Rect(30, 30, self.player1.hitpoints/self.player1.max_hitpoints*100, 20))

    # Method to draw weapon overlays
    def drawWeaponOverlay(self):
        for i, weapon in enumerate(self.player1.loadout):
            box = pg.draw.rect(self.screen, GREEN if weapon.enabled else LIGHTGRAY, (20 + 80*i, HEIGHT - 80, 60, 60), 3)
            img = weapon.img_overlay.copy()
            img_rect = img.get_rect(center=box.center)
            self.screen.blit(img, img_rect)
        for i, grenade in enumerate(self.player1.explosives):
            box = pg.draw.rect(self.screen, GREEN if grenade.enabled else LIGHTGRAY, (20 + 80*i, HEIGHT - 160, 60, 60), 3)
            img = grenade.img_overlay.copy()
            img_rect = img.get_rect(center=box.center)
            self.screen.blit(img, img_rect)

    # Method to draw ammo overlays
    def drawAmmoOverlay(self):
        weapon = self.player1.activeWeapon
        if not hasattr(weapon, 'reloading'): return
        if weapon.reloading:
            pg.draw.rect(self.screen, LIGHTGRAY, pg.Rect(WIDTH-90, HEIGHT-25, 80, 10))
            pg.draw.rect(self.screen, WHITE, pg.Rect(WIDTH-90, HEIGHT-25, weapon.reloadTimeLeft/weapon.reloadDur*80, 10))
        else:
            for i in range(weapon.magSize):
                trans_img = self.bulletTrans.copy()       
                curr_rect = trans_img.get_rect(center=(WIDTH-(self.bulletTrans.get_width()+5)*i - 10, HEIGHT-20))
                self.screen.blit(trans_img, curr_rect)
                if i < weapon.shotsLeft:
                    img = self.bulletOverlay.copy()
                    self.screen.blit(img, curr_rect)

    # Method to run the game
    def run(self):
        # Game loop while playing
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    # Method to quit the game
    def quit(self):
        pg.quit()
        sys.exit()

    # Method to update game state
    def update(self):
        # Update sprites
        self.all_sprites.update()
        if len(self.particles.sprites()) > 100:
            self.particles.sprites()[0].kill()

    # Method to draw grid lines
    def draw_grid(self):
        # Vertical lines
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGRAY, (x, 0), (x, HEIGHT))
        # Horizontal lines
        for y in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGRAY, (0, y), (WIDTH, y))    

    # Method to draw text on screen
    def draw_text(self, surface, text, font, size, color, x, y):
        font = pg.font.Font(f'./assets/{font}', size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        surface.blit(text_surface, text_rect)

    # Method to handle events
    def events(self):
        # Loop
        # Loop through pygame events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYUP:
                if event.key == pg.K_LSHIFT:
                    self.player1.grenade_mode = False
                    self.player1.activeWeapon.enabled = False
                    self.player1.activeWeapon = self.player1.loadout[0]
                    self.player1.activeWeapon.enabled = True
                
    # Method to show the start screen
    def show_start_screen(self):
        self.screen.fill(BGCOLOR)
        self.draw_text(self.screen, 'Cube wars', 'space.ttf', 24, BLUE, WIDTH/2, HEIGHT/2)
        self.draw_text(self.screen, 'PLAY', 'Quantum.ttf', 24, WHITE, WIDTH/2, HEIGHT/2 + 50)
        rot = 0
        count = 1
        while True:
            # Check if player presses key
            for event in pg.event.get():
                if event.type == pg.KEYUP:
                    return
                if event.type == pg.QUIT:
                    self.quit()
            count += 1
            if count % 1000000 == 0:
                rot += 20
                loc2 = Vector2(WIDTH/2, HEIGHT/2) + Vector2(0, 150).rotate(rot)
                pg.draw.rect(self.screen, WHITE, pg.Rect(loc2.x, loc2.y, 30, 30))
                pg.display.flip()
        

    # Method to wait for a key press
    # def wait_for_key(self):
    #     waiting = True
    #     while waiting:
    #         self.clock.tick(FPS)
    #         for event in pg.event.get():
    #             if event.type == pg.QUIT:
    #                 waiting = False
    #                 self.quit()
    #             if event.type == pg.KEYUP:
    #                 waiting = False
    #     return not waiting

# Create a new game
g = Game()
# Run the game
g.show_start_screen()
while True:
    g.new()
    g.run()
    # g.show_go_screen()
g.run()
