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
        self.pistol_shot = pg.mixer.Sound(os.path.join(self.soundDir, 'pistol.ogg'))
        self.pistol_shot.set_volume(0.5)
        self.shotgun_shot = pg.mixer.Sound(os.path.join(self.soundDir, 'shotgun.ogg'))
        self.shotgun_shot.set_volume(0.5)
        self.pistol_reload = pg.mixer.Sound(os.path.join(self.soundDir, 'pistol-reload.ogg'))
        self.shotgun_reload = pg.mixer.Sound(os.path.join(self.soundDir, 'shotgun-reload.ogg'))
        self.music = pg.mixer.music.load(os.path.join(self.soundDir, 'music1.ogg'))
        
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
                    self.camera = Camera(self)
                if tile == 'C':
                    Coin(self, col, row, 0)
                if tile == 'U':
                    Speed(self, col, row, 0)
                if tile == 'H':
                    Health(self, col, row, 0)
                if tile == 'M':
                    Troop(self, self.player1, col, row)
                if tile == 'S':
                    Sentinel(self, self.player1, col, row)
                if tile == 'L':
                    Lootbox(self, col, row)
    
    # Method to draw game elements
    def draw(self):
        self.screen.fill(BGCOLOR)
        self.draw_grid()
        self.camera.custom_draw(self.player1)
        self.draw_text(self.screen, "Coins " + str(self.player1.moneybag), 'space.ttf', 24, WHITE, WIDTH/2 - 32, 2)
        self.drawWeaponOverlay()
        self.drawAmmoOverlay()
        self.drawHealthBar()
        pg.display.update()
        pg.display.flip()

    # Method to draw weapon overlays
    def drawWeaponOverlay(self):
        for i, weapon in enumerate(self.player1.loadout):
            box = pg.draw.rect(self.screen, GREEN if weapon.enabled else LIGHTGRAY, (20 + 80*i, HEIGHT - 80, 60, 60), 3)
            img = weapon.img_overlay.copy()
            img_rect = img.get_rect(center=box.center)
            self.screen.blit(img, img_rect)

    # Method to draw ammo overlays
    def drawAmmoOverlay(self):
        weapon = self.player1.activeWeapon
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
            
    # Method to draw health bar
    def drawHealthBar(self):
        pg.draw.rect(self.screen, SOFTGRAY, pg.Rect(30, 30, 100, 20))
        pg.draw.rect(self.screen, RED, pg.Rect(30, 30, self.player1.hitpoints, 20))

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
            self.particles.remove(self.particles.sprites()[100:])

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
            # If user presses key
            # if event.type == pg.KEYDOWN:
            #     # Check input and move character based on input
            #     match event.key:
            #         # Move left
            #         case pg.K_a | pg.K_LEFT:
            #             self.player1.move(dx=-1)
            #         # Move right
            #         case pg.K_d | pg.K_RIGHT:
            #             self.player1.move(dx=1)
            #         # Move down
            #         case pg.K_s | pg.K_DOWN:
            #             self.player1.move(dy=1)
            #         # Move up
            #         case pg.K_w | pg.K_UP:
            #             self.player1.move(dy=-1)
                
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
