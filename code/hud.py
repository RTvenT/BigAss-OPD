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

    def draw(self, surface):
        # Считаем, сколько сегментов заполнено
        hp_per_segment = 100 / self.segments_total
        current_segments = max(0, int(self.player.health / hp_per_segment))

        # Рисуем полоски
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

        # Текст поверх (если хочешь)
        health_text = self.font.render(f'{self.player.health}/100', True, (255, 255, 255))
        surface.blit(health_text, (self.x, self.y + self.segment_height + 5))
