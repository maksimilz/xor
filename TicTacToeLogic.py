from time import time

class TicTacToeLogic:
    def __init__(self, grid_size=3):
        self.grid_size = grid_size
        self.grid = [['' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.current_player = 'O'  # O всегда ходит первым
        self.points = {'X': 0, 'O': 0}
        self.game_over = False
        self.winning_line = []
        self.moves_history = []
        self.last_move = None
        self.game_state = 'playing'
        self.time_spent = {'X': 0, 'O': 0}  # Время каждого игрока
        self.move_start_time = None  # Время начала текущего хода
        self.bot_enabled = False
        self.bot_symbol = None  # 'X' или 'O'
        self.bot = None

    def get_game_state(self):
        return {
            'grid': self.grid,
            'current_player': self.current_player,
            'points': self.points,
            'game_over': self.game_over,
            'winning_line': self.winning_line,
            'moves_history': self.moves_history,
            'game_state': self.game_state
        }

    def load_game_state(self, state):
        self.grid = state['grid']
        self.current_player = state['current_player']
        self.points = state['points']
        self.game_over = state['game_over']
        self.winning_line = state['winning_line']
        self.moves_history = state['moves_history']
        self.game_state = state['game_state']

    def pause_game(self):
        if self.game_state == 'playing':
            self.game_state = 'paused'
            return True
        return False

    def resume_game(self):
        if self.game_state == 'paused':
            self.game_state = 'playing'
            return True
        return False

    def make_move(self, i, j):
        """Делает ход в указанную позицию"""
        if self.game_state != 'playing':
            print(f"Game state is not playing: {self.game_state}")  # Отладка
            return False, None

        # Обновляем время предыдущего хода
        if self.move_start_time is not None:
            elapsed = time() - self.move_start_time
            self.time_spent[self.current_player] += elapsed

        # Проверяем, что ход допустим
        if not self.is_valid_move(i, j):
            print(f"Invalid move at {i},{j}")  # Отладка
            return False, None

        # Делаем ход
        self.grid[i][j] = self.current_player
        self.moves_history.append((i, j, self.current_player))
        self.last_move = (i, j)
        
        print(f"Move made by {self.current_player} at {i},{j}")  # Отладка

        # Проверяем победу или ничью
        if self.check_win(i, j):
            self.game_over = True
            self.game_state = 'ended'
            self.points[self.current_player] += 1
            print(f"Player {self.current_player} wins!")  # Отладка
            return True, self.current_player

        if self.check_draw():
            self.game_over = True
            self.game_state = 'ended'
            print("Game ends in draw")  # Отладка
            return True, None

        # Меняем игрока
        old_player = self.current_player
        self.current_player = 'X' if self.current_player == 'O' else 'O'
        print(f"Current player changed from {old_player} to {self.current_player}")  # Отладка
        self.move_start_time = time()

        return True, None

    def get_last_move(self):
        return self.last_move

    def get_board_size(self):
        return self.grid_size

    def can_continue(self):
        return self.game_state != 'ended'

    def get_statistics(self):
        return {
            'total_moves': len(self.moves_history),
            'points': self.points,
            'current_streak': self._calculate_streak()
        }

    def _calculate_streak(self):
        streak = {'X': 0, 'O': 0}
        for _, _, player in reversed(self.moves_history):
            if player == self.current_player:
                streak[player] += 1
            else:
                break
        return streak

    def check_win(self, i, j):
        """
        Проверяет все возможные выигрышные комбинации после хода в позицию (i, j)
        """
        player = self.grid[i][j]
        size = self.grid_size
        
        # Количество символов для победы
        needed_to_win = 3  # для поля 3x3 нужно 3 в ряд
        if size == 4:
            needed_to_win = 4  # для 4x4 нужно 4 в ряд
        elif size >= 5:
            needed_to_win = 5  # для 5x5 и больше нужно 5 в ряд

        # Проверяем горизонталь
        count = 0
        line = []
        for col in range(size):
            if self.grid[i][col] == player:
                count += 1
                line.append((i, col))
            else:
                count = 0
                line = []
            if count >= needed_to_win:
                self.winning_line = line
                return True

        # Проверяем вертикаль
        count = 0
        line = []
        for row in range(size):
            if self.grid[row][j] == player:
                count += 1
                line.append((row, j))
            else:
                count = 0
                line = []
            if count >= needed_to_win:
                self.winning_line = line
                return True

        # Проверяем главную диагональ
        count = 0
        line = []
        start_i = i - min(i, j)
        start_j = j - min(i, j)
        while start_i < size and start_j < size:
            if self.grid[start_i][start_j] == player:
                count += 1
                line.append((start_i, start_j))
            else:
                count = 0
                line = []
            if count >= needed_to_win:
                self.winning_line = line
                return True
            start_i += 1
            start_j += 1

        # Проверяем побочную диагональ
        count = 0
        line = []
        start_i = i + min(size - 1 - i, j)
        start_j = j - min(size - 1 - i, j)
        while start_i >= 0 and start_j < size:
            if self.grid[start_i][start_j] == player:
                count += 1
                line.append((start_i, start_j))
            else:
                count = 0
                line = []
            if count >= needed_to_win:
                self.winning_line = line
                return True
            start_i -= 1
            start_j += 1

        return False

    def check_draw(self):
        """
        Проверяет ничью (все клетки заполнены)
        """
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j] == '':
                    return False
        return True

    def undo_move(self):
        """Отменяет последний ход"""
        if self.moves_history:
            i, j, player = self.moves_history.pop()
            self.grid[i][j] = ''
            self.current_player = player
            self.game_over = False
            self.winning_line = []
            self.game_state = 'playing'
            
            # Сбрасываем время последнего хода
            if self.move_start_time is not None:
                self.time_spent[player] -= (time() - self.move_start_time)
                if self.time_spent[player] < 0:
                    self.time_spent[player] = 0
            self.move_start_time = time()
            
            return True
        return False

    def reset_game(self):
        self.grid = [['' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.current_player = 'O'  # O всегда ходит первым при новой игре
        self.game_over = False
        self.winning_line = []
        self.moves_history = []
        self.game_state = 'playing'
        self.time_spent = {'X': 0, 'O': 0}
        self.move_start_time = time()

    def reset_points(self):
        self.points = {'X': 0, 'O': 0}

    def get_empty_cells(self):
        empty_cells = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j] == '':
                    empty_cells.append((i, j))
        return empty_cells

    def is_valid_move(self, i, j):
        """
        Проверяет, допустим ли ход в указанную позицию
        """
        return (0 <= i < self.grid_size and 
                0 <= j < self.grid_size and 
                self.grid[i][j] == '' and 
                not self.game_over and 
                self.game_state == 'playing')

    def save_game_to_file(self, filename="game_save.json"):
        """
        Сохраняет текущее состояние игры в файл
        """
        import json
        
        save_state = {
            'grid': self.grid,
            'current_player': self.current_player,
            'points': self.points,
            'moves_history': self.moves_history,
            'game_state': self.game_state
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(save_state, f)
            return True
        except:
            return False

    def load_game_from_file(self, filename="game_save.json"):
        """
        Загружает состояние игры из файла
        """
        import json
        
        try:
            with open(filename, 'r') as f:
                save_state = json.load(f)
                
            self.grid = save_state['grid']
            self.current_player = save_state['current_player']
            self.points = save_state['points']
            self.moves_history = save_state['moves_history']
            self.game_state = save_state['game_state']
            return True
        except:
            return False

    def get_detailed_statistics(self):
        """
        Возвращает подробную статистику игры
        """
        x_moves = sum(1 for _, _, player in self.moves_history if player == 'X')
        o_moves = sum(1 for _, _, player in self.moves_history if player == 'O')
        
        return {
            'total_games': sum(self.points.values()),
            'x_wins': self.points['X'],
            'o_wins': self.points['O'],
            'total_moves': len(self.moves_history),
            'x_moves': x_moves,
            'o_moves': o_moves,
            'average_moves_per_game': len(self.moves_history) / max(sum(self.points.values()), 1),
            'current_streak': self._calculate_streak()
        }

    def get_time_spent(self):
        """
        Возвращает время, потраченное каждым игроком
        """
        # Добавляем текущее незавершенное время
        current_times = self.time_spent.copy()
        
        # Добавляем текущее время только если игра идёт и есть начальное время
        if self.move_start_time is not None:
            if self.game_state == 'playing':
                elapsed = time() - self.move_start_time
                current_times[self.current_player] += elapsed
            elif self.game_state == 'ended' and not self.game_over:
                # Добавляем последнее время, если игра только что закончилась
                elapsed = time() - self.move_start_time
                current_times[self.current_player] += elapsed
                self.time_spent = current_times.copy()  # Сохраняем финальное время
                self.game_over = True
        
        return current_times

    def set_bot(self, bot, symbol):
        """Включает игру с ботом"""
        self.bot_enabled = True
        self.bot_symbol = symbol
        self.bot = bot

    def disable_bot(self):
        """Выключает игру с ботом"""
        self.bot_enabled = False
        self.bot_symbol = None
        self.bot = None
