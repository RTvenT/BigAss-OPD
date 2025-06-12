from settings import *
import pygame
from os.path import join


class HUD:
    def __init__(self, player):
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

        self.font = pygame.font.Font(None, 24)
        self.timer_font = pygame.font.Font(None, 36)  # Больший шрифт для таймера

        # Время начала игры
        self.start_time = pygame.time.get_ticks()

        # Счетчик убийств
        self.kills = 0

        # Инвентарь оружия
        self.weapon_slot_size = 64
        self.weapon_slot_gap = 10
        self.weapon_slots_y = 60
        self.weapon_names = {
            'Pistol': 'Пистолет',
            'Shotgun': 'Дробовик',
            'Sword': 'Меч',
            'AutoRifle': 'Автомат'
        }
        # Загружаем изображение оружия (временно используем одно для всех)
        self.weapon_image = pygame.image.load(join('..', 'images', 'gun', 'bullet.png')).convert_alpha()
        self.weapon_image = pygame.transform.scale(self.weapon_image, (48, 48))

    def get_survival_time(self):
        """Возвращает время выживания в секундах"""
        if not self.player.alive:  # Если игрок мертв, возвращаем последнее время
            return (self.player.death_time - self.start_time) // 1000
        current_time = pygame.time.get_ticks()
        return (current_time - self.start_time) // 1000

    def add_kill(self):
        """Увеличивает счетчик убийств"""
        self.kills += 1

    def format_time(self, seconds):
        """Форматирует время в MM:SS"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def reset_timer(self):
        """Сбрасывает таймер и счетчик убийств"""
        self.start_time = pygame.time.get_ticks()
        self.kills = 0

    def draw_weapon_slots(self, surface):
        # Рисуем слоты для оружия
        center_x = surface.get_width() // 2
        start_x = center_x - (self.weapon_slot_size * 1.5 + self.weapon_slot_gap)

        for i in range(3):
            slot_x = start_x + i * (self.weapon_slot_size + self.weapon_slot_gap)
            slot_rect = pygame.Rect(slot_x, self.weapon_slots_y, self.weapon_slot_size, self.weapon_slot_size)
            
            # Рисуем фон слота
            pygame.draw.rect(surface, (30, 30, 30), slot_rect)
            pygame.draw.rect(surface, (60, 60, 60), slot_rect, 2)

            # Если есть оружие в этом слоте
            if i < len(self.player.weapons):
                # Рисуем иконку оружия
                weapon = self.player.weapons[i]
                image_rect = self.weapon_image.get_rect(center=slot_rect.center)
                surface.blit(self.weapon_image, image_rect)
                
                # Название оружия
                weapon_name = self.weapon_names.get(weapon.__class__.__name__, weapon.__class__.__name__)
                name_surf = self.font.render(weapon_name, True, (200, 200, 200))
                name_rect = name_surf.get_rect(centerx=slot_rect.centerx, top=slot_rect.bottom + 5)
                surface.blit(name_surf, name_rect)

            # Если это активное оружие
            if i == self.player.current_weapon_index:
                pygame.draw.rect(surface, (200, 200, 0), slot_rect, 3)

            # Номер слота (1,2,3)
            slot_num = self.font.render(str(i + 1), True, (200, 200, 200))
            num_rect = slot_num.get_rect(topleft=(slot_rect.left + 5, slot_rect.top + 5))
            surface.blit(slot_num, num_rect)

    def draw(self, surface):
        # Рисуем слоты оружия
        self.draw_weapon_slots(surface)

        # Считаем, сколько сегментов заполнено
        hp_per_segment = 100 / self.segments_total
        current_segments = max(0, int(self.player.health / hp_per_segment))

        # Рисуем полоски здоровья
        for i in range(self.segments_total):
            rect = pygame.Rect(
                self.x + i * (self.segment_width + self.gap),
                self.y,
                self.segment_width,
                self.segment_height
            )
            pygame.draw.rect(surface, self.bg_color, rect.inflate(2, 2))  # рамка
            color = self.filled_color if i < current_segments else self.empty_color
            pygame.draw.rect(surface, color, rect)

        # Текст здоровья
        health_text = self.font.render(f'{self.player.health}/100', True, (255, 255, 255))
        surface.blit(health_text, (self.x, self.y + self.segment_height + 5))

        # Секундомер по центру сверху
        survival_time = self.get_survival_time()
        time_text = self.format_time(survival_time)
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