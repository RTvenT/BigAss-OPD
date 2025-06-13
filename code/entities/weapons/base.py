"""
Base class for all weapons.
"""
import pygame
from abc import ABC, abstractmethod
from ...core.settings import WEAPON_COOLDOWN

class Weapon(ABC):
    def __init__(self, owner, damage: float, cooldown: float = WEAPON_COOLDOWN):
        self.owner = owner
        self.damage = damage
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.is_active = False

    @abstractmethod
    def attack(self):
        """Perform attack."""
        pass

    def update(self, dt: float):
        """Update weapon state."""
        if self.current_cooldown > 0:
            self.current_cooldown -= dt

    def can_attack(self) -> bool:
        """Check if weapon can attack."""
        return self.current_cooldown <= 0

    def start_cooldown(self):
        """Start weapon cooldown."""
        self.current_cooldown = self.cooldown 