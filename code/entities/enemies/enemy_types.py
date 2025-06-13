import os
import sys

# Добавляем корневую директорию проекта в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sprites import Enemy

class Bat(Enemy):
    def __init__(self, pos, frames, groups, player, collision_sprites):
        # Сначала устанавливаем базовые характеристики
        self.speed = 200  # Быстрее обычного врага
        self.max_health = 30  # Возвращаем прежнее значение
        self.damage = 5  # Меньше урона
        self.attack_cooldown = 800  # Быстрее атакует
        
        # Затем вызываем конструктор родительского класса
        super().__init__(pos, frames, groups, player, collision_sprites)
        
        # Переопределяем значения после инициализации родителя
        self.health = self.max_health

class Slime(Enemy):
    def __init__(self, pos, frames, groups, player, collision_sprites):
        # Сначала устанавливаем базовые характеристики
        self.speed = 125  # Медленнее обычного врага
        self.max_health = 120  # Возвращаем прежнее значение
        self.damage = 15  # Больше урона
        self.attack_cooldown = 1200  # Медленнее атакует
        
        # Затем вызываем конструктор родительского класса
        super().__init__(pos, frames, groups, player, collision_sprites)
        
        # Переопределяем значения после инициализации родителя
        self.health = self.max_health

class Skeleton(Enemy):
    def __init__(self, pos, frames, groups, player, collision_sprites):
        # Сначала устанавливаем базовые характеристики
        self.speed = 175
        self.max_health = 90  # Возвращаем прежнее значение
        self.damage = 10
        self.attack_cooldown = 1000
        
        # Затем вызываем конструктор родительского класса
        super().__init__(pos, frames, groups, player, collision_sprites)
        
        # Переопределяем значения после инициализации родителя
        self.health = self.max_health 