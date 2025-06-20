import pygame
import math
import random
from random import random, choice

from core import WINDOW_WIDTH, WINDOW_HEIGHT
from weapons import AutoRifle, Pistol, Shotgun, WeaponItem


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(groups)
        
        # Сохраняем ссылку на группу all_sprites
        self.all_sprites = groups[0] if isinstance(groups, (list, tuple)) else groups
        
        # animation
        self.frames = frames
        self.frame_index = 0
        self.animation_speed = 15
        
        self.image = self.frames[self.frame_index]
        self.original_image = self.image.copy()
        self.rect = self.image.get_frect(center=pos)
        
        # Определяем тип врага по имени файла
        self.enemy_type = self._determine_enemy_type(frames[0] if frames else None)
        
        # movement
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2()
        
        # collisions - одинаковый хитбокс для всех врагов
        self.hitbox_rect = self.rect.inflate(-self.rect.width * 0.6, -self.rect.height * 0.6)
        self.collision_sprites = collision_sprites
        
        # player interaction
        self.player = player
        self.death_time = 0
        self.death_duration = 600
        self.last_attack = 0
        
        # Создаем круглую маску для коллизий
        self.mask_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.circle(self.mask_surface, (255, 255, 255, 255), 
                         (self.rect.width // 2, self.rect.height // 2), 
                         min(self.rect.width, self.rect.height) // 2)
        self.mask = pygame.mask.from_surface(self.mask_surface)
        
        # HP bar
        self.hp_bar_width = 48  # Увеличиваем ширину
        self.hp_bar_height = 6  # Увеличиваем высоту
        
        # Опыт за убийство
        self.experience_reward = self._get_experience_reward()
        
        # Шансы дропа оружия
        self.weapon_drop_chance = 0.3  # Увеличиваем до 30%
        self.possible_weapons = [AutoRifle, Shotgun]  # Убираем пистолет из списка дропа

    def _determine_enemy_type(self, image):
        """Определяет тип врага по имени класса"""
        return self.__class__.__name__

    def _get_experience_reward(self):
        """Возвращает количество опыта за убийство в зависимости от типа врага"""
        if self.enemy_type == 'Boss':
            return 50
        elif self.enemy_type == 'Bat':
            return 5
        elif self.enemy_type == 'Slime':
            return 10
        elif self.enemy_type == 'Skeleton':
            return 10
        return 5  # По умолчанию

    def update_mask(self):
        """Обновляем маску при каждом обновлении спрайта"""
        self.mask = pygame.mask.from_surface(self.mask_surface)
        self.mask_rect = self.mask_surface.get_rect(center=self.rect.center)

    def check_bullet_collision(self, bullet):
        """Проверяем попадание пули с использованием маски"""
        if not self.death_time:
            # Получаем относительное смещение между пулей и врагом
            offset_x = bullet.rect.x - self.rect.x
            offset_y = bullet.rect.y - self.rect.y
            
            # Создаем маску для текущего кадра
            self.mask = pygame.mask.from_surface(self.image)
            bullet_mask = pygame.mask.from_surface(bullet.image)
            
            # Проверяем пересечение масок
            if self.mask.overlap(bullet_mask, (offset_x, offset_y)):
                return True
        return False

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, dt):
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        direction_vector = player_pos - enemy_pos
        
        # Проверяем, не находится ли враг точно на позиции игрока
        if direction_vector.length() == 0:
            # Если да, слегка смещаем врага в случайном направлении
            self.direction = pygame.Vector2(1, 0).rotate(random.randint(0, 360))
        else:
            self.direction = direction_vector.normalize()

        # Двигаемся по осям отдельно для лучшей коллизии
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')

        self.rect.center = self.hitbox_rect.center

    def attack(self):
        current_time = pygame.time.get_ticks()
        # Проверяем расстояние до игрока для атаки (немного больше чем hitbox)
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        distance = player_pos.distance_to(enemy_pos)

        # Атакуем если враг достаточно близко (в пределах 80 пикселей)
        if distance <= 100:
            if current_time - self.last_attack >= self.attack_cooldown:
                self.player.health -= self.damage
                self.last_attack = current_time
                # print(f"Враг атакует! Здоровье игрока: {self.player.health}")  # для отладки

    def collision(self, direction):
        # Коллизия с окружением
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top

        # Коллизия с игроком - враг не должен заходить в игрока
        if self.hitbox_rect.colliderect(self.player.hitbox_rect):
            if direction == 'horizontal':
                if self.direction.x > 0:
                    self.hitbox_rect.right = self.player.hitbox_rect.left
                elif self.direction.x < 0:
                    self.hitbox_rect.left = self.player.hitbox_rect.right
            else:  # vertical
                if self.direction.y > 0:
                    self.hitbox_rect.bottom = self.player.hitbox_rect.top
                elif self.direction.y < 0:
                    self.hitbox_rect.top = self.player.hitbox_rect.bottom

    def draw_hp_bar(self, surface, offset):
        if self.death_time == 0:  # Рисуем полоску здоровья только для живых врагов
            try:
                # Создаем копию rect для полоски здоровья
                bar_rect = pygame.Rect(
                    self.rect.centerx - self.hp_bar_width // 2,
                    self.rect.top - 15,
                    self.hp_bar_width,
                    self.hp_bar_height
                )
                
                # Применяем смещение камеры
                bar_rect.topleft += offset
                
                # Проверяем, находится ли полоска в пределах экрана
                if (0 <= bar_rect.x <= WINDOW_WIDTH and 
                    0 <= bar_rect.y <= WINDOW_HEIGHT):
                    
                    # Красная полоска фона (максимальное здоровье)
                    pygame.draw.rect(surface, (255, 0, 0), bar_rect)
                    
                    # Зеленая полоска текущего здоровья
                    health_width = int(self.hp_bar_width * (self.health / self.max_health))
                    if health_width > 0:
                        health_rect = bar_rect.copy()
                        health_rect.width = health_width
                        pygame.draw.rect(surface, (0, 255, 0), health_rect)
                    
                    # Золотая обводка
                    pygame.draw.rect(surface, (255, 215, 0), 
                                   (bar_rect.x - 1, bar_rect.y - 1, 
                                    bar_rect.width + 2, bar_rect.height + 2), 2)
                    
                    # Отображаем урон, если есть эффект попадания
                    if hasattr(self, 'hit_effect_time'):
                        current_time = pygame.time.get_ticks()
                        if current_time - self.hit_effect_time < self.hit_effect_duration:
                            # Создаем текст с уроном
                            font = pygame.font.Font(None, 24)
                            damage_text = font.render(f"-{self.hit_damage}", True, (220, 20, 60))
                            
                            # Позиция текста над полоской здоровья
                            text_pos = (bar_rect.centerx - damage_text.get_width() // 2,
                                      bar_rect.y - 20)
                            
                            # Добавляем тень для лучшей видимости
                            shadow = font.render(f"-{self.hit_damage}", True, (0, 0, 0))
                            surface.blit(shadow, (text_pos[0] + 1, text_pos[1] + 1))
                            surface.blit(damage_text, text_pos)
                            
                            # Рисуем красные палочки
                            if hasattr(self, 'hit_lines'):
                                progress = (current_time - self.hit_effect_time) / self.hit_effect_duration
                                alpha = int(255 * (1 - progress))  # Плавное затухание
                                
                                for start, end in self.hit_lines:
                                    # Применяем смещение камеры к позиции палочек
                                    start_pos = (start[0] + self.rect.x + offset[0], 
                                               start[1] + self.rect.y + offset[1])
                                    end_pos = (end[0] + self.rect.x + offset[0], 
                                             end[1] + self.rect.y + offset[1])
                                    
                                    # Рисуем палочку с затухающей прозрачностью
                                    pygame.draw.line(surface, (255, 50, 50, alpha), 
                                                   start_pos, end_pos, 3)  # Увеличили толщину и сделали красный цвет ярче
                    
                    # print(f"Drawing HP bar at {bar_rect.topleft}, health={self.health}/{self.max_health}, width={health_width}")
            except Exception as e:
                # print(f"Error drawing HP bar: {e}")
                pass

    def take_damage(self, amount):
        """Получение урона"""
        if self.death_time == 0:  # Проверяем, что враг еще жив
            self.health -= amount
            # print(f"Враг получил {amount} урона. Осталось здоровья: {self.health}")  # Для отладки
            
            # Создаем эффект попадания
            self.hit_effect_time = pygame.time.get_ticks()
            self.hit_effect_duration = 300  # Длительность эффекта
            self.hit_damage = amount  # Сохраняем урон для отображения
            
            # Создаем очень легкую вспышку
            self.original_image = self.image.copy()
            self.image = self.original_image.copy()
            
            # Создаем маску из текущего изображения
            mask = pygame.mask.from_surface(self.image)
            dark_overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            
            # Заполняем только те пиксели, где есть спрайт
            for x in range(self.image.get_width()):
                for y in range(self.image.get_height()):
                    if mask.get_at((x, y)):
                        # Получаем текущий цвет пикселя
                        current_color = self.image.get_at((x, y))
                        # Уменьшаем яркость
                        r = max(0, current_color[0] - 100)
                        g = max(0, current_color[1] - 100)
                        b = max(0, current_color[2] - 100)
                        dark_overlay.set_at((x, y), (r, g, b, current_color[3]))
            
            # Накладываем темную маску
            self.image.blit(dark_overlay, (0, 0))
            
            # Создаем красные палочки
            self.hit_lines = []
            center_x = self.rect.width / 2
            center_y = self.rect.height / 2
            
            # Создаем 4 палочки, направленные к центру по диагоналям
            for angle in [45, 135, 225, 315]:  # Палочки по диагоналям
                # Начальная точка на краю спрайта
                start_x = center_x + 20 * math.cos(math.radians(angle))
                start_y = center_y + 20 * math.sin(math.radians(angle))
                
                # Конечная точка ближе к центру
                end_x = center_x + 8 * math.cos(math.radians(angle))
                end_y = center_y + 8 * math.sin(math.radians(angle))
                
                self.hit_lines.append(((start_x, start_y), (end_x, end_y)))
            
            if self.health <= 0:
                if hasattr(self.player, 'hud'):
                    self.player.hud.add_kill()
                self.destroy()

    def destroy(self):
        """Создаем эффект силуэта при смерти"""
        if self.death_time == 0:
            self.death_time = pygame.time.get_ticks()
            try:
                # Создаем маску из текущего изображения врага
                mask = pygame.mask.from_surface(self.image)
                # Создаем поверхность для силуэта точно такого же размера
                death_surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
                
                # Получаем контур маски
                outline = mask.outline()
                if outline:
                    # Заполняем внутреннюю часть черным цветом
                    pygame.draw.polygon(death_surf, (0, 0, 0, 180), outline)
                    
                # Создаем точную копию спрайта в черном цвете
                sprite_surf = mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
                death_surf.blit(sprite_surf, (0, 0))
                
                # Сохраняем изображение для анимации
                self.death_image = death_surf
                self.image = self.death_image
                
                # Добавляем опыт игроку
                if hasattr(self.player, 'add_experience'):
                    self.player.add_experience(self.experience_reward)
            except Exception as e:
                # print(f"Ошибка при создании эффекта смерти: {e}")
                # Если что-то пошло не так, просто делаем спрайт черным
                self.death_image = self.image.copy()
                self.death_image.fill((0, 0, 0, 180))
                self.image = self.death_image

    def death_timer(self):
        """Обработка смерти врага"""
        if self.death_time > 0:
            current_time = pygame.time.get_ticks()
            if current_time - self.death_time >= self.death_duration:
                # Проверяем шанс дропа оружия перед удалением врага
                roll = random()
                print(f"[DEBUG] Enemy death - Weapon drop roll: {roll:.2f} (need < {self.weapon_drop_chance})")
                if roll < self.weapon_drop_chance:
                    # Фильтруем список возможного оружия, исключая те, что уже есть у игрока
                    available_weapons = []
                    for weapon_class in self.possible_weapons:
                        # Проверяем есть ли оружие такого типа у игрока
                        weapon_exists = False
                        for player_weapon in self.player.weapons:
                            if isinstance(player_weapon, weapon_class):
                                weapon_exists = True
                                break
                        if not weapon_exists:
                            available_weapons.append(weapon_class)
                    
                    # Если есть доступное оружие, выбираем случайное из них
                    if available_weapons:
                        weapon_class = choice(available_weapons)
                        print(f"[DEBUG] Dropping weapon: {weapon_class.__name__} at position {self.rect.center}")
                        print(f"[DEBUG] Using all_sprites group: {self.all_sprites}")
                        
                        # Создаем оружие с временным игроком
                        class TempPlayer:
                            def __init__(self):
                                self.rect = pygame.Rect(0, 0, 32, 32)
                        
                        weapon = weapon_class(TempPlayer(), {'all': self.all_sprites, 'bullet': pygame.sprite.Group()})
                        print(f"[DEBUG] Created weapon: {weapon.__class__.__name__}")
                        
                        # Создаем WeaponItem на месте смерти врага
                        weapon_item = WeaponItem(weapon, self.rect.center, self.all_sprites)
                        print(f"[DEBUG] Created WeaponItem: {weapon_item} in group {weapon_item.groups}")
                
                # Удаляем врага
                self.kill()
            else:
                # Вычисляем прогресс анимации смерти
                progress = (current_time - self.death_time) / self.death_duration
                
                # Плавное затухание
                alpha = int(255 * (1 - progress))
                
                # Создаем новое изображение с текущей прозрачностью
                new_image = self.death_image.copy()
                new_image.fill((0, 0, 0, alpha), special_flags=pygame.BLEND_RGBA_MULT)
                self.image = new_image

    def update(self, dt):
        if self.death_time == 0:
            self.move(dt)
            self.animate(dt)
            self.attack()
            self.update_mask()
            
            # Обновляем эффект попадания
            if hasattr(self, 'hit_effect_time'):
                current_time = pygame.time.get_ticks()
                if current_time - self.hit_effect_time >= self.hit_effect_duration:
                    # Возвращаем нормальное изображение
                    if hasattr(self, 'original_image'):
                        self.image = self.original_image
                    delattr(self, 'hit_effect_time')
                else:
                    # Плавное затухание вспышки
                    progress = (current_time - self.hit_effect_time) / self.hit_effect_duration
                    brightness = int(100 * (1 - progress))  # Плавное уменьшение яркости
                    
                    self.image = self.original_image.copy()
                    mask = pygame.mask.from_surface(self.image)
                    dark_overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
                    
                    # Заполняем только те пиксели, где есть спрайт
                    for x in range(self.image.get_width()):
                        for y in range(self.image.get_height()):
                            if mask.get_at((x, y)):
                                # Получаем текущий цвет пикселя
                                current_color = self.original_image.get_at((x, y))
                                # Увеличиваем яркость с учетом прогресса
                                r = min(255, current_color[0] + brightness)
                                g = min(255, current_color[1] + brightness)
                                b = min(255, current_color[2] + brightness)
                                dark_overlay.set_at((x, y), (r, g, b, current_color[3]))
                    
                    self.image.blit(dark_overlay, (0, 0))
        else:
            self.death_timer()

    def draw_hitbox(self, surface, offset):
        rect_with_offset = self.hitbox_rect.copy()
        rect_with_offset.topleft += offset
        pygame.draw.rect(surface, (255, 0, 0), rect_with_offset, 2)  # красный контур толщиной 2 пикселя
