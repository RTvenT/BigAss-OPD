import pygame
import math
import os
from os.path import join
from core import WINDOW_WIDTH, WINDOW_HEIGHT, load_settings, save_settings


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
        
        # Загружаем фоновое изображение для меню
        try:
            self.background_image = pygame.image.load(join('..', 'images', 'ui', 'menu_bg.jpg')).convert()
            # Масштабируем изображение под размер окна
            self.background_image = pygame.transform.scale(self.background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except:
            self.background_image = None
        
    def draw(self, surface):
        # Отрисовка фона
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            # Градиентный фон как запасной вариант
            for i in range(WINDOW_HEIGHT):
                darkness = 1 - (i / WINDOW_HEIGHT * 0.5)
                color = (int(30 * darkness), 0, 0)
                pygame.draw.line(surface, color, (0, i), (WINDOW_WIDTH, i))
            
        if self.title:
            # Тень для заголовка (белая)
            title_shadow = self.font.render(self.title, True, (255, 255, 255))
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
        self.title = "Большие S"
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

class GameParamsMenu(BaseMenu):
    def __init__(self):
        super().__init__()
        self.title = "Параметры игры"
        
        # Позиции и размеры элементов
        center_x = WINDOW_WIDTH // 2
        button_width = 200
        button_height = 50
        map_preview_size = 200
        map_gap = 50
        
        # Кнопки выбора сложности (увеличиваем расстояние между ними)
        self.difficulty_buttons = [
            Button(center_x - button_width//2 - 220, 200, button_width, button_height, "Легко"),
            Button(center_x - button_width//2, 200, button_width, button_height, "Средне"),
            Button(center_x + button_width//2 + 20, 200, button_width, button_height, "Сложно")
        ]
        self.selected_difficulty = 1  # Индекс выбранной сложности (0-Легко, 1-Средне, 2-Сложно)
        
        # Превью карт
        self.map_previews = [
            pygame.Rect(center_x - map_preview_size - map_gap//2, 300, map_preview_size, map_preview_size),
            pygame.Rect(center_x + map_gap//2, 300, map_preview_size, map_preview_size)
        ]
        self.selected_map = 0  # Индекс выбранной карты
        
        # Кнопка "Играть"
        self.play_button = Button(center_x - button_width//2, 550, button_width, button_height, "Играть")
        
        # Загрузка превью карт
        self.map_images = []
        try:
            # Используем правильные пути к файлам
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            map2_path = os.path.join(base_path, 'images', 'maps', 'map1_preview.png')
            map1_path = os.path.join(base_path, 'images', 'maps', 'map2_preview.png')
            
            if os.path.exists(map1_path) and os.path.exists(map2_path):
                # Загружаем и масштабируем изображения
                map1 = pygame.image.load(map1_path).convert_alpha()
                map2 = pygame.image.load(map2_path).convert_alpha()
                
                # Масштабируем изображения до размера превью
                self.map_images = [
                    pygame.transform.scale(map1, (map_preview_size, map_preview_size)),
                    pygame.transform.scale(map2, (map_preview_size, map_preview_size))
                ]
            else:
                raise FileNotFoundError("Файлы превью не найдены")
        except Exception as e:
            print(f"Ошибка загрузки превью карт: {e}")
            # Если изображения не найдены, создаем заглушки
            self.map_images = [
                pygame.Surface((map_preview_size, map_preview_size)),
                pygame.Surface((map_preview_size, map_preview_size))
            ]
            self.map_images[0].fill((100, 100, 100))
            self.map_images[1].fill((150, 150, 150))
        
        # Инициализация завершена
        
    def draw(self, surface):
        super().draw(surface)
        
        # Отрисовка кнопок сложности
        for i, button in enumerate(self.difficulty_buttons):
            if i == self.selected_difficulty:
                button.color = (150, 0, 0)  # Выделяем выбранную сложность
            else:
                button.color = (80, 0, 0)
            button.draw(surface)
            
        # Отрисовка превью карт
        for i, rect in enumerate(self.map_previews):
            # Рисуем превью
            surface.blit(self.map_images[i], rect)
            
            # Рамка для карт
            if i == self.selected_map:
                # Белая рамка для выбранной карты
                pygame.draw.rect(surface, (255, 255, 255), rect, 4)
            else:
                # Серая рамка для невыбранной карты
                pygame.draw.rect(surface, (80, 80, 80), rect, 2)
        
        # Отрисовка кнопки "Играть"
        self.play_button.draw(surface)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Проверка нажатия на кнопки сложности
            for i, button in enumerate(self.difficulty_buttons):
                if button.rect.collidepoint(mouse_pos):
                    self.selected_difficulty = i
                    return None
                
            # Проверка нажатия на превью карт
            for i, rect in enumerate(self.map_previews):
                if rect.collidepoint(mouse_pos):
                    self.selected_map = i
                    return None
            
            # Проверка нажатия на кнопку "Играть"
            if self.play_button.rect.collidepoint(mouse_pos):
                return "play"
                
        # Обработка наведения мыши для кнопок
        for button in self.difficulty_buttons:
            button.handle_event(event)
        self.play_button.handle_event(event)
        
        return None
