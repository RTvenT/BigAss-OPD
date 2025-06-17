import pygame
import math
from os.path import join
from .enemy import Enemy

from core import WINDOW_WIDTH, WINDOW_HEIGHT


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
        self.max_health = 1000  # Увеличено с 300 до 1000
        self.health = self.max_health
        self.speed = 150  # Оставляем прежней
        self.damage = 50  # Увеличено с 25 до 50
        self.attack_cooldown = 1500  # Уменьшено с 2000 до 1500 (быстрее атакует)
        
        # Увеличенная полоска HP для босса
        self.hp_bar_width = 200  # Увеличено с 120 до 200
        self.hp_bar_height = 15   # Увеличено с 10 до 15
        
        # Применяем множители сложности
        difficulty = self.player.game.difficulty if hasattr(self.player, 'game') else 1
        difficulty_multipliers = {
            0: {'health': 0.5, 'damage': 0.5},  # Легко
            1: {'health': 1.0, 'damage': 1.0},  # Средне
            2: {'health': 1.5, 'damage': 2.0}   # Сложно
        }
        
        self.health = int(self.health * difficulty_multipliers[difficulty]['health'])
        self.max_health = self.health
        self.damage = int(self.damage * difficulty_multipliers[difficulty]['damage'])

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
                            damage_text = font.render(f"-{self.hit_damage}", True, (255, 255, 255))
                            
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
                    
                    print(f"Drawing HP bar at {bar_rect.topleft}, health={self.health}/{self.max_health}, width={health_width}")
            except Exception as e:
                print(f"Error drawing HP bar: {e}")

    def take_damage(self, amount):
        """Получение урона"""
        if self.death_time == 0:  # Проверяем, что босс еще жив
            self.health -= amount
            print(f"Босс получил {amount} урона. Осталось здоровья: {self.health}")  # Для отладки
            
            # Создаем эффект попадания
            self.hit_effect_time = pygame.time.get_ticks()
            self.hit_effect_duration = 300  # Длительность эффекта
            self.hit_damage = amount  # Сохраняем урон для отображения
            
            # Создаем очень легкую вспышку
            self.original_image = self.image.copy()
            self.image = self.original_image.copy()
            
            # Создаем маску из текущего изображения
            mask = pygame.mask.from_surface(self.image)
            bright_overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            
            # Заполняем только те пиксели, где есть спрайт
            for x in range(self.image.get_width()):
                for y in range(self.image.get_height()):
                    if mask.get_at((x, y)):
                        # Получаем текущий цвет пикселя
                        current_color = self.image.get_at((x, y))
                        # Увеличиваем яркость
                        r = min(255, current_color[0] + 100)
                        g = min(255, current_color[1] + 100)
                        b = min(255, current_color[2] + 100)
                        bright_overlay.set_at((x, y), (r, g, b, current_color[3]))
            
            # Накладываем яркую маску
            self.image.blit(bright_overlay, (0, 0))
            
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