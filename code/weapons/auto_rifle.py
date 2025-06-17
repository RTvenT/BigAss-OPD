from os.path import join
from math import radians, cos, sin
from random import random

import pygame

from .base_weapon import Weapon
from .bullet import Bullet


class AutoRifle(Weapon):
    def __init__(self, player, groups):
        super().__init__(player, groups)
        self.cooldown = 100
        self.weapon_surf = pygame.image.load(join('..', 'images', 'gun', 'auto-rifle.png')).convert_alpha()
        self.damage = 35
        self.bullet_spawn_distance = 30

    def _create_bullets(self):
        pos = self.rect.center + self.player_direction * self.bullet_spawn_distance
        angle = pygame.math.Vector2().angle_to(self.player_direction)
        spread = 5
        angle += (random() - 0.5) * spread
        rad = radians(angle)
        direction = pygame.math.Vector2(cos(rad), sin(rad))
        Bullet(self.bullet_surf, pos, direction, (self.all_sprites, self.bullet_sprites)) 