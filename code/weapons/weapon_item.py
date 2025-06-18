import pygame
from math import sin

class WeaponItem(pygame.sprite.Sprite):
    def __init__(self, weapon_type, pos, groups):
        super().__init__(groups)
        self.weapon_type = weapon_type
        self.groups = groups
        
        # Спрайт оружия
        self.image = weapon_type.weapon_surf.copy()
        self.rect = self.image.get_rect(center=pos)
        
        # Эффект парения
        self.float_offset = 0
        self.float_speed = 2
        self.time = 0
        self.base_pos = pygame.math.Vector2(pos)
        
        # Подсветка
        self.glow_radius = 40
        self.glow_color = (255, 255, 100, 100)  # Желтая подсветка с прозрачностью
        self.glow_surface = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.glow_surface, self.glow_color, (self.glow_radius, self.glow_radius), self.glow_radius)
        
        # Подсветка при приближении
        self.pickup_radius = 50
        self.pickup_glow_color = (100, 255, 100, 150)  # Зеленая подсветка
        self.pickup_glow_surface = pygame.Surface((self.pickup_radius * 2, self.pickup_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.pickup_glow_surface, self.pickup_glow_color, 
                         (self.pickup_radius, self.pickup_radius), self.pickup_radius)
        
        # Эффект броска
        self.throw_cooldown = 500  # Время в миллисекундах, в течение которого нельзя подобрать оружие
        self.throw_time = pygame.time.get_ticks()
        
    def update(self, dt):
        current_time = pygame.time.get_ticks()
        
        # Обновляем эффект парения
        self.time += dt * self.float_speed
        self.float_offset = sin(self.time) * 10
        self.rect.center = self.base_pos + pygame.math.Vector2(0, self.float_offset)
        
        # Обновляем изображение с поворотом
        angle = sin(self.time * 2) * 15
        self.image = pygame.transform.rotate(self.weapon_type.weapon_surf, angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Проверяем подбор оружия только после окончания кулдауна броска
        if current_time - self.throw_time >= self.throw_cooldown:
            for group in self.groups:
                for sprite in group:
                    if hasattr(sprite, 'weapons'):  # Ищем игрока
                        distance = pygame.math.Vector2(sprite.rect.center).distance_to(pygame.math.Vector2(self.rect.center))
                        if distance < self.pickup_radius and sprite.can_pickup_weapon():
                            if sprite.pickup_weapon(self.weapon_type):
                                self.kill()  # Удаляем предмет с карты
                            break
    
    def draw_effects(self, surface, offset):
        current_time = pygame.time.get_ticks()
        
        # Получаем позицию на экране с учетом смещения камеры
        screen_rect = self.rect.copy()
        screen_rect.topleft += offset
        
        # Рисуем подсветку
        glow_pos = (
            screen_rect.centerx - self.glow_radius,
            screen_rect.centery - self.glow_radius
        )
        surface.blit(self.glow_surface, glow_pos)
        
        # Проверяем расстояние до игрока и показываем зеленую подсветку только после кулдауна
        if current_time - self.throw_time >= self.throw_cooldown:
            for group in self.groups:
                for sprite in group:
                    if hasattr(sprite, 'weapons'):  # Ищем игрока
                        distance = pygame.math.Vector2(sprite.rect.center).distance_to(pygame.math.Vector2(self.rect.center))
                        if distance < self.pickup_radius and sprite.can_pickup_weapon():
                            # Рисуем подсветку подбора
                            pickup_pos = (
                                screen_rect.centerx - self.pickup_radius,
                                screen_rect.centery - self.pickup_radius
                            )
                            surface.blit(self.pickup_glow_surface, pickup_pos)
                        break
        
        # Рисуем оружие
        angle = sin(self.time * 2) * 15
        rotated_image = pygame.transform.rotate(self.weapon_type.weapon_surf, angle)
        rotated_rect = rotated_image.get_rect(center=screen_rect.center)
        surface.blit(rotated_image, rotated_rect) 