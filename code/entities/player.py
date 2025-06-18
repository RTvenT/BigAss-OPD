import pygame
import os

from weapons import Pistol, Shotgun, Sword, AutoRifle, GunSprite, Bullet
from core import WINDOW_WIDTH, WINDOW_HEIGHT


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, enemy_sprites, game=None):
        super().__init__(groups)
        
        # Сохраняем ссылку на игру
        self.game = game
        
        # animation setup
        self.import_assets()
        self.state = 'down'
        self.frame_index = 0
        self.animation_speed = 8  # Увеличиваем скорость анимации
        
        # sprite setup
        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_frect(center=pos)
        self.hitbox_rect = self.rect.inflate(-60, -90)
        
        # movement
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2()
        self.speed = 500
        
        # collision
        self.collision_sprites = collision_sprites
        self.enemy_sprites = enemy_sprites
        
        # stats
        self.health = 1000
        self.alive = True
        self.death_time = 0
        
        # Система уровней и опыта
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 300  # Базовое количество опыта для 2 уровня
        
        # weapon system
        self.bullet_sprites = pygame.sprite.Group()
        self.weapons = [
            Pistol(self, {'all': groups, 'bullet': self.bullet_sprites}),
            Sword(self, {'all': groups, 'bullet': self.bullet_sprites}),
            AutoRifle(self, {'all': groups, 'bullet': self.bullet_sprites})
        ]
        self.current_weapon_index = 0
        self.current_weapon = self.weapons[self.current_weapon_index]
        # Сохраняем ссылку на all_sprites в оружии
        for weapon in self.weapons:
            weapon.all_sprites = groups  # Передаем сам объект groups
        self.gun = GunSprite(self, groups)

    def import_assets(self):
        """Импорт всех анимаций игрока"""
        self.animations = {'up': [], 'down': [], 'left': [], 'right': []}
        
        for animation in self.animations.keys():
            full_path = os.path.join('..', 'images', 'player', animation)
            try:
                self.animations[animation] = []
                for frame_file in sorted(os.listdir(full_path)):
                    if frame_file.endswith('.png'):
                        frame_path = os.path.join(full_path, frame_file)
                        frame_surf = pygame.image.load(frame_path).convert_alpha()
                        self.animations[animation].append(frame_surf)
            except Exception as e:
                print(f'Ошибка загрузки анимации {animation}: {e}')
                # Создаем временное изображение если загрузка не удалась
                temp_surf = pygame.Surface((64, 64))
                temp_surf.fill('red')
                self.animations[animation] = [temp_surf]

    def animate(self, dt):
        """Анимация игрока"""
        if not self.alive:
            return
            
        # Обновляем состояние только если движемся
        if self.direction.magnitude() != 0:
            # Определяем направление
            if abs(self.direction.x) > abs(self.direction.y):
                self.state = 'right' if self.direction.x > 0 else 'left'
            else:
                self.state = 'down' if self.direction.y > 0 else 'up'
                
            # Обновляем индекс кадра
            self.frame_index += self.animation_speed * dt
            if self.frame_index >= len(self.animations[self.state]):
                self.frame_index = 0
                
            # Устанавливаем новый кадр
            self.image = self.animations[self.state][int(self.frame_index)]
        else:
            # Если стоим на месте - используем первый кадр текущего направления
            self.frame_index = 0
            self.image = self.animations[self.state][0]

    def move(self, dt):
        if not self.alive:
            return

        # normalize vector
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Сохраняем старую позицию для проверки коллизий
        old_hitbox_x = self.hitbox_rect.x
        old_hitbox_y = self.hitbox_rect.y

        # horizontal movement
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')

        # vertical movement
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')

        # Обновляем позицию спрайта на основе hitbox
        self.rect.center = self.hitbox_rect.center

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)
        self.bullet_sprites.update(dt)
        self.check_death()
        
        if self.alive:
            weapon_dir = self.get_weapon_direction()
            self.current_weapon.update_position(pygame.math.Vector2(self.rect.center), weapon_dir)
            self.current_weapon.update_timer(self.current_weapon.cooldown)

    def input(self):
        if not self.alive:
            return

        keys = pygame.key.get_pressed()
        
        # Movement
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

        # Weapon switching
        if keys[pygame.K_1]:
            self.switch_weapon(0)
        elif keys[pygame.K_2]:
            self.switch_weapon(1)
        elif keys[pygame.K_3]:
            self.switch_weapon(2)

        # Shooting
        if pygame.mouse.get_pressed()[0]:
            self.current_weapon.shoot()

    def get_weapon_direction(self):
        mouse_pos = pygame.mouse.get_pos()
        screen_center = pygame.math.Vector2(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        direction = pygame.math.Vector2(mouse_pos) - screen_center

        if direction.length_squared() == 0:
            return pygame.math.Vector2(0, -1)  # По умолчанию пусть смотрит вверх
        return direction.normalize()

    def switch_weapon(self, index):
        if 0 <= index < len(self.weapons):
            self.current_weapon_index = index
            self.current_weapon = self.weapons[self.current_weapon_index]
            # Обновляем изображение оружия
            self.gun.image = self.current_weapon.weapon_surf

    def check_death(self):
        if self.health <= 0 and self.alive:
            self.alive = False
            self.death_time = pygame.time.get_ticks()

    def collision(self, direction):
        # Коллизия с окружением
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:  # moving right
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox_rect.left = sprite.rect.right

                if direction == 'vertical':
                    if self.direction.y > 0:  # moving down
                        self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox_rect.top = sprite.rect.bottom

        # Коллизия с врагами
        for enemy in self.enemy_sprites:
            if enemy.death_time == 0 and enemy.hitbox_rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:  # moving right
                        self.hitbox_rect.right = enemy.hitbox_rect.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox_rect.left = enemy.hitbox_rect.right

                if direction == 'vertical':
                    if self.direction.y > 0:  # moving down
                        self.hitbox_rect.bottom = enemy.hitbox_rect.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox_rect.top = enemy.hitbox_rect.bottom

    def draw_hitbox(self, surface, offset):
        rect_with_offset = self.hitbox_rect.copy()
        rect_with_offset.topleft += offset
        pygame.draw.rect(surface, (255, 0, 0), rect_with_offset, 2)

    def bullet_collision(self):
        # Проверяем коллизии для каждой пули
        for bullet in self.bullet_sprites.sprites():
            # Проверяем коллизии с врагами
            for enemy in self.enemy_sprites.sprites():
                if enemy.check_bullet_collision(bullet):
                    # Определяем тип оружия и урон
                    weapon_damage = {
                        'pistol': 15,  # 2 выстрела для убийства (30 HP / 15 = 2)
                        'drobovik': 10,  # 3 пули по 10 урона каждая
                        'avtomat': 12   # Быстрая стрельба, но меньше урон
                    }.get(self.current_weapon, 15)
                    
                    # print(f"Попадание из {self.current_weapon}, урон: {weapon_damage}")  # Для отладки
                    
                    # Наносим урон врагу
                    enemy.take_damage(weapon_damage)
                    
                    # Удаляем пулю только для пистолета и автомата
                    if self.current_weapon != 'drobovik':
                        bullet.kill()
                    break  # Прерываем проверку для этой пули, если попали во врага

    def add_experience(self, amount):
        """Добавляет опыт и проверяет повышение уровня"""
        self.experience += amount
        while self.experience >= self.experience_to_next_level:
            self.level_up()
    
    def level_up(self):
        """Повышает уровень персонажа"""
        self.level += 1
        self.experience -= self.experience_to_next_level
        self.experience_to_next_level = int(self.experience_to_next_level * 3)  # Увеличиваем требуемый опыт в 3 раза
        
        # Увеличиваем характеристики при повышении уровня
        self.health += 100  # Увеличиваем максимальное здоровье
        self.speed += 20    # Увеличиваем скорость
        
        # Обновляем текущее здоровье до максимума
        self.health = min(self.health, 2000)  # Ограничиваем максимальное здоровье
        
        # Обновляем урон оружия
        for weapon in self.weapons:
            weapon.damage = int(weapon.damage * 1.2)  # Увеличиваем урон на 20%