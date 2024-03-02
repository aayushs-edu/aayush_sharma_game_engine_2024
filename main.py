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
import sys
from os import path

# Creating the game class
class Game:
    # Initializer -- sets up the game
    def __init__(self):
        # Initializes pygame
        pg.init()
        # Settings -- set canvas width, height, and title
        self.screen = pg.display.set_mode((WIDTH, HEIGHT)) 
        pg.display.set_caption(TITLE)
        # Setting up pygame clock
        self.clock = pg.time.Clock()
        self.load_data()

    def load_data(self):
        game_folder = path.dirname(__file__)
        self.map_data = []
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
        with open(path.join(game_folder, 'map.txt'), 'rt') as f:
            for line in f:
                print(line)
                self.map_data.append(line)
    
    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.coins = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
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
                    Coin(self, col, row)
                if tile == 'U':
                    PowerUp(self, col, row)

    def draw(self):
        self.screen.fill(BGCOLOR)
        self.draw_grid()
        self.all_sprites.draw(self.screen)
        self.draw_text(self.screen, "Coins " + str(self.player1.moneybag), 24, WHITE, WIDTH/2 - 32, 2)
        pg.display.update()
        pg.display.flip()

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

    def draw_grid(self):
        # Vertical lines
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        # Horizontal lines
        for y in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))    

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

# Create a new game
g = Game()
# Run the game
# g.show_start_screen()
while True:
    g.new()
    g.run()
    # g.show_go_screen()
g.run()