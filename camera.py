import pygame as pg
from pygame import Vector2
from settings import *

class Camera(pg.sprite.Sprite):
    def __init__(self, game, target):
        super().__init__()
        self.offset = Vector2()
        self.target = target
        self.game = game

    def custom_draw(self):
        self.offset.x = self.target.rect.centerx - WIDTH // 2
        self.offset.y = self.target.rect.centery - HEIGHT // 2        
        
        # shift the floor
        
        for sprite in self.game.all_sprites:
            offset_pos = sprite.rect.topleft - self.offset
            self.game.screen.blit(sprite.image, offset_pos)