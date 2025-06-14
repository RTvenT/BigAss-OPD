import pygame 
from os.path import join 
from os import walk
import json
import os

WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720 
TILE_SIZE = 64

# Настройки звука по умолчанию
DEFAULT_MUSIC_VOLUME = 0.5
DEFAULT_SOUND_VOLUME = 0.5

def load_settings():
    try:
        settings_path = join(os.path.dirname(os.path.dirname(__file__)), 'data', 'settings.json')
        with open(settings_path, 'r') as f:
            settings = json.load(f)
            return settings.get('music_volume', DEFAULT_MUSIC_VOLUME), \
                   settings.get('sound_volume', DEFAULT_SOUND_VOLUME)
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_MUSIC_VOLUME, DEFAULT_SOUND_VOLUME

def save_settings(music_volume, sound_volume):
    settings = {
        'music_volume': music_volume,
        'sound_volume': sound_volume
    }
    settings_path = join(os.path.dirname(os.path.dirname(__file__)), 'data', 'settings.json')
    # Создаем директорию, если она не существует
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    with open(settings_path, 'w') as f:
        json.dump(settings, f)