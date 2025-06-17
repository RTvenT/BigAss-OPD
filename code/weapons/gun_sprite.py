from math import atan2, degrees, sin, radians

import pygame

from core import WINDOW_WIDTH, WINDOW_HEIGHT


class GunSprite(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        # player connection
        self.player = player
        self.base_distance = 50
        self.distance = self.base_distance
        self.player_direction = pygame.Vector2(0, 1)
        self.target_direction = pygame.Vector2(0, 1)
        
        # Параметры плавного движения
        self.smoothing = 1
        self.floating_offset = 0
        self.floating_speed = 3
        self.time = 0

        # sprite setup
        super().__init__(groups)
        self.image = self.player.current_weapon.weapon_surf
        self.rect = self.image.get_frect(center=self.player.rect.center + self.player_direction * self.distance)

    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        raw_direction = mouse_pos - player_pos

        if raw_direction.length_squared() == 0:
            self.target_direction = pygame.Vector2(0, -1)
        else:
            self.target_direction = raw_direction.normalize()

        direction_diff = self.target_direction - self.player_direction
        self.player_direction += direction_diff * self.smoothing

        if self.player_direction.length_squared() == 0:
            self.player_direction = pygame.Vector2(0, -1)
        else:
            self.player_direction = self.player_direction.normalize()

    def update_floating(self, dt):
        self.time += dt * self.floating_speed
        self.floating_offset = sin(self.time) * 10
        self.distance = self.base_distance + self.floating_offset

    def rotate_gun(self):
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.player.current_weapon.weapon_surf, angle, 1)
        else:
            self.image = pygame.transform.rotozoom(self.player.current_weapon.weapon_surf, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False, True)

    def update(self, dt):
        self.get_direction()
        self.update_floating(dt)
        self.rotate_gun()
        
        target_pos = self.player.rect.center + self.player_direction * self.distance
        current_pos = pygame.Vector2(self.rect.center)
        new_pos = current_pos + (pygame.Vector2(target_pos) - current_pos) * self.smoothing
        self.rect.center = new_pos 