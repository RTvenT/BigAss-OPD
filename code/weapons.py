import pygame
from os.path import join
from sprites import Bullet
from math import sin, cos, radians
from random import random

class Weapon:
    def __init__(self, player, groups):
        self.player = player
        self.all_sprites = groups['all']
        self.bullet_sprites = groups['bullet']
        self.can_shoot = True
        self.shoot_time = 0
        self.player_direction = pygame.math.Vector2()
        self.rect = pygame.Rect(0, 0, 32, 32)  # Временный размер
        self.bullet_surf = pygame.image.load(join('..', 'images', 'gun', 'bullet.png')).convert_alpha()
        self.shoot_sound = pygame.mixer.Sound(join('..', 'audio', 'shoot.wav'))
        self.shoot_sound.set_volume(0.2)
        # Default weapon image
        self.weapon_surf = pygame.image.load(join('..', 'images', 'gun', 'gun.png')).convert_alpha()
        # Default damage
        self.damage = 30  # Увеличиваем базовый урон

    def shoot(self):
        if self.can_shoot:
            self.shoot_sound.play()
            self._create_bullets()
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def _create_bullets(self):
        # Переопределяется в подклассах
        pass

    def update_position(self, player_pos, direction):
        self.player_direction = direction
        self.rect.center = player_pos + direction * 50

    def update_timer(self, cooldown):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= cooldown:
                self.can_shoot = True

class Pistol(Weapon):
    def __init__(self, player, groups):
        super().__init__(player, groups)
        self.cooldown = 500  # Увеличенный кулдаун для пистолета
        self.weapon_surf = pygame.image.load(join('..', 'images', 'gun', 'gun.png')).convert_alpha()
        self.damage = 15  # Сильный урон с одного выстрела

    def _create_bullets(self):
        pos = self.rect.center + self.player_direction * 50
        Bullet(self.bullet_surf, pos, self.player_direction, (self.all_sprites, self.bullet_sprites))

class Shotgun(Weapon):
    def __init__(self, player, groups):
        super().__init__(player, groups)
        self.cooldown = 1000  # Больший кулдаун для дробовика
        self.spread = 30  # Разброс в градусах
        self.weapon_surf = pygame.image.load(join('..', 'images', 'gun', 'drobovik.png')).convert_alpha()
        self.damage = 20  # Меньше урон, но много пуль (5 пуль = 100 урона)

    def _create_bullets(self):
        base_pos = self.rect.center + self.player_direction * 50
        base_angle = pygame.math.Vector2().angle_to(self.player_direction)
        
        for angle_offset in [-self.spread, -self.spread/2, 0, self.spread/2, self.spread]:
            # Поворачиваем базовое направление на угол отклонения
            angle = base_angle + angle_offset
            rad = radians(angle)
            direction = pygame.math.Vector2(cos(rad), sin(rad))
            Bullet(self.bullet_surf, base_pos, direction, (self.all_sprites, self.bullet_sprites))

class Sword(Weapon):
    def __init__(self, player, groups):
        super().__init__(player, groups)
        self.cooldown = 400  # Быстрые атаки для меча
        self.damage_rect = pygame.Rect(0, 0, 100, 50)  # Область урона

    def _create_bullets(self):
        # Меч не создает пули, вместо этого проверяет коллизии в области удара
        # Логика атаки будет реализована в player.py
        pass

class AutoRifle(Weapon):
    def __init__(self, player, groups):
        super().__init__(player, groups)
        self.cooldown = 100  # Очень быстрая стрельба
        self.weapon_surf = pygame.image.load(join('..', 'images', 'gun', 'avtomat.png')).convert_alpha()
        self.damage = 25  # Средний урон, но высокая скорострельность

    def _create_bullets(self):
        pos = self.rect.center + self.player_direction * 50
        # Добавляем небольшой случайный разброс
        angle = pygame.math.Vector2().angle_to(self.player_direction)
        spread = 5  # Разброс в градусах
        angle += (random() - 0.5) * spread
        rad = radians(angle)
        direction = pygame.math.Vector2(cos(rad), sin(rad))
        Bullet(self.bullet_surf, pos, direction, (self.all_sprites, self.bullet_sprites)) 