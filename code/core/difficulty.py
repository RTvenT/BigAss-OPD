class DifficultyParams:
    def __init__(self, difficulty_level):
        # Базовые параметры для средней сложности
        self.health_multiplier = 1.0
        self.damage_multiplier = 1.0
        self.spawn_rate_multiplier = 1.0
        
        # Применяем модификаторы в зависимости от уровня сложности
        if difficulty_level == 0:  # Легко
            self.health_multiplier = 0.5
            self.damage_multiplier = 0.5
            self.spawn_rate_multiplier = 0.33
        elif difficulty_level == 2:  # Сложно
            self.health_multiplier = 1.5
            self.damage_multiplier = 2.0
            self.spawn_rate_multiplier = 2.0 