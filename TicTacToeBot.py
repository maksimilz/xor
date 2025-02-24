from random import choice

class TicTacToeBot:
    def __init__(self, difficulty='легко'):
        self.difficulty = difficulty.lower()  # приводим к нижнему регистру
        
    def make_move(self, game_logic):
        """Выбирает ход в зависимости от сложности"""
        # Проверяем, есть ли доступные ходы
        empty_cells = game_logic.get_empty_cells()
        if not empty_cells:
            return None
            
        # Добавим отладочную информацию
        print(f"Bot making move with difficulty: {self.difficulty}")
        print(f"Available cells: {empty_cells}")
        
        if self.difficulty == 'легко':
            move = self.make_random_move(game_logic)
        elif self.difficulty == 'средне':
            move = self.make_smart_move(game_logic)
        else:  # сложно
            move = self.make_best_move(game_logic)
            
        print(f"Bot chose move: {move}")
        return move
    
    def make_random_move(self, game_logic):
        """Случайный ход"""
        empty_cells = game_logic.get_empty_cells()
        if empty_cells:
            move = choice(empty_cells)
            # Проверяем, что клетка действительно пуста
            if game_logic.is_valid_move(move[0], move[1]):
                return move
        return None
    
    def find_winning_move(self, game_logic):
        """Ищет выигрышный ход"""
        for i, j in game_logic.get_empty_cells():
            # Пробуем сделать ход
            game_logic.grid[i][j] = game_logic.current_player
            # Проверяем победу
            if game_logic.check_win(i, j):
                # Отменяем пробный ход
                game_logic.grid[i][j] = ''
                return (i, j)
            # Отменяем пробный ход
            game_logic.grid[i][j] = ''
        return None

    def find_blocking_move(self, game_logic):
        """Ищет ход для блокировки победы противника"""
        # Сохраняем текущего игрока
        current = game_logic.current_player
        # Меняем на противника
        opponent = 'O' if current == 'X' else 'X'
        game_logic.current_player = opponent
        
        # Ищем выигрышный ход противника
        blocking_move = self.find_winning_move(game_logic)
        
        # Возвращаем исходного игрока
        game_logic.current_player = current
        return blocking_move
    
    def make_smart_move(self, game_logic):
        """Простая стратегия: блокировать победу противника или выиграть"""
        size = game_logic.grid_size
        center = size // 2

        # Проверяем возможность победы
        winning_move = self.find_winning_move(game_logic)
        if winning_move:
            return winning_move
            
        # Блокируем победу противника
        blocking_move = self.find_blocking_move(game_logic)
        if blocking_move:
            return blocking_move
            
        # Пытаемся занять центр
        if game_logic.grid[center][center] == '':
            return (center, center)
        
        # Пытаемся занять углы
        corners = [(0, 0), (0, size-1), (size-1, 0), (size-1, size-1)]
        empty_corners = [corner for corner in corners if game_logic.grid[corner[0]][corner[1]] == '']
        if empty_corners:
            return choice(empty_corners)
        
        # Иначе случайный ход
        return self.make_random_move(game_logic)
    
    def make_best_move(self, game_logic):
        """Использует улучшенную стратегию для поиска лучшего хода"""
        size = game_logic.grid_size
        center = size // 2

        # Сначала проверяем выигрышный ход
        winning_move = self.find_winning_move(game_logic)
        if winning_move:
            return winning_move
        
        # Затем проверяем блокирующий ход
        blocking_move = self.find_blocking_move(game_logic)
        if blocking_move:
            return blocking_move
        
        # Пытаемся занять центр
        if game_logic.grid[center][center] == '':
            return (center, center)
        
        # Пытаемся занять углы рядом с занятыми противником
        corners = [(0, 0), (0, size-1), (size-1, 0), (size-1, size-1)]
        for i, j in corners:
            if game_logic.grid[i][j] == '':
                # Проверяем соседние углы
                for ni, nj in corners:
                    if (ni != i or nj != j) and game_logic.grid[ni][nj] != '':
                        return (i, j)
        
        # Пытаемся занять любой свободный угол
        empty_corners = [corner for corner in corners if game_logic.grid[corner[0]][corner[1]] == '']
        if empty_corners:
            return choice(empty_corners)
        
        # Пытаемся занять центральные клетки
        center_cells = []
        for i in range(1, size-1):
            for j in range(1, size-1):
                if game_logic.grid[i][j] == '':
                    center_cells.append((i, j))
        if center_cells:
            return choice(center_cells)
        
        # Иначе случайный ход
        return self.make_random_move(game_logic) 