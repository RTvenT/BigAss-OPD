from os.path import join
from math import radians, cos, sin

import pygame

from .base_weapon import Weapon


class Sword(Weapon):
    def __init__(self, player, groups):
        super().__init__(player, groups)
        self.cooldown = 400
        self.weapon_surf = pygame.image.load(join('..', 'images', 'gun', 'sword.png')).convert_alpha()
        self.damage = 100
        self.attack_range = 100
        self.attack_angle = 60
        self.attack_duration = 200
        self.attack_start_time = 0
        self.is_attacking = False
        self.show_attack_area = True
        self.attack_animation_duration = 200
        self.player_direction = pygame.math.Vector2(0, -1)  # По умолчанию смотрит вверх

    def draw_attack_area(self, surface):
        if not self.is_attacking:
            # print("Not attacking, returning")  # Отладка
            return

        current_time = pygame.time.get_ticks()
        animation_progress = (current_time - self.attack_start_time) / self.attack_animation_duration
        # print(f"Animation progress: {animation_progress}")  # Отладка
        
        if animation_progress > 1:
            # print("Animation finished")  # Отладка
            return

        # Получаем смещение камеры
        camera_offset = self.all_sprites.offset if hasattr(self.all_sprites, 'offset') else (0, 0)
        # print(f"Camera offset: {camera_offset}")  # Отладка
        
        # Получаем центр экрана
        screen_center = pygame.math.Vector2(surface.get_width() // 2, surface.get_height() // 2)
        # print(f"Screen center: {screen_center}")  # Отладка
        
        # Вычисляем позицию игрока относительно центра экрана
        player_center = screen_center
        # print(f"Player position relative to screen: {player_center}")  # Отладка
        
        base_angle = pygame.math.Vector2().angle_to(self.player_direction)
        start_angle = base_angle - self.attack_angle / 2
        end_angle = base_angle + self.attack_angle / 2
        # print(f"Angles - Base: {base_angle}, Start: {start_angle}, End: {end_angle}")  # Отладка
        
        attack_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        
        if animation_progress < 0.3:
            alpha = int(220 * (animation_progress / 0.3))
        else:
            alpha = int(220 * (1 - (animation_progress - 0.3) / 0.7))
        # print(f"Alpha value: {alpha}")  # Отладка
        
        num_waves = 3
        for i in range(num_waves):
            wave_progress = (animation_progress + i * 0.2) % 1.0
            current_radius = self.attack_range / 2 + (self.attack_range / 2 - self.attack_range / 4) * wave_progress
            # print(f"Wave {i} - Progress: {wave_progress}, Radius: {current_radius}")  # Отладка
            
            points = []
            for angle in range(int(start_angle), int(end_angle) + 1):
                rad = radians(angle)
                x = player_center.x + cos(rad) * current_radius
                y = player_center.y + sin(rad) * current_radius
                points.append((x, y))
            
            for angle in range(int(end_angle), int(start_angle) - 1, -1):
                rad = radians(angle)
                x = player_center.x + cos(rad) * (current_radius + 25)
                y = player_center.y + sin(rad) * (current_radius + 25)
                points.append((x, y))
            
            if len(points) > 2:
                wave_alpha = int(alpha * (1 - wave_progress * 0.7))
                pygame.draw.polygon(attack_surface, (255, 50, 50, wave_alpha), points)
                pygame.draw.polygon(attack_surface, (255, 100, 100, min(255, wave_alpha + 50)), points, 2)
                # print(f"Drew wave {i} with {len(points)} points")  # Отладка
                # print(f"First point coordinates: {points[0]}")  # Отладка
                # print(f"Last point coordinates: {points[-1]}")  # Отладка
        
        surface.blit(attack_surface, (0, 0))
        # print("Attack area drawn")  # Отладка

    def _create_bullets(self):
        # print(f"Creating bullets, is_attacking: {self.is_attacking}")  # Отладка
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_start_time = pygame.time.get_ticks()
            # print(f"Set is_attacking to True, start_time: {self.attack_start_time}")  # Отладка
            
            attack_rect = pygame.Rect(0, 0, self.attack_range, self.attack_range)
            player_center = pygame.math.Vector2(self.player.rect.center)
            attack_rect.center = player_center + self.player_direction * (self.attack_range / 2)
            
            for enemy in self.player.enemy_sprites:
                if attack_rect.colliderect(enemy.rect):
                    enemy_dir = pygame.math.Vector2(enemy.rect.center) - player_center
                    angle = self.player_direction.angle_to(enemy_dir)
                    if abs(angle) <= self.attack_angle / 2:
                        enemy.take_damage(self.damage)

    def update_timer(self, cooldown):
        current_time = pygame.time.get_ticks()
        
        if self.is_attacking and current_time - self.attack_start_time >= self.attack_duration:
            # print(f"Resetting is_attacking, duration: {self.attack_duration}, time passed: {current_time - self.attack_start_time}")  # Отладка
            self.is_attacking = False
            
        if not self.can_shoot:
            if current_time - self.shoot_time >= cooldown:
                self.can_shoot = True

    def update_position(self, pos, direction):
        self.player_direction = direction
        super().update_position(pos, direction) 