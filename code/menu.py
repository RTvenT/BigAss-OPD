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

class Slider:
    def __init__(self, x, y, width, height, min_val=0, max_val=1, initial_val=0.5):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False
        self.handle_radius = height // 2
        self.handle_pos = self._value_to_pos(initial_val)
        
    def _value_to_pos(self, value):
        return self.rect.x + (value - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        
    def _pos_to_value(self, pos):
        value = (pos - self.rect.x) / self.rect.width * (self.max_val - self.min_val) + self.min_val
        return max(self.min_val, min(self.max_val, value))
        
    def draw(self, surface):
        # Рисуем линию слайдера
        pygame.draw.line(surface, (100, 100, 100), 
                        (self.rect.x, self.rect.centery),
                        (self.rect.right, self.rect.centery), 2)
        
        # Рисуем ползунок
        pygame.draw.circle(surface, (150, 0, 0), 
                         (int(self.handle_pos), self.rect.centery), 
                         self.handle_radius)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                handle_rect = pygame.Rect(
                    self.handle_pos - self.handle_radius,
                    self.rect.centery - self.handle_radius,
                    self.handle_radius * 2,
                    self.handle_radius * 2
                )
                if handle_rect.collidepoint(event.pos):
                    self.dragging = True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
                
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.handle_pos = max(self.rect.x, min(self.rect.right, event.pos[0]))
            self.value = self._pos_to_value(self.handle_pos)
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
        center_x = WINDOW_WIDTH // 2 - 150
        
        # Загружаем сохраненные настройки
        music_volume, sound_volume = load_settings()
        
        # Создаем слайдеры с сохраненными значениями
        self.music_slider = Slider(center_x, 200, 300, 20, initial_val=music_volume)
        self.sound_slider = Slider(center_x, 300, 300, 20, initial_val=sound_volume)
        
        # Создаем текст для слайдеров
        self.font = pygame.font.Font(None, 36)
        
        self.buttons = [
            Button(center_x, 400, 200, 50, "Назад")
        ]
        
    def draw(self, surface):
        super().draw(surface)
        
        # Рисуем текст для слайдеров
        music_text = self.font.render("Громкость музыки", True, (200, 200, 200))
        sound_text = self.font.render("Громкость эффектов", True, (200, 200, 200))
        
        surface.blit(music_text, (self.music_slider.rect.x, self.music_slider.rect.y - 30))
        surface.blit(sound_text, (self.sound_slider.rect.x, self.sound_slider.rect.y - 30))
        
        # Рисуем слайдеры
        self.music_slider.draw(surface)
        self.sound_slider.draw(surface)
        
    def handle_event(self, event):
        # Обрабатываем события слайдеров
        if self.music_slider.handle_event(event):
            pygame.mixer.music.set_volume(self.music_slider.value)
            # Сохраняем настройки при изменении
            save_settings(self.music_slider.value, self.sound_slider.value)
            
        if self.sound_slider.handle_event(event):
            # Здесь нужно будет обновить громкость звуковых эффектов
            # Сохраняем настройки при изменении
            save_settings(self.music_slider.value, self.sound_slider.value)
            
        # Обрабатываем события кнопок
        for button in self.buttons:
            if button.handle_event(event):
                return button.text.lower()
        return None
