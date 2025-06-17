class GameParamsMenu(BaseMenu):
    def __init__(self, screen, game_state_manager):
        super().__init__(screen, game_state_manager)
        self.difficulty_level = 1  # По умолчанию средняя сложность
        
        # ... existing code ...
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # ... existing code ...
            
            # Обработка нажатия на кнопки сложности
            for i, button in enumerate(self.difficulty_buttons):
                if button.is_clicked(mouse_pos):
                    self.difficulty_level = i
                    # Обновляем внешний вид кнопок
                    for j, btn in enumerate(self.difficulty_buttons):
                        btn.active = (j == i)
                    return
                    
            # При нажатии на кнопку Play передаем уровень сложности
            if self.play_button.is_clicked(mouse_pos):
                self.game_state_manager.set_state('game', difficulty_level=self.difficulty_level)
                return
                
        # ... existing code ... 