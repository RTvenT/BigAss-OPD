from enum import Enum

class GameState(Enum):
    MAIN_MENU = 'main_menu'    # Главное меню
    PLAYING = 'playing'        # Игровой процесс
    PAUSED = 'paused'         # Пауза
    GAME_OVER = 'game_over'   # Конец игры
    SETTINGS = 'settings'     # Настройки
