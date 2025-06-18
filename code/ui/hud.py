import pygame
from os.path import join

from core import WINDOW_WIDTH, WINDOW_HEIGHT


class HUD:
    def __init__(self, player=None):
        self.player = player
        self.segment_width = 20
        self.segment_height = 10
        self.gap = 4
        self.segments_total = 10  # 10 сегментов = 100 HP

        self.x = 10
        self.y = 10

        self.bg_color = (40, 40, 40)
        self.filled_color = (200, 0, 0)
        self.empty_color = (60, 60, 60)
        self.exp_color = (0, 200, 0)  # Зеленый цвет для полоски опыта

        self.font = pygame.font.Font(None, 24)
        self.timer_font = pygame.font.Font(None, 36)  # Больший шрифт для таймера
        self.boss_font = pygame.font.Font(None, 48)  # Ещё больший шрифт для босса
        self.level_font = pygame.font.Font(None, 32)  # Шрифт для уровня

        # Время начала игры
        self.start_time = pygame.time.get_ticks()
        self.game_time = 0  # Текущее время игры

        # Счетчик убийств
        self.kills = 0

        # Время до следующего босса
        self.time_until_boss = 30

        # Инвентарь оружия
        self.weapon_slot_size = 48  # Уменьшили размер слота
        self.weapon_slot_gap = 8    # Уменьшили промежуток между слотами
        self.weapon_slots_y = WINDOW_HEIGHT - 80  # Подняли слоты выше
        self.weapon_names = {
            'Pistol': 'Пистолет',
            'Sword': 'Меч',
            'AutoRifle': 'Автомат'
        }
        # print("HUD инициализирован, kills =", self.kills)  # Отладка

    def update(self):
        """Обновляем время игры"""
        if not self.player or not self.player.alive:
            return
        current_time = pygame.time.get_ticks()
        self.game_time = (current_time - self.start_time) // 1000

    def get_survival_time(self):
        """Возвращает время выживания в секундах"""
        return self.game_time

    def add_kill(self):
        """Увеличивает счетчик убийств"""
        self.kills += 1
        # print(f"Убито врагов: {self.kills}")  # Добавим для отладки

    def format_time(self, seconds):
        """Форматирует время в MM:SS"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def reset(self):
        """Сбрасывает таймер и счетчик убийств"""
        self.start_time = pygame.time.get_ticks()
        self.game_time = 0
        self.kills = 0

    def draw_weapon_slots(self, surface):
        if not self.player or not hasattr(self.player, 'weapons'):
            return

        # Рисуем слоты для оружия внизу экрана
        center_x = surface.get_width() // 2
        start_x = center_x - (self.weapon_slot_size * 1.5 + self.weapon_slot_gap)

        # Фон для всех слотов
        slots_bg_width = (self.weapon_slot_size * 3) + (self.weapon_slot_gap * 2) + 10
        slots_bg_height = self.weapon_slot_size + 10
        slots_bg_rect = pygame.Rect(
            center_x - slots_bg_width // 2,
            self.weapon_slots_y - 5,
            slots_bg_width,
            slots_bg_height
        )
        pygame.draw.rect(surface, (20, 20, 20), slots_bg_rect)
        pygame.draw.rect(surface, (40, 40, 40), slots_bg_rect, 1)

        for i in range(3):
            slot_x = start_x + i * (self.weapon_slot_size + self.weapon_slot_gap)
            slot_rect = pygame.Rect(slot_x, self.weapon_slots_y, self.weapon_slot_size, self.weapon_slot_size)
            
            # Рисуем фон слота
            pygame.draw.rect(surface, (30, 30, 30), slot_rect)
            pygame.draw.rect(surface, (60, 60, 60), slot_rect, 1)

            # Если есть оружие в этом слоте
            if i < len(self.player.weapons):
                # Рисуем иконку оружия
                weapon = self.player.weapons[i]
                if hasattr(weapon, 'weapon_surf'):
                    weapon_image = pygame.transform.scale(weapon.weapon_surf, (36, 36))
                    image_rect = weapon_image.get_rect(center=slot_rect.center)
                    surface.blit(weapon_image, image_rect)

            # Если это активное оружие
            if hasattr(self.player, 'current_weapon_index') and i == self.player.current_weapon_index:
                pygame.draw.rect(surface, (200, 200, 0), slot_rect, 2)

    def draw_boss_timer(self, surface):
        if self.time_until_boss > 0:
            # Текст для таймера босса
            boss_text = f"Босс через: {self.time_until_boss}"
            boss_surface = self.timer_font.render(boss_text, True, (255, 50, 50, 128))  # Уменьшили непрозрачность

            # Размещаем в правом верхнем углу
            boss_x = surface.get_width() - boss_surface.get_width() - 20
            boss_y = 60

            # Фон для текста
            boss_bg = pygame.Rect(boss_x - 10, boss_y - 5,
                                boss_surface.get_width() + 20,
                                boss_surface.get_height() + 10)
            pygame.draw.rect(surface, (0, 0, 0, 64), boss_bg)  # Сделали фон более прозрачным
            pygame.draw.rect(surface, (255, 0, 0, 64), boss_bg, 1)  # Уменьшили толщину рамки и сделали её прозрачной

            surface.blit(boss_surface, (boss_x, boss_y))

    def draw_survival_time(self, surface):
        """Отрисовка времени выживания"""
        self.update()  # Обновляем время
        time_text = self.format_time(self.game_time)
        timer_surface = self.timer_font.render(time_text, True, (255, 255, 255))

        # Центрируем по горизонтали
        timer_x = (surface.get_width() - timer_surface.get_width()) // 2
        timer_y = 15  # Небольшой отступ сверху

        # Добавляем фон для лучшей читаемости
        timer_bg = pygame.Rect(timer_x - 10, timer_y - 5,
                            timer_surface.get_width() + 20,
                            timer_surface.get_height() + 10)
        pygame.draw.rect(surface, (0, 0, 0, 128), timer_bg)  # Полупрозрачный фон
        pygame.draw.rect(surface, (60, 60, 60), timer_bg, 2)  # Рамка

        surface.blit(timer_surface, (timer_x, timer_y))

    def draw(self, surface):
        if not self.player:
            return

        # Рисуем полоску здоровья
        self.draw_health_bar(surface)
        
        # Рисуем полоску опыта
        self.draw_experience_bar(surface)
        
        # Рисуем уровень
        self.draw_level(surface)

        # Рисуем время
        self.draw_time(surface)

        # Рисуем счетчик убийств
        self.draw_kills(surface)

        # Рисуем время до босса
        self.draw_boss_timer(surface)

        # Рисуем инвентарь оружия
        self.draw_weapon_slots(surface)

    def draw_health_bar(self, surface):
        # Рисуем полоску здоровья
        bar_width = 200
        bar_height = 20
        bar_x = self.x
        bar_y = self.y
        
        # Фон полоски
        pygame.draw.rect(surface, self.bg_color, (bar_x, bar_y, bar_width, bar_height))
        
        # Заполненная часть
        health_percent = self.player.health / self.player.max_health
        filled_width = int(bar_width * health_percent)
        pygame.draw.rect(surface, self.filled_color, (bar_x, bar_y, filled_width, bar_height))
        
        # Текст здоровья
        health_text = f"HP: {self.player.health}/{self.player.max_health}"
        text_surf = self.font.render(health_text, True, (0, 0, 0))  # Черный цвет
        surface.blit(text_surf, (bar_x + bar_width + 10, bar_y))

    def draw_experience_bar(self, surface):
        # Рисуем полоску опыта под полоской здоровья
        bar_width = 200
        bar_height = 10
        bar_x = self.x
        bar_y = self.y + 25  # Под полоской здоровья
        
        # Фон полоски
        pygame.draw.rect(surface, self.bg_color, (bar_x, bar_y, bar_width, bar_height))
        
        # Заполненная часть
        exp_percent = self.player.experience / self.player.experience_to_next_level
        filled_width = int(bar_width * exp_percent)
        pygame.draw.rect(surface, self.exp_color, (bar_x, bar_y, filled_width, bar_height))
        
        # Текст опыта
        exp_text = f"XP: {self.player.experience}/{self.player.experience_to_next_level}"
        text_surf = self.font.render(exp_text, True, (0, 0, 0))  # Черный цвет
        surface.blit(text_surf, (bar_x + bar_width + 10, bar_y))

    def draw_level(self, surface):
        # Рисуем уровень в левом краю экрана под полоской опыта
        level_text = f"LVL {self.player.level}"
        text_surf = self.level_font.render(level_text, True, (0, 0, 0))  # Черный цвет
        # Размещаем текст по левому краю экрана
        text_x = 10  # Отступ от левого края
        text_y = self.y + 40  # Под полоской опыта
        surface.blit(text_surf, (text_x, text_y))

    def draw_time(self, surface):
        self.draw_survival_time(surface)

    def draw_kills(self, surface):
        # Счетчик убийств в правом верхнем углу
        kills_text = f"Kills: {self.kills}"
        kills_surface = self.font.render(kills_text, True, (255, 255, 0))  # Желтый цвет

        kills_x = surface.get_width() - kills_surface.get_width() - 15
        kills_y = 15

        # Фон для счетчика убийств
        kills_bg = pygame.Rect(kills_x - 10, kills_y - 5,
                               kills_surface.get_width() + 20,
                               kills_surface.get_height() + 10)
        pygame.draw.rect(surface, (0, 0, 0, 128), kills_bg)
        pygame.draw.rect(surface, (60, 60, 60), kills_bg, 2)

        surface.blit(kills_surface, (kills_x, kills_y))