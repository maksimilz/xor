from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Line, Color, Rectangle
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.animation import Animation
from TicTacToeLogic import TicTacToeLogic
from kivy.config import Config
from kivy.support import install_twisted_reactor
from kivy.utils import platform

class TicTacToeCell(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.2, 0.2, 0.2, 1)  # Тёмный фон
        self.font_size = dp(40)
        self.i = 0
        self.j = 0

class TicTacToeBoard(GridLayout):
    def __init__(self, game_logic, **kwargs):
        super().__init__(**kwargs)
        self.game_logic = game_logic
        self.cols = game_logic.grid_size
        self.padding = dp(10)
        self.spacing = dp(5)
        
        # Создаём ячейки
        self.cells = []
        for i in range(self.game_logic.grid_size):
            row = []
            for j in range(self.game_logic.grid_size):
                cell = TicTacToeCell()
                cell.i = i
                cell.j = j
                cell.bind(on_press=self.cell_pressed)
                self.add_widget(cell)
                row.append(cell)
            self.cells.append(row)

    def cell_pressed(self, cell):
        if self.game_logic.game_state != 'playing':
            return
            
        i, j = cell.i, cell.j
        if self.game_logic.is_valid_move(i, j):
            game_over, winner = self.game_logic.make_move(i, j)
            
            # Анимация хода
            self.animate_move(cell, self.game_logic.current_player)
            
            if game_over:
                if winner:
                    self.highlight_winning_line()
                self.parent.update_score()
                self.parent.show_game_over(winner)

    def animate_move(self, cell, player):
        # Анимация появления символа
        cell.text = 'X' if player == 'O' else 'O'
        cell.color = (1, 0.28, 0.34, 0) if player == 'O' else (0.18, 0.83, 0.45, 0)
        anim = Animation(color=(1, 0.28, 0.34, 1) if player == 'O' else (0.18, 0.83, 0.45, 1), 
                        duration=0.3)
        anim.start(cell)

    def highlight_winning_line(self):
        # Подсветка выигрышной линии
        for i, j in self.game_logic.winning_line:
            cell = self.cells[i][j]
            anim = Animation(background_color=(1, 0.83, 0.17, 1), duration=0.3)
            anim.start(cell)

    def reset_board(self):
        for row in self.cells:
            for cell in row:
                cell.text = ''
                cell.background_color = (0.2, 0.2, 0.2, 1)
                cell.color = (1, 1, 1, 1)

    def redraw_board(self):
        """Перерисовать доску на основе текущего состояния игры"""
        for i in range(self.game_logic.grid_size):
            for j in range(self.game_logic.grid_size):
                cell = self.cells[i][j]
                value = self.game_logic.grid[i][j]
                if value:
                    cell.text = value
                    cell.color = (1, 0.28, 0.34, 1) if value == 'O' else (0.18, 0.83, 0.45, 1)

    def undo_move(self, instance):
        if self.game_logic.undo_move():
            self.board.reset_board()
            self.board.redraw_board()
            # Восстанавливаем состояние игры
            self.game_logic.game_state = 'playing'

class TicTacToeGame(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(10)
        
        # Настройка для мобильных устройств
        if platform == 'android' or platform == 'ios':
            Window.softinput_mode = 'below_target'
        
        # Добавляем обработчик события по умолчанию
        def on_swipe(self, *args):
            pass
            
        # Инициализация логики
        self.game_logic = TicTacToeLogic()
        
        # Создаём интерфейс
        self.create_ui()
        
    def create_ui(self):
        # Счёт
        self.score_label = Label(
            text=f"X: {self.game_logic.points['X']} | O: {self.game_logic.points['O']}",
            size_hint_y=None,
            height=dp(50),
            font_size=dp(24)
        )
        self.add_widget(self.score_label)
        
        # Игровое поле
        self.board = TicTacToeBoard(self.game_logic)
        self.add_widget(self.board)
        
        # Кнопки управления
        controls = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        undo_button = Button(
            text="Отменить",
            background_color=(0.45, 0.49, 0.55, 1),
            on_press=self.undo_move
        )
        
        new_game_button = Button(
            text="Новая игра",
            background_color=(0.18, 0.83, 0.45, 1),
            on_press=self.new_game
        )
        
        reset_score_button = Button(
            text="Сброс счёта",
            background_color=(1, 0.28, 0.34, 1),
            on_press=self.reset_score
        )
        
        controls.add_widget(undo_button)
        controls.add_widget(new_game_button)
        controls.add_widget(reset_score_button)
        self.add_widget(controls)

    def update_score(self):
        self.score_label.text = f"X: {self.game_logic.points['X']} | O: {self.game_logic.points['O']}"

    def show_game_over(self, winner):
        if winner:
            text = f"Победил игрок {winner}!"
        else:
            text = "Ничья!"
            
        label = Label(
            text=text,
            font_size=dp(30),
            color=(1, 1, 1, 0)
        )
        self.add_widget(label)
        
        # Анимация появления текста
        anim = Animation(color=(1, 1, 1, 1), duration=0.5)
        anim.start(label)

    def undo_move(self, instance):
        if self.game_logic.undo_move():
            self.board.reset_board()
            self.board.redraw_board()

    def new_game(self, instance):
        self.game_logic.reset_game()
        self.board.reset_board()
        # Удаляем сообщение о победе, если оно есть
        for child in self.children[:]:
            if isinstance(child, Label) and child != self.score_label:
                self.remove_widget(child)

    def reset_score(self, instance):
        self.game_logic.reset_points()
        self.update_score()

    def on_touch_move(self, touch):
        # Добавляем поддержку жеста "смахивания" для отмены хода
        if touch.dx < -50:  # Смахивание влево
            self.undo_move(None)
            return True
        return super().on_touch_move(touch)

class TicTacToeMobileApp(App):
    def build(self):
        # Настройка для мобильных устройств
        if platform == 'android' or platform == 'ios':
            Window.clearcolor = (0.12, 0.12, 0.12, 1)
            Config.set('graphics', 'fullscreen', 'auto')
            Config.set('graphics', 'multitouch', 'auto')
            
        return TicTacToeGame()

if __name__ == '__main__':
    TicTacToeMobileApp().run()
