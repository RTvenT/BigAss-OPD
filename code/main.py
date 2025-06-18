import pygame
import os
import sys
from os.path import join
from os import walk

# Добавляем корневую директорию проекта в Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from random import randint, choice

from core import (
    WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE,
    load_settings, save_settings, GameState
)
from sprites import Sprite, CollisionSprite, AllSprites
from weapons import Sword, WeaponItem
from pytmx.util_pygame import load_pygame
from entities import Player, Boss, Bat, Slime, Skeleton
from ui import HUD, MainMenu, PauseMenu, GameOverMenu, SettingsMenu, GameParamsMenu


os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Survivor')
        self.clock = pygame.time.Clock()
        self.running = True

        # Загружаем настройки звука
        self.music_volume, self.sound_volume = load_settings()

        # Состояние игры
        self.state = GameState.MAIN_MENU
        pygame.mouse.set_visible(True)  # Показываем курсор в главном меню
        
        # Меню
        self.main_menu = MainMenu()
        self.pause_menu = PauseMenu()
        self.game_over_menu = GameOverMenu()
        self.settings_menu = SettingsMenu()
        self.game_params_menu = GameParamsMenu()

        # Параметры игры
        self.difficulty = 1  # 0-Легко, 1-Средне, 2-Сложно
        self.selected_map = 0  # 0-Первая карта, 1-Вторая карта
        
        # Коэффициенты сложности
        self.difficulty_multipliers = {
            0: {  # Легко
                'health': 0.5,  # 50% от средней
                'damage': 0.5,  # 50% от средней
                'spawn_rate': 0.33  # В 3 раза реже
            },
            1: {  # Средне (базовые значения)
                'health': 1.0,
                'damage': 1.0,
                'spawn_rate': 1.0
            },
            2: {  # Сложно
                'health': 1.5,  # 150% от средней
                'damage': 2.0,  # 200% от средней
                'spawn_rate': 2.0  # В 2 раза чаще
            }
        }

        # crosshair
        self.crosshair_image = pygame.image.load(join('..', 'images', 'ui', 'crosshair.png')).convert_alpha()

        # Игровые объекты (создаются только при старте игры)
        self.all_sprites = None
        self.collision_sprites = None
        self.bullet_sprites = None
        self.enemy_sprites = None
        self.player = None
        self.hud = None

        # Спавн врагов
        self.enemy_event = pygame.event.custom_type()
        self.boss_event = pygame.event.custom_type()  # Новый тип события для босса
        self.spawn_positions = []
        self.last_boss_spawn = 0  # Время последнего спавна босса
        self.boss_spawn_interval = 30000  # 30 секунд в миллисекундах
        self.boss_spawn_timer = 0  # Таймер для спавна босса
        self.initial_boss_delay = True  # Флаг для первого спавна

        # audio 
        self.music = pygame.mixer.Sound(join('..', 'audio', 'music1.wav'))
        self.music.set_volume(self.music_volume)
        self.music.play(loops = -1)
        self.impact_sound = pygame.mixer.Sound(join('..', 'audio', 'impact.ogg'))
        self.impact_sound.set_volume(self.sound_volume)

        # Изображения (загружаем один раз)
        self.load_images()

    def load_images(self):
        self.bullet_surf = pygame.image.load(join('..', 'images', 'gun', 'bullet.png')).convert_alpha()

        folders = list(walk(join('..', 'images', 'enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('..', 'images', 'enemies', folder)):
                self.enemy_frames[folder] = []
                if folder == 'Boss':
                    # Для папки Boss просто загружаем изображения без сортировки по номерам
                    for file_name in file_names:
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.enemy_frames[folder].append(surf)
                else:
                    # Для остальных папок используем числовую сортировку
                    for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.enemy_frames[folder].append(surf)

    def init_game(self):
        """Инициализация игровых объектов"""
        # groups 
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # Сброс позиций спавна
        self.spawn_positions = []
        
        # Таймер спавна врагов
        pygame.time.set_timer(self.enemy_event, 300)
        
        # Сброс времени спавна босса
        self.last_boss_spawn = pygame.time.get_ticks()
        self.boss_spawn_timer = 0
        self.initial_boss_delay = True  # Флаг для первого спавна

        # Создаем новый HUD
        self.hud = HUD()

        # Сброс финальных результатов
        self.final_kills = 0
        self.final_time = 0

        # setup
        self.setup()

        # После создания игрока присваиваем его HUD'у
        if self.player:
            self.hud.player = self.player
            self.hud.reset()  # Сбрасываем таймеры

    def setup(self):
        """Настройка игровых объектов"""
        # Создаем HUD до создания игрока
        self.hud = HUD()
        
        # Загружаем карту в зависимости от выбора
        map_file = 'world1.tmx' if self.selected_map == 0 else 'world2.tmx'
        tmx_data = load_pygame(join('..', 'data', 'maps', map_file))
        
        # Создаем тайлы
        for x, y, surf in tmx_data.get_layer_by_name('Ground').tiles():
            pos = (x * TILE_SIZE, y * TILE_SIZE)
            Sprite(pos, surf, [self.all_sprites])
            
        for obj in tmx_data.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
        
        for obj in tmx_data.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)
            
        # Создаем игрока
        for obj in tmx_data.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player(
                    (obj.x, obj.y),
                    [self.all_sprites],
                    self.collision_sprites,
                    self.enemy_sprites,
                    self  # Передаем ссылку на игру
                )
                # Присваиваем HUD игроку
                self.player.hud = self.hud
            else:
                pos = (obj.x, obj.y)
                # Проверка расстояния
                if self.player:
                    player_pos = pygame.math.Vector2(self.player.rect.center)
                    spawn_pos = pygame.math.Vector2(pos)
                    if player_pos.distance_to(spawn_pos) > 100:
                        self.spawn_positions.append(pos)
                else:
                    self.spawn_positions.append(pos)

    def check_game_over(self):
        if self.player and not self.player.alive:
            if self.state != GameState.GAME_OVER:
                # Сохраняем финальные результаты перед переходом в game over
                if self.hud:
                    self.final_kills = self.hud.kills
                    self.final_time = self.hud.game_time
                else:
                    self.final_kills = 0
                    self.final_time = 0
                
                self.state = GameState.GAME_OVER
                pygame.mouse.set_visible(True)

    def bullet_collision(self):
        # Проверяем столкновения пуль с врагами
        for enemy in self.enemy_sprites:
            if enemy.death_time == 0:  # Проверяем, что враг жив
                for bullet in self.player.bullet_sprites:
                    if pygame.sprite.collide_mask(bullet, enemy):
                        bullet.kill()
                        enemy.take_damage(self.player.current_weapon.damage)
                        self.impact_sound.play()

    def enemy_attacks(self):
        for enemy in self.enemy_sprites:
            enemy.attack()

    def handle_menu_events(self, event):
        """Обработка событий в меню"""
        if self.state == GameState.MAIN_MENU:
            result = self.main_menu.handle_event(event)
            if result == "играть":
                self.state = GameState.GAME_PARAMS
            elif result == "настройки":
                self._prev_state = self.state
                self.state = GameState.SETTINGS
            elif result == "выход":
                self.running = False
                
        elif self.state == GameState.GAME_PARAMS:
            result = self.game_params_menu.handle_event(event)
            if result == "play":
                self.difficulty = self.game_params_menu.selected_difficulty
                self.selected_map = self.game_params_menu.selected_map
                self.state = GameState.PLAYING
                self.init_game()
                pygame.mouse.set_visible(False)
                
        elif self.state == GameState.PAUSED:
            result = self.pause_menu.handle_event(event)
            if result == "продолжить":
                self.state = GameState.PLAYING
                pygame.mouse.set_visible(False)
            elif result == "настройки":
                self._prev_state = self.state
                self.state = GameState.SETTINGS
            elif result == "в меню":
                self.state = GameState.MAIN_MENU
                pygame.mouse.set_visible(True)
                
        elif self.state == GameState.GAME_OVER:
            result = self.game_over_menu.handle_event(event)
            if result == "заново":
                self.state = GameState.GAME_PARAMS
            elif result == "в меню":
                self.state = GameState.MAIN_MENU
                pygame.mouse.set_visible(True)
                
        elif self.state == GameState.SETTINGS:
            result = self.settings_menu.handle_event(event)
            if result == "назад":
                if hasattr(self, '_prev_state'):
                    self.state = self._prev_state
                else:
                    self.state = GameState.MAIN_MENU
            self.music.set_volume(self.settings_menu.music_slider.value)
            self.impact_sound.set_volume(self.settings_menu.sound_slider.value)
            save_settings(self.settings_menu.music_slider.value, 
                         self.settings_menu.sound_slider.value)

    def spawn_boss(self):
        """Спавн босса недалеко от игрока"""
        if not self.player:
            return

        self.boss_spawn_timer += self.clock.get_time()  # Добавляем прошедшее время
        time_until_boss = (self.boss_spawn_interval - self.boss_spawn_timer) // 1000  # Время до босса в секундах
        
        # Обновляем информацию о времени до босса в HUD
        if self.hud:
            self.hud.time_until_boss = time_until_boss

        # Проверяем, прошло ли достаточно времени для первого спавна
        if self.initial_boss_delay and self.boss_spawn_timer < 10000:  # 10 секунд задержки
            return

        self.initial_boss_delay = False  # Сбрасываем флаг после первой задержки

        if self.boss_spawn_timer >= self.boss_spawn_interval:
            # print("Спавним босса!")  # Отладочное сообщение
            
            # Спавним босса на расстоянии 200 пикселей от игрока в случайном направлении
            angle = random.randint(0, 360)  # Случайный угол
            spawn_distance = 200  # Расстояние от игрока
            
            # Вычисляем позицию спавна
            spawn_offset = pygame.Vector2(spawn_distance, 0).rotate(angle)
            spawn_pos = pygame.Vector2(self.player.rect.center) + spawn_offset
            
            Boss(spawn_pos, [self.all_sprites, self.enemy_sprites], self.player, self.collision_sprites)
            self.boss_spawn_timer = 0  # Сбрасываем таймер

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # Пауза по ESC во время игры
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == GameState.PLAYING:
                            self.state = GameState.PAUSED
                            pygame.mouse.set_visible(True)
                        elif self.state == GameState.PAUSED:
                            self.state = GameState.PLAYING
                            pygame.mouse.set_visible(False)

                # Обработка событий меню
                if self.state in [GameState.MAIN_MENU, GameState.PAUSED, 
                                GameState.GAME_OVER, GameState.SETTINGS,
                                GameState.GAME_PARAMS]:
                    self.handle_menu_events(event)
                elif self.state == GameState.PLAYING:
                    if event.type == self.enemy_event:
                        self.spawn_enemies()

            # Обновление и отрисовка в зависимости от состояния игры
            if self.state == GameState.MAIN_MENU:
                self.display_surface.fill('black')
                self.main_menu.draw(self.display_surface)
            elif self.state == GameState.GAME_PARAMS:
                self.display_surface.fill('black')
                self.game_params_menu.draw(self.display_surface)
            elif self.state == GameState.PAUSED:
                # Сначала рисуем игру
                if self.player and self.all_sprites:
                    self.display_surface.fill('black')
                    self.all_sprites.draw(self.player.rect.center)
                # Затем меню паузы поверх
                self.pause_menu.draw(self.display_surface)
            elif self.state == GameState.GAME_OVER:
                self.display_surface.fill('black')
                self.game_over_menu.draw(self.display_surface, self.final_time, self.final_kills)
            elif self.state == GameState.SETTINGS:
                self.display_surface.fill('black')
                self.settings_menu.draw(self.display_surface)
            elif self.state == GameState.PLAYING:
                # Обновление
                self.all_sprites.update(dt)
                self.bullet_collision()
                self.enemy_attacks()
                self.check_game_over()
                self.spawn_boss()

                # Отрисовка
                self.display_surface.fill('black')
                if self.player:
                    self.all_sprites.draw(self.player.rect.center)
                    
                    # Отрисовка хитбоксов
                    # self.player.draw_hitbox(self.display_surface, self.all_sprites.offset)
                    for enemy in self.enemy_sprites:
                    #     enemy.draw_hitbox(self.display_surface, self.all_sprites.offset)
                        enemy.draw_hp_bar(self.display_surface, self.all_sprites.offset)
                    
                    # Отрисовка эффектов оружия
                    for sprite in self.all_sprites:
                        if isinstance(sprite, WeaponItem):
                            sprite.draw_effects(self.display_surface, self.all_sprites.offset)
                    
                    # Отрисовка области атаки меча (после всего остального)
                    if self.player and isinstance(self.player.current_weapon, Sword):
                        self.player.current_weapon.draw_attack_area(self.display_surface)
                
                # Отрисовка HUD только во время игры
                if self.player and self.hud:
                    self.hud.draw(self.display_surface)

                # crosshair
                if not pygame.mouse.get_visible():
                    crosshair_rect = self.crosshair_image.get_rect(center = pygame.mouse.get_pos())
                    self.display_surface.blit(self.crosshair_image, crosshair_rect)

            pygame.display.update()
        
        pygame.quit()

    def spawn_enemies(self):
        """Спавн обычных врагов"""
        if self.spawn_positions and self.enemy_frames:
            # Проверяем шанс спавна в зависимости от сложности
            if random.random() > self.difficulty_multipliers[self.difficulty]['spawn_rate']:
                return
                
            pos = choice(self.spawn_positions)
            # Выбираем случайный тип врага, кроме босса
            available_frames = {k: v for k, v in self.enemy_frames.items() if k != 'Boss'}
            if available_frames:
                # print(f"Доступные типы врагов: {list(available_frames.keys())}")  # Отладочная информация
                enemy_type = choice(list(available_frames.keys()))
                frames = available_frames[enemy_type]
                # print(f"Создаем врага типа: {enemy_type}")  # Отладочная информация
                
                # Создаем врага соответствующего типа
                if enemy_type == 'bat':
                    enemy = Bat(pos, frames, [self.all_sprites, self.enemy_sprites], self.player, self.collision_sprites)
                    # print(f"Создана летучая мышь: скорость={enemy.speed}, здоровье={enemy.health}, урон={enemy.damage}")
                elif enemy_type == 'blob':
                    enemy = Slime(pos, frames, [self.all_sprites, self.enemy_sprites], self.player, self.collision_sprites)
                    # print(f"Создан слизень: скорость={enemy.speed}, здоровье={enemy.health}, урон={enemy.damage}")
                else:  # skeleton или любой другой тип
                    enemy = Skeleton(pos, frames, [self.all_sprites, self.enemy_sprites], self.player, self.collision_sprites)
                    # print(f"Создан скелет: скорость={enemy.speed}, здоровье={enemy.health}, урон={enemy.damage}")
                
                # Применяем множители сложности
                enemy.health = int(enemy.health * self.difficulty_multipliers[self.difficulty]['health'])
                enemy.max_health = enemy.health
                enemy.damage = int(enemy.damage * self.difficulty_multipliers[self.difficulty]['damage'])

if __name__ == '__main__':
    game = Game()
    game.run()