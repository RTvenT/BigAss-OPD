from os.path import join

import pygame

from .base_weapon import Weapon
from .bullet import Bullet


class Pistol(Weapon):
    def __init__(self, player, groups):
        super().__init__(player, groups)
        self.cooldown = 500
        self.weapon_surf = pygame.image.load(join('..', 'images', 'gun', 'pistol.png')).convert_alpha()
        self.damage = 15
        self.bullet_spawn_distance = 25

    def _create_bullets(self):
        pos = self.rect.center + self.player_direction * self.bullet_spawn_distance
        Bullet(self.bullet_surf, pos, self.player_direction, (self.all_sprites, self.bullet_sprites)) 