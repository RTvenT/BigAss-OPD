from os.path import join

import pygame

from .bullet import Bullet

class Weapon:
    def __init__(self, player, groups):
        self.player = player
        self.all_sprites = groups['all']
        self.bullet_sprites = groups['bullet']
        self.can_shoot = True
        self.shoot_time = 0
        self.player_direction = pygame.math.Vector2()
        self.rect = pygame.Rect(0, 0, 32, 32)
        self.bullet_surf = pygame.image.load(join('..', 'images', 'gun', 'bullet.png')).convert_alpha()
        self.shoot_sound = pygame.mixer.Sound(join('..', 'audio', 'shoot.wav'))
        self.shoot_sound.set_volume(0.2)
        self.weapon_surf = pygame.image.load(join('..', 'images', 'gun', 'pistol.png')).convert_alpha()
        self.damage = 30
        self.bullet_spawn_distance = 30

    def shoot(self):
        if self.can_shoot:
            self.shoot_sound.play()
            self._create_bullets()
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def _create_bullets(self):
        pass

    def update_position(self, player_pos, direction):
        self.player_direction = direction
        self.rect.center = player_pos + direction * self.bullet_spawn_distance

    def update_timer(self, cooldown):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= cooldown:
                self.can_shoot = True 