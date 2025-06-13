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
        self.rect = pygame.Rect(0, 0, 32, 32)
        self.bullet_surf = pygame.image.load(join('..', 'images', 'gun', 'bullet.png')).convert_alpha()
        self.shoot_sound = pygame.mixer.Sound(join('..', 'audio', 'shoot.wav'))
        self.shoot_sound.set_volume(0.2)
        # Default weapon image
        self.weapon_surf = pygame.image.load(join('..', 'images', 'gun', 'pistol.png')).convert_alpha()
        # Default damage
        self.damage = 30
        # Расстояние появления пуль от игрока
        self.bullet_spawn_distance = 30  # Уменьшаем с 50 до 30

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
        self.rect.center = player_pos + direction * self.bullet_spawn_distance

    def update_timer(self, cooldown):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= cooldown:
                self.can_shoot = True

class Pistol(Weapon):
    def __init__(self, player, groups):
        super().__init__(player, groups)
        self.cooldown = 500
        self.weapon_surf = pygame.image.load(join('..', 'images', 'gun', 'pistol.png')).convert_alpha()
        self.damage = 15
        self.bullet_spawn_distance = 25  # Для пистолета еще ближе

    def _create_bullets(self):
        pos = self.rect.center + self.player_direction * self.bullet_spawn_distance
        Bullet(self.bullet_surf, pos, self.player_direction, (self.all_sprites, self.bullet_sprites))

class Shotgun(Weapon):
    def __init__(self, player, groups):
        super().__init__(player, groups)
        self.cooldown = 500  # Больший кулдаун для дробовика
        self.spread = 30  # Разброс в градусах
        self.weapon_surf = pygame.image.load(join('..', 'images', 'gun', 'shotgun.png')).convert_alpha()
        self.weapon_surf = pygame.transform.rotozoom(self.weapon_surf, 0, 1.2)  # Увеличим на 20%
        self.damage = 30  # Меньше урон, но много пуль (5 пуль = 100 урона)

    def _create_bullets(self):
        base_pos = self.rect.center + self.player_direction * self.bullet_spawn_distance
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
        self.weapon_surf = pygame.image.load(join('..', 'images', 'gun', 'sword.png')).convert_alpha()
        self.damage = 100  # Увеличено с 50 до 100 (убивает всех с одного удара, кроме слизня)
        self.attack_range = 100  # Дальность атаки мечом
        self.attack_angle = 60  # Угол атаки в градусах
        self.attack_duration = 200  # Длительность атаки в миллисекундах
        self.attack_start_time = 0
        self.is_attacking = False
        self.show_attack_area = True  # Флаг для отображения области атаки
        self.attack_animation_duration = 200  # Длительность анимации в миллисекундах

    def draw_attack_area(self, surface):
        if not self.is_attacking:
            return

        current_time = pygame.time.get_ticks()
        animation_progress = (current_time - self.attack_start_time) / self.attack_animation_duration
        
        if animation_progress > 1:
            return

        # Получаем смещение камеры из all_sprites
        camera_offset = self.all_sprites.offset if hasattr(self.all_sprites, 'offset') else (0, 0)
        
        # Центр игрока с учетом смещения камеры
        player_center = pygame.math.Vector2(self.player.rect.center) + pygame.math.Vector2(camera_offset)
        
        # Вычисляем углы для сектора
        base_angle = pygame.math.Vector2().angle_to(self.player_direction)
        start_angle = base_angle - self.attack_angle / 2
        end_angle = base_angle + self.attack_angle / 2
        
        # Создаем поверхность с поддержкой прозрачности
        attack_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        
        # Анимируем прозрачность
        if animation_progress < 0.3:  # Первые 30% анимации - появление
            alpha = int(220 * (animation_progress / 0.3))
        else:  # Оставшиеся 70% - затухание
            alpha = int(220 * (1 - (animation_progress - 0.3) / 0.7))
        
        # Рисуем несколько секторов для создания эффекта волны
        num_waves = 3  # Количество волн
        for i in range(num_waves):
            wave_progress = (animation_progress + i * 0.2) % 1.0  # Смещаем каждую волну
            
            # Вычисляем текущий радиус волны
            current_radius = self.attack_range / 2 + (self.attack_range / 2 - self.attack_range / 4) * wave_progress
            
            # Рисуем сектор для текущей волны
            points = []
            
            # Добавляем точки для текущей волны
            for angle in range(int(start_angle), int(end_angle) + 1):
                rad = radians(angle)
                x = player_center.x + cos(rad) * current_radius
                y = player_center.y + sin(rad) * current_radius
                points.append((x, y))
            
            # Добавляем точки для внешнего края сектора
            for angle in range(int(end_angle), int(start_angle) - 1, -1):
                rad = radians(angle)
                x = player_center.x + cos(rad) * (current_radius + 25)  # Увеличили ширину волны до 25 пикселей
                y = player_center.y + sin(rad) * (current_radius + 25)
                points.append((x, y))
            
            if len(points) > 2:
                # Вычисляем прозрачность для текущей волны
                wave_alpha = int(alpha * (1 - wave_progress * 0.7))  # Уменьшили скорость затухания
                
                # Рисуем волну
                pygame.draw.polygon(attack_surface, (255, 50, 50, wave_alpha), points)
                pygame.draw.polygon(attack_surface, (255, 100, 100, min(255, wave_alpha + 50)), points, 2)  # Увеличили толщину обводки
        
        surface.blit(attack_surface, (0, 0))

    def _create_bullets(self):
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_start_time = pygame.time.get_ticks()
            
            # Создаем область атаки из центра персонажа
            attack_rect = pygame.Rect(0, 0, self.attack_range, self.attack_range)
            player_center = pygame.math.Vector2(self.player.rect.center)
            attack_rect.center = player_center + self.player_direction * (self.attack_range / 2)
            
            # Проверяем попадание по врагам
            for enemy in self.player.enemy_sprites:
                if attack_rect.colliderect(enemy.rect):
                    # Проверяем, находится ли враг в пределах угла атаки
                    enemy_dir = pygame.math.Vector2(enemy.rect.center) - player_center
                    angle = self.player_direction.angle_to(enemy_dir)
                    if abs(angle) <= self.attack_angle / 2:
                        enemy.take_damage(self.damage)

    def update_timer(self, cooldown):
        current_time = pygame.time.get_ticks()
        
        # Проверяем окончание атаки
        if self.is_attacking and current_time - self.attack_start_time >= self.attack_duration:
            self.is_attacking = False
            
        # Проверяем кулдаун
        if not self.can_shoot:
            if current_time - self.shoot_time >= cooldown:
                self.can_shoot = True

class AutoRifle(Weapon):
    def __init__(self, player, groups):
        super().__init__(player, groups)
        self.cooldown = 100
        self.weapon_surf = pygame.image.load(join('..', 'images', 'gun', 'auto-rifle.png')).convert_alpha()
        self.damage = 35
        self.bullet_spawn_distance = 30  # Стандартное расстояние для автомата

    def _create_bullets(self):
        pos = self.rect.center + self.player_direction * self.bullet_spawn_distance
        # Добавляем небольшой случайный разброс
        angle = pygame.math.Vector2().angle_to(self.player_direction)
        spread = 5  # Разброс в градусах
        angle += (random() - 0.5) * spread
        rad = radians(angle)
        direction = pygame.math.Vector2(cos(rad), sin(rad))
        Bullet(self.bullet_surf, pos, direction, (self.all_sprites, self.bullet_sprites)) 