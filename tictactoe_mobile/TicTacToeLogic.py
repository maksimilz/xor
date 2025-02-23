class TicTacToeLogic:
    def __init__(self, grid_size=3):
        # Добавляем возможность изменять размер поля
        self.grid_size = grid_size
        self.grid = [['' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.current_player = 'X'
        self.points = {'X': 0, 'O': 0}
        self.game_over = False
        self.winning_line = []
        self.moves_history = []
        self.last_move = None  # Добавляем отслеживание последнего хода для анимации
        self.game_state = 'playing'  # Добавляем состояние игры: 'playing', 'paused', 'ended'
    
    def get_game_state(self):
        """Получить текущее состояние игры для сохранения"""
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
        """Загрузить сохранённое состояние игры"""
        self.grid = state['grid']
        self.current_player = state['current_player']
        self.points = state['points']
        self.game_over = state['game_over']
        self.winning_line = state['winning_line']
        self.moves_history = state['moves_history']
        self.game_state = state['game_state']
    
    def pause_game(self):
        """Поставить игру на паузу"""
        if self.game_state == 'playing':
            self.game_state = 'paused'
            return True
        return False
    
    def resume_game(self):
        """Возобновить игру"""
        if self.game_state == 'paused':
            self.game_state = 'playing'
            return True
        return False

    def make_move(self, i, j):
        if self.game_state != 'playing':
            return False, None
            
        if self.grid[i][j] == '' and not self.game_over:
            self.grid[i][j] = self.current_player
            self.moves_history.append((i, j, self.current_player))
            self.last_move = (i, j)  # Сохраняем последний ход
            
            if self.check_win(i, j):
                self.game_over = True
                self.game_state = 'ended'
                self.points[self.current_player] += 1
                return True, self.current_player
            elif self.check_draw():
                self.game_over = True
                self.game_state = 'ended'
                return True, None
            
            self.current_player = 'O' if self.current_player == 'X' else 'X'
            return False, None
        return False, None

    def get_last_move(self):
        """Получить координаты последнего хода для анимации"""
        return self.last_move

    def get_board_size(self):
        """Получить размер игрового поля"""
        return self.grid_size

    def can_continue(self):
        """Проверить, можно ли продолжить игру"""
        return self.game_state != 'ended'

    def get_statistics(self):
        """Получить статистику игры"""
        return {
            'total_moves': len(self.moves_history),
            'points': self.points,
            'current_streak': self._calculate_streak()
        }

    def _calculate_streak(self):
        """Подсчёт текущей серии побед"""
        streak = {'X': 0, 'O': 0}
        for _, _, player in reversed(self.moves_history):
            if player == self.current_player:
                streak[player] += 1
            else:
                break
        return streak

    def check_win(self, i, j):
        # Проверка по горизонтали
        if all(cell == self.grid[i][j] for cell in self.grid[i]):
            self.winning_line = [(i, col) for col in range(self.grid_size)]
            return True
        
        # Проверка по вертикали
        if all(row[j] == self.grid[i][j] for row in self.grid):
            self.winning_line = [(row, j) for row in range(self.grid_size)]
            return True
        
        # Проверка главной диагонали
        if i == j and all(self.grid[k][k] == self.grid[i][j] for k in range(self.grid_size)):
            self.winning_line = [(k, k) for k in range(self.grid_size)]
            return True
        
        # Проверка побочной диагонали
        if i + j == 2 and all(self.grid[k][2-k] == self.grid[i][j] for k in range(self.grid_size)):
            self.winning_line = [(k, 2-k) for k in range(self.grid_size)]
            return True
        
        return False

    def check_draw(self):
        """Проверка на ничью"""
        # Добавляем проверку на выигрыш, чтобы избежать ложной ничьей
        if self.winning_line:
            return False
        return all(all(cell != '' for cell in row) for row in self.grid)

    def undo_move(self):
        """Отменить последний ход"""
        if self.moves_history:
            i, j, player = self.moves_history.pop()
            self.grid[i][j] = ''
            self.current_player = player
            self.game_over = False
            self.winning_line = []
            return True
        return False

    def reset_game(self):
        self.grid = [['' for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.current_player = 'X'
        self.game_over = False
        self.winning_line = []
        self.moves_history = []
        self.game_state = 'playing'

    def reset_points(self):
        self.points = {'X': 0, 'O': 0}

    def get_empty_cells(self):
        """Получить список пустых клеток"""
        empty_cells = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.grid[i][j] == '':
                    empty_cells.append((i, j))
        return empty_cells

    def is_valid_move(self, i, j):
        """Проверить, возможен ли ход в указанную клетку"""
        return 0 <= i < self.grid_size and 0 <= j < self.grid_size and self.grid[i][j] == '' and not self.game_over
