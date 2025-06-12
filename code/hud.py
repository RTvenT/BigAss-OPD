from settings import *
import pygame


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

    def get_survival_time(self):
        """Возвращает время выживания в секундах"""
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

    def add_kill(self):
        """Увеличивает счетчик убийств"""
        self.kills += 1

    def reset_timer(self):
        """Сбрасывает таймер и счетчик убийств"""
        self.start_time = pygame.time.get_ticks()
        self.kills = 0

    def draw(self, surface):
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