from settings import *
from math import atan2, degrees, sin
from os.path import join
import random


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.ground = True


class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)


class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        # player connection
        self.player = player
        self.base_distance = 50  # Базовое расстояние от игрока
        self.distance = self.base_distance
        self.player_direction = pygame.Vector2(0, 1)
        self.target_direction = pygame.Vector2(0, 1)
        
        # Параметры плавного движения
        self.smoothing = 1  # Коэффициент плавности (меньше = плавнее)
        self.floating_offset = 0  # Смещение для эффекта "плавания"
        self.floating_speed = 3  # Скорость плавания
        self.time = 0  # Время для синусоиды

        # sprite setup
        super().__init__(groups)
        self.image = self.player.current_weapon.weapon_surf
        self.rect = self.image.get_frect(center=self.player.rect.center + self.player_direction * self.distance)

    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        raw_direction = mouse_pos - player_pos

        if raw_direction.length_squared() == 0:
            self.target_direction = pygame.Vector2(0, -1)  # по умолчанию — вверх
        else:
            self.target_direction = raw_direction.normalize()

        # Плавное изменение направления
        direction_diff = self.target_direction - self.player_direction
        self.player_direction += direction_diff * self.smoothing

        # Если после сглаживания вектор стал нулевым (на всякий случай), тоже застрахуемся
        if self.player_direction.length_squared() == 0:
            self.player_direction = pygame.Vector2(0, -1)
        else:
            self.player_direction = self.player_direction.normalize()

    def update_floating(self, dt):
        # Обновляем время
        self.time += dt * self.floating_speed
        
        # Создаем эффект плавания с помощью синусоиды
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
        
        # Обновляем позицию с учетом плавающего эффекта
        target_pos = self.player.rect.center + self.player_direction * self.distance
        current_pos = pygame.Vector2(self.rect.center)
        new_pos = current_pos + (pygame.Vector2(target_pos) - current_pos) * self.smoothing
        self.rect.center = new_pos


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
        self.original_pos = pygame.Vector2(pos)  # Сохраняем начальную позицию

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt

        # Проверяем расстояние от начальной позиции
        current_pos = pygame.Vector2(self.rect.center)
        if (current_pos - self.original_pos).length() > 1000:  # Максимальная дистанция полета
            self.kill()
            return

        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(groups)
        
        # animation
        self.frames = frames
        self.frame_index = 0
        self.animation_speed = 15
        
        self.image = self.frames[self.frame_index]
        self.original_image = self.image.copy()
        self.rect = self.image.get_frect(center=pos)
        
        # Определяем тип врага по имени файла
        self.enemy_type = self._determine_enemy_type()
        
        # movement
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2()
        self.speed = 175
        
        # collisions - одинаковый хитбокс для всех врагов
        self.hitbox_rect = self.rect.inflate(-self.rect.width * 0.5, -self.rect.height * 0.5)
        self.collision_sprites = collision_sprites
        
        # player interaction
        self.player = player
        self.death_time = 0
        self.death_duration = 600
        self.damage = 10
        self.attack_cooldown = 1000
        self.last_attack = 0
        
        # health system
        self.max_health = 30
        self.health = self.max_health
        
        # Создаем круглую маску для коллизий
        self.mask_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.circle(self.mask_surface, (255, 255, 255, 255), 
                         (self.rect.width // 2, self.rect.height // 2), 
                         min(self.rect.width, self.rect.height) // 2)
        self.mask = pygame.mask.from_surface(self.mask_surface)
        
        # HP bar
        self.hp_bar_width = 32
        self.hp_bar_height = 3

    def _determine_enemy_type(self):
        """Определяем тип врага по имени файла спрайта"""
        try:
            image_path = self.frames[0].get_view().raw
            if 'bat' in str(image_path).lower():
                return 'bat'
            elif 'slime' in str(image_path).lower():
                return 'slime'
            else:
                return 'skeleton'
        except:
            return 'skeleton'  # По умолчанию

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
                print(f"Враг атакует! Здоровье игрока: {self.player.health}")  # для отладки

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
        if self.death_time == 0:
            # Позиция полоски HP над врагом
            bar_pos = pygame.math.Vector2(
                self.rect.centerx - self.hp_bar_width // 2,
                self.rect.top - 8
            ) - offset
            
            # Черная обводка
            pygame.draw.rect(surface, (0, 0, 0), 
                           (bar_pos.x - 1, bar_pos.y - 1, 
                            self.hp_bar_width + 2, self.hp_bar_height + 2))
            
            # Зеленая полоска здоровья
            health_width = int(self.hp_bar_width * (self.health / self.max_health))
            if health_width > 0:
                pygame.draw.rect(surface, (0, 255, 0), 
                               (bar_pos.x, bar_pos.y, health_width, self.hp_bar_height))

    def take_damage(self, amount):
        """Получение урона"""
        if self.death_time == 0:  # Проверяем, что враг еще жив
            self.health -= amount
            print(f"Враг получил {amount} урона. Осталось здоровья: {self.health}")  # Для отладки
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
                    # Заполняем внутреннюю часть белым цветом
                    pygame.draw.polygon(death_surf, (255, 255, 255, 180), outline)
                    
                # Создаем точную копию спрайта в белом цвете
                sprite_surf = mask.to_surface(setcolor=(255, 255, 255, 180), unsetcolor=(0, 0, 0, 0))
                death_surf.blit(sprite_surf, (0, 0))
                
                # Сохраняем изображение для анимации
                self.death_image = death_surf
                self.image = self.death_image
                
            except Exception as e:
                print(f"Ошибка при создании эффекта смерти: {e}")
                # Если что-то пошло не так, просто делаем спрайт белым
                self.death_image = self.image.copy()
                self.death_image.fill((255, 255, 255, 180))
                self.image = self.death_image

    def death_timer(self):
        """Обработка анимации смерти"""
        if self.death_time > 0:
            current_time = pygame.time.get_ticks()
            if current_time - self.death_time >= self.death_duration:
                self.kill()
            else:
                # Вычисляем прогресс анимации смерти
                progress = (current_time - self.death_time) / self.death_duration
                
                # Плавное затухание
                alpha = int(255 * (1 - progress))
                
                # Создаем новое изображение с текущей прозрачностью
                new_image = self.death_image.copy()
                new_image.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
                self.image = new_image

    def update(self, dt):
        if self.death_time == 0:
            self.move(dt)
            self.animate(dt)
            self.attack()
            self.update_mask()
        else:
            self.death_timer()

    def draw_hitbox(self, surface, offset):
        rect_with_offset = self.hitbox_rect.copy()
        rect_with_offset.topleft += offset
        pygame.draw.rect(surface, (255, 0, 0), rect_with_offset, 2)  # красный контур толщиной 2 пикселя


class Boss(Enemy):
    def __init__(self, pos, groups, player, collision_sprites):
        # Загружаем изображение босса
        self.boss_image = pygame.image.load(join('..', 'images', 'enemies', 'Boss', 'Boss_Tim.png')).convert_alpha()
        # Устанавливаем размер босса
        self.boss_image = pygame.transform.scale(self.boss_image, (128, 128))
        frames = [self.boss_image]
        
        # Загружаем иконку босса
        try:
            self.icon = pygame.image.load(join('..', 'images', 'enemies', 'Boss', 'boss_icon.png')).convert_alpha()
            self.icon = pygame.transform.scale(self.icon, (16, 16))  # делаем иконку совсем маленькой
        except:
            print("Не удалось загрузить иконку босса")
            self.icon = None
        
        super().__init__(pos, frames, groups, player, collision_sprites)
        
        # Особые характеристики босса
        self.max_health = 300
        self.health = self.max_health
        self.speed = 150
        self.damage = 25
        self.attack_cooldown = 2000
        
        # Увеличенная полоска HP для босса
        self.hp_bar_width = 100  # делаем полоску пошире
        self.hp_bar_height = 8   # и повыше

    def draw_hp_bar(self, surface, offset):
        if self.death_time == 0:
            # Позиция полоски HP над врагом
            bar_pos = pygame.math.Vector2(
                self.rect.centerx - self.hp_bar_width // 2,
                self.rect.top - 12  # поднимаем повыше из-за иконки
            ) - offset
            
            # Рисуем иконку над полоской здоровья
            if self.icon:
                icon_pos = (bar_pos.x + self.hp_bar_width // 2 - 8, bar_pos.y - 20)  # центрируем иконку
                surface.blit(self.icon, icon_pos)
            
            # Черная обводка
            pygame.draw.rect(surface, (0, 0, 0), 
                           (bar_pos.x - 1, bar_pos.y - 1, 
                            self.hp_bar_width + 2, self.hp_bar_height + 2))
            
            # Зеленая полоска здоровья
            health_width = int(self.hp_bar_width * (self.health / self.max_health))
            if health_width > 0:
                pygame.draw.rect(surface, (0, 255, 0), 
                               (bar_pos.x, bar_pos.y, health_width, self.hp_bar_height))