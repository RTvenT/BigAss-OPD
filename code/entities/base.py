"""
Base class for all game entities.
"""
import pygame
from abc import ABC, abstractmethod

class Entity(ABC):
    def __init__(self, x: float, y: float, image: pygame.Surface):
        self.x = x
        self.y = y
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 0
        self.health = 100
        self.is_alive = True

    @abstractmethod
    def update(self, dt: float):
        """Update entity state."""
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        """Draw entity on the surface."""
        pass

    def move(self, dx: float, dy: float):
        """Move entity by given delta."""
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.rect.x = self.x
        self.rect.y = self.y

    def take_damage(self, amount: float):
        """Take damage and handle death."""
        self.health -= amount
        if self.health <= 0:
            self.is_alive = False 