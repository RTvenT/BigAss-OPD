from enum import Enum

class GameState(Enum):
    MAIN_MENU = 'main_menu'    # Главное меню
    GAME_PARAMS = 'game_params'  # Меню выбора параметров игры
    PLAYING = 'playing'        # Игровой процесс
    PAUSED = 'paused'         # Пауза
    GAME_OVER = 'game_over'   # Конец игры
    SETTINGS = 'settings'     # Настройки
