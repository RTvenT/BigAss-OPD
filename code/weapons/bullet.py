import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000

        self.direction = direction
        self.speed = 1200
        self.original_pos = pygame.Vector2(pos)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt

        # Проверяем расстояние от начальной позиции
        current_pos = pygame.Vector2(self.rect.center)
        if (current_pos - self.original_pos).length() > 1000:  # Максимальная дистанция полета
            self.kill()
            return

        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill() 