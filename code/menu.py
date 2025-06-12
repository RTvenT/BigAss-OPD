import pygame
from settings import *

class Button:
    def __init__(self, x, y, width, height, text, font_size=36):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        # Новые цвета в стиле вампирской темы
        self.color = (80, 0, 0)  # Тёмно-красный
        self.hover_color = (150, 0, 0)  # Красный при наведении
        self.text_color = (200, 200, 200)  # Светло-серый текст
        self.border_color = (120, 0, 0)  # Цвет рамки
        self.is_hovered = False

    def draw(self, surface):
        # Рисуем тень
        shadow_rect = self.rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(surface, (20, 0, 0), shadow_rect)
        
        # Рисуем основную кнопку
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        
        # Рисуем рамку
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
        
        # Рисуем текст
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return True
        return False

class BaseMenu:
    def __init__(self):
        self.buttons = []
        self.font = pygame.font.Font(None, 64)  # Увеличенный размер шрифта для заголовка
        self.title = ""
        self.background_color = (30, 0, 0)  # Тёмно-бордовый фон
        
    def draw(self, surface):
        # Градиентный фон
        for i in range(WINDOW_HEIGHT):
            darkness = 1 - (i / WINDOW_HEIGHT * 0.5)  # Затемнение сверху вниз
            color = (int(30 * darkness), 0, 0)
            pygame.draw.line(surface, color, (0, i), (WINDOW_WIDTH, i))
            
        if self.title:
            # Тень для заголовка
            title_shadow = self.font.render(self.title, True, (20, 0, 0))
            shadow_rect = title_shadow.get_rect(centerx=WINDOW_WIDTH // 2 + 2, y=52)
            surface.blit(title_shadow, shadow_rect)
            
            # Заголовок
            title_surf = self.font.render(self.title, True, (200, 0, 0))
            title_rect = title_surf.get_rect(centerx=WINDOW_WIDTH // 2, y=50)
            surface.blit(title_surf, title_rect)
            
        for button in self.buttons:
            button.draw(surface)

    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                return button.text.lower()
        return None

class MainMenu(BaseMenu):
    def __init__(self):
        super().__init__()
        self.title = "Vampire Survivor"
        center_x = WINDOW_WIDTH // 2 - 100
        self.buttons = [
            Button(center_x, 200, 200, 50, "Играть"),
            Button(center_x, 300, 200, 50, "Настройки"),
            Button(center_x, 400, 200, 50, "Выход")
        ]

class PauseMenu(BaseMenu):
    def __init__(self):
        super().__init__()
        self.title = "Пауза"
        center_x = WINDOW_WIDTH // 2 - 100
        self.buttons = [
            Button(center_x, 200, 200, 50, "Продолжить"),
            Button(center_x, 300, 200, 50, "Настройки"),
            Button(center_x, 400, 200, 50, "В меню")
        ]

class GameOverMenu(BaseMenu):
    def __init__(self):
        super().__init__()
        self.title = "Игра Окончена"
        center_x = WINDOW_WIDTH // 2 - 100
        self.buttons = [
            Button(center_x, 300, 200, 50, "Заново"),
            Button(center_x, 400, 200, 50, "В меню")
        ]
        
    def draw(self, surface, survival_time=0, kills=0):
        super().draw(surface)
        # Отображаем статистику
        stats_font = pygame.font.Font(None, 36)
        time_text = f"Время выживания: {survival_time:.1f} сек"
        kills_text = f"Убито врагов: {kills}"
        
        # Тень для текста
        shadow_color = (20, 0, 0)
        time_shadow = stats_font.render(time_text, True, shadow_color)
        kills_shadow = stats_font.render(kills_text, True, shadow_color)
        
        # Основной текст
        time_surf = stats_font.render(time_text, True, (200, 0, 0))
        kills_surf = stats_font.render(kills_text, True, (200, 0, 0))
        
        # Отрисовка с тенью
        for text, shadow, y in [(time_surf, time_shadow, 150), (kills_surf, kills_shadow, 200)]:
            shadow_rect = text.get_rect(centerx=WINDOW_WIDTH // 2 + 1, y=y + 1)
            text_rect = text.get_rect(centerx=WINDOW_WIDTH // 2, y=y)
            surface.blit(shadow, shadow_rect)
            surface.blit(text, text_rect)

class SettingsMenu(BaseMenu):
    def __init__(self):
        super().__init__()
        self.title = "Настройки"
        center_x = WINDOW_WIDTH // 2 - 100
        self.buttons = [
            Button(center_x, 400, 200, 50, "Назад")
        ]
        # Настройки звука
        self.music_volume = 0.5
        self.sound_volume = 0.2
