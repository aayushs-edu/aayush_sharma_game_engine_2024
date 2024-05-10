import pygame as pg
from pygame import Vector2
from settings import *
from weapons import *
import sprites

# Mob Sprite -- inherits from pygame Sprite class
class Mob(pg.sprite.Sprite):
    # Initialize the Mob
    def __init__(self, game, target, x, y, weapon, hitpoints, color, speed, range, size=1, cooldown=MOB_COOLDOWN):
        # Define the groups this sprite belongs to
        self.groups = game.all_sprites, game.mobs, game.active_sprites
        # Initialize the superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # Reference to the game instance
        self.game = game
        # Reference to the target (player)
        self.target = target
        # Set the image of the sprite
        self.image = pg.Surface((TILESIZE*size, TILESIZE*size))
        # Fill the image with a color
        self.image.fill(color)
        # Store the color
        self.color = color
        # Get the rectangular area of the sprite
        self.x = x*TILESIZE
        self.y = y*TILESIZE
        self.rect = self.image.get_rect(center=(self.x, self.y))

        # Set initial properties
        self.speed = speed
        self.max_hitpoints = hitpoints
        self.hitpoints = hitpoints
        # Assign weapon based on input
        match weapon:
            case 'Pistol':
                self.weapon = Pistol(self.game, self, self.target.rect, cooldown)
            case 'Shotgun':
                self.weapon = Shotgun(self.game, self, self.target.rect, cooldown)
            case 'Rifle':
                self.weapon = Rifle(self.game, self, self.target.rect, cooldown)
        self.weapon.enabled = True

        self.range = range
        self.target_in_range = False

    def check_range(self):
        dist_to_player = Vector2(self.target.rect.center).distance_to(Vector2(self.x, self.y))
        self.target_in_range = dist_to_player < self.range

    # Update the sprite each frame
    def update(self):
        self.check_range()
        if self.target_in_range and not self.game.shop.open_shop:
            # Move toward player
            self.vx, self.vy = (Vector2(self.target.rect.center) - Vector2(self.x, self.y)) / TILESIZE * self.speed
            
            # Update position based on velocity
            self.x += self.vx * self.game.dt
            self.y += self.vy * self.game.dt
            self.rect.x = self.x
            # Check for collision
            self.collide_with_walls('x')
            self.rect.y = self.y
            # Check for collision
            self.collide_with_walls('y')

            # Shoot at player
            self.weapon.enabled = True
            self.weapon.shoot(REDORANGE)
        else:
            self.weapon.enabled = False
        # Check for death
        if self.hitpoints <= 0:
            self.weapon.dead = True
            self.kill()
            coin = sprites.Coin(self.game, self.x/TILESIZE, self.y/TILESIZE, 0)

    # Function to handle collision with walls
    def collide_with_walls(self, dir):
        # Check for collision in the x direction
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                # If moving right, set right edge to the left edge of the wall
                if self.vx > 0:
                    self.x = hits[0].rect.left - self.rect.width
                # If moving left, set left edge to the right edge of the wall
                if self.vx < 0:
                    self.x = hits[0].rect.right
                # Stop horizontal movement
                self.vx = 0
                self.rect.x = self.x
        # Check for collision in the y direction
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                # If moving down, set bottom to the top of the wall
                if self.vy > 0:
                    self.y = hits[0].rect.top - self.rect.height
                # If moving up, set top to the bottom of the wall
                if self.vy < 0:
                    self.y = hits[0].rect.bottom
                # Stop vertical movement
                self.vy = 0
                self.rect.y = self.y

    # Function to handle death of the mob
    def die(self):
        # Create particle effect
        for _ in range(60):
            Particle(self.game, self.x, self.y, 40, 120, 360, 2, RED)
        # Mark weapon as dead
        self.weapon.dead = True
        # Remove mob from all groups
        self.kill()

# Define the different types of mobs
class Troop(Mob):
    def __init__(self, game, target, x, y):
        weapon = 'Pistol'
        super().__init__(game, target, x, y, weapon, hitpoints=30, color=RED, speed=5, range=500)

class Sentinel(Mob):
    def __init__(self, game, target, x, y):
        weapon = 'Shotgun'
        super().__init__(game, target, x, y, weapon, hitpoints=100, color=BLUE, speed=8, range=500)

# class Boss(pg.sprite.Sprite):
#     def __init__(self, game, target, x, y):
#         # Define the groups this sprite belongs to
#         self.groups = game.all_sprites, game.mobs, game.active_sprites
#         # Initialize the superclass
#         pg.sprite.Sprite.__init__(self, self.groups)
#         # Reference to the game instance
#         self.game = game
#         # Reference to the target (player)
#         self.target = target
#         # Set the image of the sprite
#         # Fill the image with a color
#         # Store the color
#         # Get the rectangular area of the sprite
#         self.x = x*TILESIZE
#         self.y = y*TILESIZE
        
#         self.image = pg.surface.Surface((TILESIZE*5, TILESIZE*5))
#         self.rect = self.image.get_rect(center=(self.x, self.y))

#         self.max_hitpoints = 1000
#         self.hitpoints = self.max_hitpoints
    
#     def update(self):
#         pg.draw.circle(self.game.screen, RED, self.rect.center, TILESIZE)
#         pg.display.flip()


class Boss(pg.sprite.Sprite):
    def __init__(self, game, target, x, y, hitpoints):
        self.groups = game.all_sprites, game.mobs, game.active_sprites
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        self.target = target

        self.max_hitpoints = hitpoints
        self.hitpoints = self.max_hitpoints

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.image = pg.surface.Surface((TILESIZE*10, TILESIZE*10))
        self.rect = self.image.get_rect()
    
    def draw(self):
        pg.draw.circle(self.image, RED, self.rect.center, TILESIZE)


