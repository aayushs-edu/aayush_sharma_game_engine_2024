import pygame as pg
from pygame import Vector2
from settings import *

class Camera:
    def __init__(self, game):
        self.offset = Vector2(0, 0)
        self.game = game

        self.zoom_scale = 1
        self.internal_surface_size = (WIDTH*1.5, HEIGHT*1.5)
        self.internal_surface = pg.Surface(self.internal_surface_size, pg.SRCALPHA)
        self.internal_rect = self.internal_surface.get_rect(center=(WIDTH/2, HEIGHT/2))
        self.internal_surface_size_vector = Vector2(self.internal_surface_size)

    # Center the camera on the target
    def center_target(self, target):
        self.offset.x = target.rect.centerx - WIDTH / 2
        self.offset.y = target.rect.centery - HEIGHT / 2

    def custom_draw(self, player):

        self.center_target(player)

        self.internal_surface.fill(BGCOLOR)

        # Apply offset to all sprites in the game based on player movement
        for sprite in self.game.all_sprites.sprites():
            offset_pos = sprite.rect.topleft - self.offset
            self.internal_surface.blit(sprite.image, offset_pos)

        scaled_surf = pg.transform.scale(self.internal_surface, self.internal_surface_size_vector*self.zoom_scale)
        scaled_rect = scaled_surf.get_rect(center=(WIDTH/2, HEIGHT/2))

        self.game.screen.blit(scaled_surf, scaled_rect)
            

class CameraGroup(pg.sprite.Group):
	def __init__(self, game):
		super().__init__()
		self.game = game
		self.display_surface = self.game.screen

		# camera offset 
		self.offset = pg.math.Vector2()
		self.half_w = WIDTH // 2
		self.half_h = HEIGHT // 2

		# box setup
		self.camera_borders = {'left': 200, 'right': 200, 'top': 100, 'bottom': 100}
		l = self.camera_borders['left']
		t = self.camera_borders['top']
		w = WIDTH  - (self.camera_borders['left'] + self.camera_borders['right'])
		h = HEIGHT  - (self.camera_borders['top'] + self.camera_borders['bottom'])
		self.camera_rect = pg.Rect(l,t,w,h)

		# camera speed
		self.keyboard_speed = 5
		self.mouse_speed = 0.2

		# zoom 
		self.zoom_scale = 1
		self.internal_surf_size = (2500,2500)
		self.internal_surf = pg.Surface(self.internal_surf_size, pg.SRCALPHA)
		self.internal_rect = self.internal_surf.get_rect(center = (self.half_w,self.half_h))
		self.internal_surface_size_vector = pg.math.Vector2(self.internal_surf_size)
		self.internal_offset = pg.math.Vector2()
		self.internal_offset.x = self.internal_surf_size[0] // 2 - self.half_w
		self.internal_offset.y = self.internal_surf_size[1] // 2 - self.half_h

	def center_target_camera(self,target):
		self.offset.x = target.rect.centerx - self.half_w
		self.offset.y = target.rect.centery - self.half_h

	def box_target_camera(self,target):

		if target.rect.left < self.camera_rect.left:
			self.camera_rect.left = target.rect.left
		if target.rect.right > self.camera_rect.right:
			self.camera_rect.right = target.rect.right
		if target.rect.top < self.camera_rect.top:
			self.camera_rect.top = target.rect.top
		if target.rect.bottom > self.camera_rect.bottom:
			self.camera_rect.bottom = target.rect.bottom

		self.offset.x = self.camera_rect.left - self.camera_borders['left']
		self.offset.y = self.camera_rect.top - self.camera_borders['top']

	def custom_draw(self, player):
		
		self.center_target_camera(player)

		self.internal_surf.fill(BGCOLOR)

		# active elements
		for sprite in self.game.all_sprites.sprites():
			offset_pos = sprite.rect.topleft - self.offset + self.internal_offset
			self.internal_surf.blit(sprite.image,offset_pos)

		scaled_surf = pg.transform.scale(self.internal_surf,self.internal_surface_size_vector * self.zoom_scale)
		scaled_rect = scaled_surf.get_rect(center = (self.half_w,self.half_h))

		self.display_surface.blit(scaled_surf,scaled_rect)
