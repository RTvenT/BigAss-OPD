import pygame.mouse
import os
import sys

from settings import *
from player import Player
from hud import HUD
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites
from game_states import GameState
from menu import MainMenu, PauseMenu, GameOverMenu, SettingsMenu

from random import randint, choice

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Survivor')
        self.clock = pygame.time.Clock()
        self.running = True

        # Состояние игры
        self.state = GameState.MAIN_MENU
        pygame.mouse.set_visible(True)  # Показываем курсор в главном меню
        
        # Меню
        self.main_menu = MainMenu()
        self.pause_menu = PauseMenu()
        self.game_over_menu = GameOverMenu()
        self.settings_menu = SettingsMenu()

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
        self.spawn_positions = []

        # audio 
        self.music = pygame.mixer.Sound(join('..', 'audio', 'music.wav'))
        self.music.set_volume(0.5)
        self.music.play(loops = -1)
        self.impact_sound = pygame.mixer.Sound(join('..', 'audio', 'impact.ogg'))
        self.impact_sound.set_volume(0.3)

        # Изображения (загружаем один раз)
        self.load_images()

    def load_images(self):
        self.bullet_surf = pygame.image.load(join('..', 'images', 'gun', 'bullet.png')).convert_alpha()

        folders = list(walk(join('..', 'images', 'enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('..', 'images', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
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

        # setup
        self.setup()

    def setup(self):
        map = load_pygame(join('..', 'data', 'maps', 'world.tmx'))

        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, self.all_sprites)
        
        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
        
        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player(
                    (obj.x,obj.y), 
                    self.all_sprites, 
                    self.collision_sprites, 
                    self.enemy_sprites
                )

                # HUD
                self.hud = HUD(self.player)
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
                self.state = GameState.GAME_OVER
                pygame.mouse.set_visible(True)

    def bullet_collision(self):
        """Проверка коллизий пуль с врагами"""
        if self.player:  # Проверяем, что игрок существует
            for bullet in self.player.bullet_sprites.sprites():
                # Используем sprite.spritecollide вместо pygame.sprite.spritecollide
                collided_enemies = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                
                if collided_enemies:
                    self.impact_sound.play()
                    bullet.kill()
                    
                    for enemy in collided_enemies:
                        if enemy.death_time == 0:  # Если враг еще жив
                            enemy.destroy()
                            self.hud.add_kill()

    def enemy_attacks(self):
        for enemy in self.enemy_sprites:
            enemy.attack()

    def handle_menu_events(self, event):
        """Обработка событий в меню"""
        if self.state == GameState.MAIN_MENU:
            result = self.main_menu.handle_event(event)
            if result == "играть":
                self.state = GameState.PLAYING
                self.init_game()
                pygame.mouse.set_visible(False)
            elif result == "настройки":
                self.state = GameState.SETTINGS
            elif result == "выход":
                self.running = False
                
        elif self.state == GameState.PAUSED:
            result = self.pause_menu.handle_event(event)
            if result == "продолжить":
                self.state = GameState.PLAYING
                pygame.mouse.set_visible(False)
            elif result == "настройки":
                self.state = GameState.SETTINGS
            elif result == "в меню":
                self.state = GameState.MAIN_MENU
                pygame.mouse.set_visible(True)
                
        elif self.state == GameState.GAME_OVER:
            result = self.game_over_menu.handle_event(event)
            if result == "заново":
                self.state = GameState.PLAYING
                self.init_game()
                pygame.mouse.set_visible(False)
            elif result == "в меню":
                self.state = GameState.MAIN_MENU
                pygame.mouse.set_visible(True)
                
        elif self.state == GameState.SETTINGS:
            result = self.settings_menu.handle_event(event)
            if result == "назад":
                # Возвращаемся в предыдущее состояние
                if hasattr(self, '_prev_state'):
                    self.state = self._prev_state
                else:
                    self.state = GameState.MAIN_MENU
            # Применяем настройки громкости
            self.music.set_volume(self.settings_menu.music_volume)

    def run(self):
        while self.running:
            # dt 
            dt = self.clock.tick(60) / 1000

            # event loop 
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
                if self.state != GameState.PLAYING:
                    self.handle_menu_events(event)
                
                # Спавн врагов только во время игры
                if self.state == GameState.PLAYING and event.type == self.enemy_event:
                    if self.spawn_positions and self.enemy_frames:
                        Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), 
                              (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)

            # Обновление игры только в состоянии PLAYING
            if self.state == GameState.PLAYING:
                self.all_sprites.update(dt)
                self.bullet_collision()
                self.enemy_attacks()
                self.check_game_over()

            # Отрисовка
            if self.state == GameState.PLAYING:
                self.display_surface.fill('black')
                self.all_sprites.draw(self.player.rect.center)

                # crosshair
                crosshair_pos = pygame.mouse.get_pos()
                self.display_surface.blit(self.crosshair_image, crosshair_pos)

                # hud
                self.hud.draw(self.display_surface)

                # hitboxes (можно убрать в финальной версии)
                self.player.draw_hitbox(self.display_surface, self.all_sprites.offset)
                for enemy in self.enemy_sprites:
                    enemy.draw_hitbox(self.all_sprites.display_surface, self.all_sprites.offset)
                    
            elif self.state == GameState.MAIN_MENU:
                self.main_menu.draw(self.display_surface)
                
            elif self.state == GameState.PAUSED:
                # Рисуем игру на фоне
                if self.all_sprites and self.player:
                    self.display_surface.fill('black')
                    self.all_sprites.draw(self.player.rect.center)
                    self.hud.draw(self.display_surface)
                self.pause_menu.draw(self.display_surface)
                
            elif self.state == GameState.GAME_OVER:
                survival_time = self.hud.get_survival_time() if self.hud else 0
                kills = self.hud.kills if self.hud else 0
                self.game_over_menu.draw(self.display_surface, survival_time, kills)
                
            elif self.state == GameState.SETTINGS:
                self.settings_menu.draw(self.display_surface)

            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()