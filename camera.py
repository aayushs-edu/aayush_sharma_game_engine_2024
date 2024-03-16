import pygame as pg
from pygame import Vector2
from settings import *

class Camera:
    def __init__(self, game):
        self.offset = Vector2(300, 300)
        self.game = game

    def center_target(self, target):
        self.offset.x = target.rect.centerx - WIDTH / 2
        self.offset.y = target.rect.centery - HEIGHT / 2

    def custom_draw(self, player):

        self.center_target(player)

        for wall in self.game.walls:
            wall_offset = wall.rect.topleft - self.offset
            self.game.screen.blit(wall.image, wall_offset)

        for sprite in self.game.active_sprites.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.game.screen.blit(sprite.image, offset_pos)
            

    