# This file was created by: Aayush Sharma
'''
enemies that follow player(could have shooting capability) - goal: kill enemy, rule: don't die to it
projectiles(guns/bullets) - verb, freedom, goal: shoot enemy
lootbox -> powerups/coins - verb: open lootbox, freedom, goal: get items
The player shoots an enemy and it dies and drops its weapon.
'''

# Import modules
import pygame as pg
from settings import *
from random import randint
from sprites import *
from camera import *
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

    def load_data(self):
        game_folder = os.path.dirname(__file__)
        asset_folder = os.path.join(game_folder, 'assets')
        self.map_data = []

        # Overlay images
        self.bulletOverlay = pg.transform.rotozoom(pg.image.load('./assets/bulletOverlay.png'), -90, 0.04)
        self.bulletTrans = self.bulletOverlay.copy()
        self.bulletTrans.fill((0, 0, 0, 30), special_flags=pg.BLEND_RGBA_MULT)

        # Sounds
        self.soundDir = os.path.join(asset_folder, 'sounds')
        self.gun_cock = pg.mixer.Sound(os.path.join(self.soundDir, 'gun-cock.ogg'))
        self.pistol_shot = pg.mixer.Sound(os.path.join(self.soundDir, 'pistol.ogg'))
        self.shotgun_shot = pg.mixer.Sound(os.path.join(self.soundDir, 'shotgun.ogg'))
        self.music = pg.mixer.music.load(os.path.join(self.soundDir, 'music1.ogg'))
        # 'r'     open for reading (default)
        # 'w'     open for writing, truncating the file first
        # 'x'     open for exclusive creation, failing if the file already exists
        # 'a'     open for writing, appending to the end of the file if it exists
        # 'b'     binary mode
        # 't'     text mode (default)
        # '+'     open a disk file for updating (reading and writing)
        # 'U'     universal newlines mode (deprecated)
        # below opens file for reading in text mode
        # with 
        '''
        The with statement is a context manager in Python. 
        It is used to ensure that a resource is properly closed or released 
        after it is used. This can help to prevent errors and leaks.
        '''
        with open(os.path.join(game_folder, 'map.txt'), 'rt') as f:
            for line in f:
                print(line)
                self.map_data.append(line)
    
    def new(self):
        pg.mixer.music.play(-1)
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.coins = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.guns = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.particles = pg.sprite.Group()
        self.player = pg.sprite.Group()
        self.cameras = pg.sprite.Group()
        for row, tiles in enumerate(self.map_data):
            print(row)
            for col, tile in enumerate(tiles):
                print(col)
                if tile == '1':
                    print("a wall at", row, col)
                    Wall(self, col, row)
                if tile == 'P':
                    self.player1 = Player(self, col, row)
                if tile == 'C':
                    Coin(self, col, row, 0)
                if tile == 'U':
                    Speed(self, col, row, 0)
                if tile == 'M':
                    Mob(self, self.player1, col, row)
                    pass
                if tile == 'L':
                    Lootbox(self, col, row)
        # self.camera_group = CameraGroup(self)

    def draw(self):
        self.screen.fill(BGCOLOR)
        self.draw_grid()
        self.all_sprites.draw(self.screen)
        self.draw_text(self.screen, "Coins " + str(self.player1.moneybag), 24, WHITE, WIDTH/2 - 32, 2)
        self.drawWeaponOverlay()
        self.drawAmmoOverlay()
        self.drawHealthBar()
        pg.display.update()
        pg.display.flip()

    def drawWeaponOverlay(self):
        for i, weapon in enumerate(self.player1.loadout):
            box = pg.draw.rect(self.screen, GREEN if weapon.enabled else LIGHTGRAY, (20 + 80*i, HEIGHT - 80, 60, 60), 3)
            img = weapon.img_overlay.copy()
            img_rect = img.get_rect(center=box.center)
            self.screen.blit(img, img_rect)

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
            
            
    
    def drawHealthBar(self):
        pg.draw.rect(self.screen, SOFTGRAY, pg.Rect(30, 30, 100, 20))
        pg.draw.rect(self.screen, RED, pg.Rect(30, 30, self.player1.hitpoints, 20))

    # Runs our game
    def run(self):
        # Game loop while playing
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # Update sprites
        self.all_sprites.update()
        # self.camera_group.update()
        # self.camera_group.custom_draw(self.player1)

    def draw_grid(self):
        # Vertical lines
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGRAY, (x, 0), (x, HEIGHT))
        # Horizontal lines
        for y in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGRAY, (0, y), (WIDTH, y))    

    def draw_text(self, surface, text, size, color, x, y):
        font_name = pg.font.match_font('arial')
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x,y)
        surface.blit(text_surface, text_rect)

    def events(self):
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
                
    def show_start_screen(self):
        self.screen.fill(BGCOLOR)
        self.draw_text(self.screen, 'Top Down Shooter', 24, WHITE, WIDTH/2 - 32, 2)
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False

# Create a new game
g = Game()
# Run the game
g.show_start_screen()
while True:
    g.new()
    g.run()
    # g.show_go_screen()
g.run()