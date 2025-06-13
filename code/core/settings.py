"""
Game settings and configuration.
"""
import pygame
from os.path import join
from os import walk

# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TILE_SIZE = 64

# Game settings
FPS = 60
GAME_TITLE = "Vampire Survivor"

# Asset paths
ASSET_DIR = "assets"
IMAGE_DIR = join(ASSET_DIR, "images")
AUDIO_DIR = join(ASSET_DIR, "audio")

# Player settings
PLAYER_SPEED = 5
PLAYER_HEALTH = 100

# Enemy settings
ENEMY_SPAWN_RATE = 1.0  # enemies per second
ENEMY_SPEED = 3

# Weapon settings
WEAPON_COOLDOWN = 0.5  # seconds 
 