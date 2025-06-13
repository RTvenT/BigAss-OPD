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

class GameOverMenu:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)
        self.buttons = [
            Button(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 50, 200, 50, "заново"),
            Button(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 100, 200, 50, "в меню")
        ]

    def format_time(self, seconds):
        """Форматирует время в MM:SS"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def draw(self, surface, survival_time=0, kills=0):
        # Заголовок
        title_surf = self.title_font.render('GAME OVER', True, (255, 0, 0))
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 3))
        surface.blit(title_surf, title_rect)

        # Результаты
        time_text = f"Время выживания: {self.format_time(survival_time)}"
        kills_text = f"Убито врагов: {kills}"

        time_surf = self.font.render(time_text, True, (255, 255, 255))
        kills_surf = self.font.render(kills_text, True, (255, 255, 255))

        time_rect = time_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        kills_rect = kills_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))

        # Добавляем фон для текста
        padding = 10
        for text_rect in [time_rect, kills_rect]:
            bg_rect = text_rect.inflate(padding * 2, padding * 2)
            pygame.draw.rect(surface, (0, 0, 0), bg_rect)
            pygame.draw.rect(surface, (40, 40, 40), bg_rect, 2)

        surface.blit(time_surf, time_rect)
        surface.blit(kills_surf, kills_rect)

        # Кнопки
        for button in self.buttons:
            button.draw(surface)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                if button.rect.collidepoint(mouse_pos):
                    return button.text
        return None

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
