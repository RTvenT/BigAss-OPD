from os.path import join
from math import radians, cos, sin

import pygame

from .base_weapon import Weapon
from .bullet import Bullet


class Shotgun(Weapon):
    def __init__(self, player, groups):
        super().__init__(player, groups)
        self.cooldown = 500
        self.spread = 30
        self.weapon_surf = pygame.image.load(join('..', 'images', 'gun', 'shotgun.png')).convert_alpha()
        self.weapon_surf = pygame.transform.rotozoom(self.weapon_surf, 0, 1.2)
        self.damage = 30

    def _create_bullets(self):
        base_pos = self.rect.center + self.player_direction * self.bullet_spawn_distance
        base_angle = pygame.math.Vector2().angle_to(self.player_direction)
        
        for angle_offset in [-self.spread, -self.spread/2, 0, self.spread/2, self.spread]:
            angle = base_angle + angle_offset
            rad = radians(angle)
            direction = pygame.math.Vector2(cos(rad), sin(rad))
            Bullet(self.bullet_surf, base_pos, direction, (self.all_sprites, self.bullet_sprites)) 