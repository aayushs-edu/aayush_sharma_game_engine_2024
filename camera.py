import pygame as pg
from pygame import Vector2
from settings import *

class Camera:
    def __init__(self, game):
        self.offset = Vector2(0, 0)
        self.game = game

    # Center the camera on the target
    def center_target(self, target):
        self.offset.x = target.rect.centerx - WIDTH / 2
        self.offset.y = target.rect.centery - HEIGHT / 2

    def custom_draw(self, player):

        self.center_target(player)

        # Apply offset to all sprites in the game based on player movement
        for sprite in self.game.all_sprites.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.game.screen.blit(sprite.image, offset_pos)
            

    