import pygame as pg
from settings import *

class CameraGroup(pg.sprite.Group):
	def __init__(self, game):
		super().__init__()
		self.display_surface = game.screen

		# camera offset 
		self.offset = pg.math.Vector2()
		self.half_w = self.display_surface.get_size()[0] // 2
		self.half_h = self.display_surface.get_size()[1] // 2

		# box setup
		self.camera_borders = {'left': 200, 'right': 200, 'top': 100, 'bottom': 100}
		l = self.camera_borders['left']
		t = self.camera_borders['top']
		w = self.display_surface.get_size()[0]  - (self.camera_borders['left'] + self.camera_borders['right'])
		h = self.display_surface.get_size()[1]  - (self.camera_borders['top'] + self.camera_borders['bottom'])
		self.camera_rect = pg.Rect(l,t,w,h)

		# ground
		self.ground_surf = pg.image.load('graphics/ground.png').convert_alpha()
		self.ground_rect = self.ground_surf.get_rect(topleft = (0,0))

		# camera speed
		self.keyboard_speed = 5
		self.mouse_speed = 0.2

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

	def custom_draw(self,player):
		
		# self.center_target_camera(player)
		self.box_target_camera(player)

		# ground 
		ground_offset = self.ground_rect.topleft - self.offset + self.internal_offset
		self.internal_surf.blit(self.ground_surf,ground_offset)

		# active elements
		for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
			offset_pos = sprite.rect.topleft - self.offset + self.internal_offset
			self.internal_surf.blit(sprite.image,offset_pos)

		scaled_surf = pg.transform.scale(self.internal_surf,self.internal_surface_size_vector * self.zoom_scale)
		scaled_rect = scaled_surf.get_rect(center = (self.half_w,self.half_h))

		self.display_surface.blit(scaled_surf,scaled_rect)