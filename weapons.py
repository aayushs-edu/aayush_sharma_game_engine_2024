import pygame as pg
from pygame import Vector2
import math

from settings import *
import random as rand
from particles import *
import numpy as np

# Rotate function to be used for guns
def rotate_img_on_pivot(img, angle, pivot, origin):
    surf = pg.transform.rotate(img, angle)

    offset = pivot + (origin - pivot).rotate(-angle)
    rect = surf.get_rect(center = offset)

    return surf, rect

def rotate_point_on_pivot(angle, pivot, origin):
    new_pt = pivot + (origin - pivot).rotate(-angle)
    return new_pt

class Gun(pg.sprite.Sprite):
    def __init__(self, game, holder, target, cooldown, img, sound, reload_sound, magSize, reloadDur, recoil, damage, bullet_speed=20, knockback=0):
        # Define sprite groups
        self.groups = game.all_sprites, game.guns, game.active_sprites
        self.game = game
        self.holder = holder
        self.target = target
        
        # Initialize sprite superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        
        # Set image and attributes
        self.img_overlay = img
        self.image_orig = img
        self.image = self.image_orig
        
        # Set position
        self.pivot = Vector2(self.holder.rect.center)
        self.pos = self.pivot + (20, 0)
        self.x, self.y = self.pos
        self.rect = self.image.get_rect(center=self.pos)
        
        # Set shooting attributes
        self.alpha = 255
        self.shooting_point = Vector2(0, 0)
        self.cooldown = cooldown
        self.cool_dur = 0
        self.magSize = magSize
        self.shotsLeft = magSize
        self.reloading = False
        self.reloadDur = reloadDur
        self.reloadTimeLeft = self.reloadDur
        self.damage = damage
        self.bullet_speed = bullet_speed
        self.knockback = knockback
        
        # Set other attributes
        self.enabled = False
        self.dead = False
        self.disabledLifetime = 1
        self.flipped = False
        self.angle = 0
        self.recoiling = False
        self.recoil = recoil
        self.recoil_time = max(recoil/200, self.cooldown)
        self.recoil_timer = self.recoil_time
        
        # Set sounds
        self.sound = sound
        self.reload_sound = reload_sound
        pg.mixer.Sound.play(self.game.gun_cock)

    def get_data(self):
        return {
            'angle': self.angle,
        }
    
    def load_data(self, data : dict):
        if data.__class__.__name__ != 'dict': return
        self.angle = data.get('angle')

    def update(self):
        # Update recoil
        if self.recoiling:
            self.recoil_timer -= self.game.dt
            if self.recoil_timer <= 0:
                self.recoiling = False
                self.recoil_timer = self.recoil_time
        
        # Handle disabled state
        if self.dead:
            if self.disabledLifetime <= 0:
                self.fade()
            else:
                self.disabledLifetime -= self.game.dt
        else:
            # Handle enabled state
            if not self.enabled:
                self.image = self.image.copy()
                self.image.fill((255, 255, 255, 0), special_flags=pg.BLEND_RGBA_MULT)
            else:
                self.image = self.image_orig
                # Stick to player
                self.pivot = Vector2(self.holder.rect.center)
                self.pos = self.pivot + (20, 0)
                self.x, self.y = self.pos
                
                # Rotate gun towards target
                if self.target == 'Mouse':
                    self.rotate(Vector2(pg.mouse.get_pos()))
                elif self.target == 'Idle':
                    pass
                else:
                    self.rotate(self.target.center)

                # Cooldown
                if self.cool_dur > 0:
                    self.cool_dur -= 2 * self.game.dt
                if self.reloading:
                    if self.reloadTimeLeft <= 0:
                        self.shotsLeft = self.magSize
                        self.reloading = False
                        self.reloadTimeLeft = self.reloadDur
                    else:
                        self.reloadTimeLeft -= self.game.dt

    def rotate(self, target):
        # Calculate difference vector between holder and target
        if self.holder.__class__.__bases__[0].__name__ == 'Mob':
            offset = Vector2(self.target.center) - Vector2(self.pos)
        else:
            offset = Vector2(target) - (WIDTH // 2, HEIGHT // 2)
        # Calculate angle between holder and target
        angle = -math.degrees(math.atan2(offset.y, offset.x))

        # Handle recoiling
        if self.recoiling:
            self.angle += (angle - self.angle) / 2
        else:
            self.angle = angle

        # FLip sprite image if necessary
        if target[0] < WIDTH // 2 and not self.flipped:
            self.flipped = True
            self.image_orig = pg.transform.flip(self.image_orig, False, True)
        elif target[0] > WIDTH // 2 and self.flipped: 
            self.flipped = False
            self.image_orig = pg.transform.flip(self.image_orig, False, True)

        # Rotate shooting point and apply rotation to image
        self.shooting_point = rotate_point_on_pivot(self.angle, 
                                                    Vector2(self.pivot), 
                                                    self.pivot + (max(self.image.get_width(), self.image.get_height()), 
                                                    -5 * (-1 if self.flipped else 1)))
        self.image, self.rect = rotate_img_on_pivot(self.image_orig, self.angle, Vector2(self.pivot), Vector2(self.pos))
        
    def shoot(self, color):
        # Fire bullet if conditions allow -- not cooling down, not reloading
        if self.cool_dur <= 0 and not self.reloading:
            # Instantiate bullets
            Bullet(self.game, *self.shooting_point, self.angle, self.holder, color, self.damage, speed=(self.bullet_speed if not self.game.slowmo or self.holder.__class__.__name__ == 'Player' else self.bullet_speed/4))
            
            # Particle trail
            pDir = -1 if self.flipped else 1
            for _ in range(10):
                Particle(self.game, *self.shooting_point, 15, 100*pDir, 40, 5, YELLOW)

            self.cool_dur = self.cooldown
            pg.mixer.Sound.play(self.sound) if not self.game.slowmo else pg.mixer.Sound.play(self.game.slow_gunshot)

            # Handle magSize and reloading
            self.shotsLeft -= 1
            if self.shotsLeft <= 0:
                self.reloading = True
                pg.mixer.Sound.play(self.reload_sound)

            self.recoiling = True

            # Apply recoil
            self.angle += (-self.recoil if self.flipped else self.recoil)

            # knockback_vec = Vector2(*pg.mouse.get_pos()) - Vector2(WIDTH//2, HEIGHT//2)
            # self.holder.vx -= self.knockback * knockback_vec.x
            # self.holder.vy -= self.knockback * knockback_vec.y
    
    def fade(self):
        # Fade out the gun sprite
        self.alpha = max(0, self.alpha-2)  # alpha should never be < 0.
        self.image = self.image.copy()
        self.image.fill((255, 255, 255, self.alpha), special_flags=pg.BLEND_RGBA_MULT)
        if self.alpha <= 0:  # Kill the sprite when the alpha is <= 0.
            self.kill() 

# Inherits from Gun class
class Pistol(Gun):
    def __init__(self, game, holder, target, cooldown):
        self.image = pg.transform.scale(pg.image.load('./assets/pistol.png').convert_alpha(), (35, 25))
        sound = game.pistol_shot
        reload_sound = game.pistol_reload
        super().__init__(game, holder, target, cooldown, self.image, sound, reload_sound, magSize=6, reloadDur=1.5, recoil=60, damage=20)

# Inherits from Gun class
class Rifle(Gun):
    def __init__(self, game, holder, target, cooldown):
        self.image = pg.transform.scale(pg.image.load('./assets/rifle.png').convert_alpha(), (52, 14))
        sound = game.pistol_shot
        reload_sound = game.pistol_reload
        super().__init__(game, holder, target, cooldown, self.image, sound, reload_sound, magSize=30, reloadDur=1, recoil=15, damage=10)

# Inherits from Gun class
class Sniper(Gun):
    def __init__(self, game, holder, target, cooldown):
        self.image = pg.transform.scale(pg.image.load('./assets/sniper.png').convert_alpha(), (65, 21))
        sound = game.sniper_shot
        reload_sound = game.shotgun_reload
        super().__init__(game, holder, target, cooldown, self.image, sound, reload_sound, magSize=4, reloadDur=4, recoil=100, damage=100, bullet_speed=50, knockback=5)

class RocketLauncher(Gun):
    def __init__(self, game, holder, target, cooldown):
        self.image = pg.transform.scale(pg.image.load('./assets/rocket-launcher.png').convert_alpha(), (65, 21))
        sound = game.sniper_shot
        reload_sound = game.shotgun_reload
        super().__init__(game, holder, target, cooldown, self.image, sound, reload_sound, magSize=4, reloadDur=4, recoil=100, damage=100, bullet_speed=25, knockback=5)

    def shoot(self, color):
        # Fire bullet if conditions allow -- not cooling down, not reloading
        if self.cool_dur <= 0 and not self.reloading:
            # Instantiate bullets
            Bullet(self.game, *self.shooting_point, self.angle, self.holder, LIGHTBLUE, self.damage, speed=(self.bullet_speed if not self.game.slowmo or self.holder.__class__.__name__ == 'Player' else self.bullet_speed/4), image=pg.transform.scale(pg.image.load('./assets/rocket.png').convert_alpha(), (20, 20)), trail=True)
            
            # Particle trail
            pDir = -1 if self.flipped else 1
            for _ in range(10):
                Particle(self.game, *self.shooting_point, 15, 100*pDir, 40, 5, YELLOW)

            self.cool_dur = self.cooldown
            pg.mixer.Sound.play(self.sound)

            # Handle magSize and reloading
            self.shotsLeft -= 1
            if self.shotsLeft <= 0:
                self.reloading = True
                pg.mixer.Sound.play(self.reload_sound)

            self.recoiling = True

            # Apply recoil
            self.angle += (-self.recoil if self.flipped else self.recoil)

            # knockback_vec = Vector2(*pg.mouse.get_pos()) - Vector2(WIDTH//2, HEIGHT//2)
            # self.holder.vx -= self.knockback * knockback_vec.x
            # self.holder.vy -= self.knockback * knockback_vec.y
    
    def fade(self):
        # Fade out the gun sprite
        self.alpha = max(0, self.alpha-2)  # alpha should never be < 0.
        self.image = self.image.copy()
        self.image.fill((255, 255, 255, self.alpha), special_flags=pg.BLEND_RGBA_MULT)
        if self.alpha <= 0:  # Kill the sprite when the alpha is <= 0.
            self.kill() 

# Inherits from Gun class	
class Shotgun(Gun):
    def __init__(self, game, holder, target, cooldown):
        self.image = pg.transform.scale(pg.image.load('./assets/shotgun.png').convert_alpha(), (44, 16))
        sound = game.shotgun_shot
        reload_sound = game.shotgun_reload
        super().__init__(game, holder, target, cooldown, self.image, sound, reload_sound, magSize=10, reloadDur=3, recoil=120, damage=50)
    
    def shoot(self, color):
        if self.cool_dur <= 0 and not self.reloading:
            for angle in np.random.normal(loc=self.angle, scale=10.0, size=5):
                Bullet(self.game, *self.shooting_point, angle, self.holder, color, self.damage, 10 if self.game.slowmo else 20) 

            self.shotsLeft -= 1
            if self.shotsLeft <= 0:
                self.reloading = True
                if not self.holder.__class__.__bases__[0].__name__ == 'Mob':
                    pg.mixer.Sound.play(self.reload_sound)

            pDir = -1 if self.flipped else 1
            for _ in range(10):
                Particle(self.game, *self.shooting_point, 15, 100*pDir, 40, 5, YELLOW)

            self.cool_dur = self.cooldown

            pg.mixer.Sound.play(self.sound) if not self.game.slowmo else pg.mixer.Sound.play(self.game.slow_gunshot)
            
            self.recoiling = True

            self.angle += (-self.recoil if self.flipped else self.recoil)

            # Apply recoil
            self.angle += (-self.recoil if self.flipped else self.recoil)

            # knockback_vec = Vector2(*pg.mouse.get_pos()) - Vector2(WIDTH//2, HEIGHT//2)            
            # self.holder.vx -= self.knockback * knockback_vec.x
            # self.holder.vy -= self.knockback * knockback_vec.y


# Bullet Sprites
class Bullet(pg.sprite.Sprite):
    def __init__(self, game, x, y, angle, shooter, color, damage, speed, image=None, trail=False, dur=5):
        self.groups = game.all_sprites, game.bullets, game.active_sprites
        # init superclass
        pg.sprite.Sprite.__init__(self, self.groups)
        # set game class
        self.game = game
        # Set dimensions 
        # self.image = pg.transform.rotozoom(pg.image.load('./assets/bullet1.png'), angle+45, 2)
        if image: 
            self.image = image
        else:
            self.image = pg.Surface((10, 10))
            self.image.fill(color)

        self.rect = self.image.get_rect(center=(x, y))
        self.x = x
        self.y = y

        self.shooter = shooter
        self.color = color

        self.angle = angle
        self.norm_speed = speed
        self.speed = self.norm_speed
        self.damage = damage
        self.trail = trail
        self.dur = dur

        # Calculating velocity based on angle
        self.vx = math.cos(self.angle * math.pi/180) * self.speed
        self.vy = math.sin(self.angle * math.pi/180) * self.speed
    
    def update(self):
        self.dur -= self.game.dt
        if self.dur <= 0:
            self.kill()
        # Move in direction specified in init, constant speed
        self.x += self.vx
        self.y -= self.vy

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        self.collide()

    # Handle bullet collisions
    def collide(self):
        hits = pg.sprite.spritecollide(self, self.game.all_sprites, False)
        if hits:
            # Particle trail
            if self.trail:
                n = 50
            elif self.game.slowmo:
                n = 5  
            else: n = 10
            for _ in range(n):
                Particle(self.game, self.x, self.y, 15, 150, 360, 1, self.color, decay=True)

            # If bullet hits mob, kill mob
            if hits[0].__class__.__bases__[0].__name__ == 'Mob' or hits[0].__class__.__name__ == 'Player':
                for _ in range(10):
                    Particle(self.game, self.x, self.y, 20, 120, 360, 1, hits[0].color)
                hits[0].hitpoints -= self.damage
                print(hits[0].hitpoints)
                self.kill()
            # Destroy bullet if hits wall
            elif hits[0].__class__.__name__ == 'Wall':
                self.kill()
                for _ in range(10):
                    Particle(self.game, self.x, self.y, 12, 80, 360, 1, YELLOW)
            # If hit other bullets, destroy both bullets
            elif hits[0].__class__.__name__ == 'Bullet' and hits[0] is not self and hits[0].shooter is not self.shooter:
                self.kill()
                hits[0].kill()
                for _ in range(10):
                    Particle(self.game, self.x, self.y, 25, 200, 360, 1, YELLOW)

class Grenade(pg.sprite.Sprite):
    def __init__(self, game, holder, radius, damage) -> None:
        self.game = game
        self.holder = holder
        self.target = None
        
        # Initialize sprite superclass
        pg.sprite.Sprite.__init__(self, game.all_sprites, game.active_sprites)

        # Set image and attributes
        self.img_overlay = pg.transform.scale(pg.image.load('./assets/grenade.png').convert_alpha(), (TILESIZE, TILESIZE))
        self.image_orig = self.img_overlay
        self.image = self.image_orig
        
        # Set position
        self.pivot = Vector2(self.holder.rect.center)
        self.pos = self.pivot + (20, 0)
        self.x, self.y = self.pos
        self.rect = self.image.get_rect(center=self.pos)
        self.offset = Vector2(0, 0)

        # Set other attributes
        self.enabled = False
        self.dead = False
        self.disabledLifetime = 1
        self.flipped = False
        self.angle = 0

        # Set detonation attributes
        self.detonate_time = 2
        self.detonate_timer = self.detonate_time
        self.detonating = False
        self.radius = radius
        self.damage = damage

    
    def rotate(self, target):
        self.offset = Vector2(target) - (WIDTH // 2, HEIGHT // 2)

        pg.draw.line(self.game.screen, GREEN, (WIDTH//2, HEIGHT//2), target, 2)
        pg.display.flip()

        # Calculate angle between holder and target
        angle = -math.degrees(math.atan2(self.offset.y, self.offset.x))
        self.angle = angle

        # FLip sprite image if necessary
        if target[0] < WIDTH // 2 and not self.flipped:
            self.flipped = True
            self.image_orig = pg.transform.flip(self.image_orig, False, True)
        elif target[0] > WIDTH // 2 and self.flipped: 
            self.flipped = False
            self.image_orig = pg.transform.flip(self.image_orig, False, True)

        self.image, self.rect = rotate_img_on_pivot(self.image_orig, self.angle, Vector2(self.pivot), Vector2(self.pos))
    
    def update(self):
        if self.detonating:
            if not (abs(self.offset.x) <= TILESIZE and abs(self.offset.y) <= TILESIZE):
                self.offset = self.target - (self.x, self.y)
                self.x += 0.2*self.offset.x
                self.y += 0.2*self.offset.y
                self.rect.x = self.x
                self.rect.y = self.y

            self.detonate_timer -= self.game.dt
            if self.detonate_timer <= 0:
                for mob in self.game.mobs.sprites():
                    dist = Vector2(mob.rect.center).distance_to(Vector2(self.x, self.y))
                    if dist <= self.radius:
                        mob.hitpoints -= self.damage
                self.detonating = False
                self.kill()
            elif self.detonate_timer <= 0.5:
                pg.mixer.Sound.play(self.game.explosion)
                for i in range(25):
                    Particle(self.game, self.x, self.y, 30, self.radius*1.5, 360, 1, rand.choice([RED, YELLOW, ORANGE]), rotation=rand.randint(0, 360))
            return
        if not self.enabled:
                self.image = self.image.copy()
                self.image.fill((255, 255, 255, 0), special_flags=pg.BLEND_RGBA_MULT)
        else:
            self.image = self.image_orig
            # Stick to player
            self.pivot = Vector2(self.holder.rect.center)
            self.pos = self.pivot + (20, 0)
            self.x, self.y = self.pos
            self.rotate(Vector2(pg.mouse.get_pos()))
    
    def shoot(self, color):
        if not self.detonating: self.detonating = True
        self.target = pg.mouse.get_pos() + self.game.camera.offset

