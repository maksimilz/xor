from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Line, Color, Rectangle, Ellipse
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.animation import Animation
from TicTacToeLogic import TicTacToeLogic
from kivy.clock import Clock
from random import random
from math import pi, cos, sin

class TicTacToeCell(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.2, 0.2, 0.2, 1)
        self.background_normal = ''
        self.background_down = ''
        self.size_hint = (1, 1)
        self.font_size = dp(40)
        self.i = 0
        self.j = 0
        
        # Возвращаем эффекты при наведении
        self.bind(on_enter=self.on_mouse_enter)
        self.bind(on_leave=self.on_mouse_leave)
    
    def on_press(self):
        """Простой эффект нажатия"""
        Animation(
            background_color=(0.25, 0.25, 0.25, 1),
            duration=0.1
        ).start(self)

    def on_release(self):
        """Возврат к исходному цвету"""
        Animation(
            background_color=(0.2, 0.2, 0.2, 1),
            duration=0.1
        ).start(self)

    def on_mouse_enter(self, *args):
        if not self.text:  # Только для пустых ячеек
            Animation(
                background_color=(0.25, 0.25, 0.25, 1),
                duration=0.2
            ).start(self)
    
    def on_mouse_leave(self, *args):
        if not self.text:  # Только для пустых ячеек
            Animation(
                background_color=(0.2, 0.2, 0.2, 1),
                duration=0.2
            ).start(self)

class TicTacToeBoard(GridLayout):
    def __init__(self, game_logic, game_ui, **kwargs):
        super().__init__(**kwargs)
        self.game_logic = game_logic
        self.game_ui = game_ui
        self.cols = game_logic.grid_size
        self.padding = dp(10)
        self.spacing = dp(5)
        
        # Растягиваем поле по обоим измерениям
        self.size_hint = (1, 1)
        
        # Изменяем структуру хранения анимаций
        self.winning_animations = {}  # словарь {cell: animation}
        
        # Адаптируем размер шрифта в зависимости от размера поля
        self.cell_font_size = dp(60 - (self.cols - 3) * 15)

        # Добавляем градиентный фон
        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            self.background = Rectangle(pos=self.pos, size=self.size)
            
            # Мягкое свечение по краям
            Color(0.2, 0.2, 0.2, 0.3)
            self.top_gradient = Rectangle(
                pos=self.pos,
                size=(self.width, dp(50))
            )
            self.bottom_gradient = Rectangle(
                pos=(self.x, self.y + self.height - dp(50)),
                size=(self.width, dp(50))
            )
            self.left_gradient = Rectangle(
                pos=self.pos,
                size=(dp(50), self.height)
            )
            self.right_gradient = Rectangle(
                pos=(self.x + self.width - dp(50), self.y),
                size=(dp(50), self.height)
            )

        # Создаём ячейки
        self.cells = []
        for i in range(self.game_logic.grid_size):
            row = []
            for j in range(self.game_logic.grid_size):
                cell = TicTacToeCell()
                cell.i = i
                cell.j = j
                cell.font_size = self.cell_font_size
                cell.bind(on_press=self.cell_pressed)
                self.add_widget(cell)
                row.append(cell)
            self.cells.append(row)

        # Привязываем обновление фона к изменению размера
        self.bind(pos=self.update_background, size=self.update_background)

    def update_background(self, *args):
        """Обновляет позицию и размер фона при изменении размера виджета"""
        self.background.pos = self.pos
        self.background.size = self.size
        
        # Обновляем градиенты
        self.top_gradient.pos = self.pos
        self.top_gradient.size = (self.width, dp(50))
        
        self.bottom_gradient.pos = (self.x, self.y + self.height - dp(50))
        self.bottom_gradient.size = (self.width, dp(50))
        
        self.left_gradient.pos = self.pos
        self.left_gradient.size = (dp(50), self.height)
        
        self.right_gradient.pos = (self.x + self.width - dp(50), self.y)
        self.right_gradient.size = (dp(50), self.height)

    def cell_pressed(self, cell):
        if self.game_logic.game_state != 'playing':
            return

        i, j = cell.i, cell.j
        if not self.game_logic.is_valid_move(i, j):
            return
        
        if self.game_logic.bot_enabled and self.game_logic.current_player == self.game_logic.bot_symbol:
            return
        
        current_player = self.game_logic.current_player
        success, winner = self.game_logic.make_move(i, j)

        if success:
            self.animate_move(cell, current_player)

            if self.game_logic.game_over:
                if winner:
                    self.highlight_winning_line()
                self.game_ui.update_score()
                self.game_ui.show_game_over(winner)
            elif self.game_logic.bot_enabled and self.game_logic.current_player == self.game_logic.bot_symbol:
                Clock.schedule_once(lambda dt: self.make_bot_move(), 0.5)

    def animate_move(self, cell, player):
        """Анимация хода с эффектом волны"""
        # Базовая анимация символа
        cell.text = player
        cell.font_size = self.cell_font_size
        cell.color = (1, 0.28, 0.34, 0) if player == 'X' else (0.18, 0.83, 0.45, 0)
        
        # Анимация появления символа
        anim = Animation(
            color=(1, 0.28, 0.34, 1) if player == 'X' else (0.18, 0.83, 0.45, 1),
            duration=0.2
        )
        anim.start(cell)
        
        # Создаем эффект волны для соседних ячеек
        i, j = cell.i, cell.j
        neighbors = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                ni, nj = i + di, j + dj
                if (0 <= ni < self.game_logic.grid_size and 
                    0 <= nj < self.game_logic.grid_size and 
                    (di != 0 or dj != 0)):
                    neighbors.append((ni, nj, abs(di) + abs(dj)))
        
        # Волновой эффект для соседей (только изменение цвета фона)
        for ni, nj, dist in neighbors:
            neighbor = self.cells[ni][nj]
            delay = dist * 0.1
            wave_anim = (
                Animation(
                    background_color=(0.25, 0.25, 0.25, 1),
                    duration=0.2
                ) + 
                Animation(
                    background_color=(0.2, 0.2, 0.2, 1),
                    duration=0.2
                )
            )
            Clock.schedule_once(lambda dt, n=neighbor, a=wave_anim: a.start(n), delay)

    def highlight_winning_line(self):
        """Анимированная подсветка победной линии"""
        # Сначала плавно затемняем все ячейки
        for i in range(self.game_logic.grid_size):
            for j in range(self.game_logic.grid_size):
                cell = self.cells[i][j]
                if (i, j) not in self.game_logic.winning_line:
                    # Мягкое затемнение для неактивных ячеек
                    anim = Animation(
                        background_color=(0.18, 0.18, 0.18, 1),
                        opacity=0.7,
                        duration=0.5
                    )
                    anim.start(cell)
                    self.winning_animations[cell] = anim

        # Затем последовательно подсвечиваем победные ячейки
        for idx, (i, j) in enumerate(self.game_logic.winning_line):
            cell = self.cells[i][j]
            delay = idx * 0.2  # Задержка для последовательной анимации
            
            # Сохраняем текущий цвет текста
            text_color = (1, 0.28, 0.34, 1) if cell.text == 'X' else (0.18, 0.83, 0.45, 1)
            
            # Анимация победной ячейки
            win_anim = (
                Animation(
                    background_color=(1, 0.83, 0.17, 0.1),  # Начальный цвет подсветки
                    opacity=1,
                    duration=0.3
                ) + 
                Animation(
                    background_color=(1, 0.83, 0.17, 0.3),  # Конечный цвет подсветки
                    duration=0.2
                )
            )
            
            # Запускаем анимацию с задержкой
            Clock.schedule_once(
                lambda dt, c=cell, a=win_anim: a.start(c), 
                delay
            )
            
            # Сохраняем анимацию
            self.winning_animations[cell] = win_anim
            
            # Устанавливаем цвет символа
            cell.color = text_color

    def reset_board(self):
        """Простой сброс доски без анимации"""
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
                    cell.color = (1, 0.28, 0.34, 1) if value == 'X' else (0.18, 0.83, 0.45, 1)

    def undo_move(self, instance):
        if self.game_logic.undo_move():
            self.reset_board()
            self.redraw_board()
            # Восстанавливаем состояние игры
            self.game_logic.game_state = 'playing'
            
            # Если после отмены хода сейчас ход бота, отменяем еще один ход
            # чтобы вернуться к ходу игрока
            if (self.game_logic.bot_enabled and 
                self.game_logic.current_player == self.game_logic.bot_symbol):
                if self.game_logic.undo_move():
                    self.reset_board()
                    self.redraw_board()
                    self.game_logic.game_state = 'playing'
            
            # Обновляем отображение времени
            times = self.game_logic.get_time_spent()
            self.game_ui.x_time_label.text = self.game_ui.format_time(times['X'])
            self.game_ui.o_time_label.text = self.game_ui.format_time(times['O'])
            
            # Обновляем цвета таймеров
            if self.game_logic.current_player == 'X':
                self.game_ui.x_time_label.color = (1, 0.28, 0.34, 1)  # Активный X
                self.game_ui.o_time_label.color = (0.7, 0.7, 0.7, 1)  # Неактивный O
            else:
                self.game_ui.x_time_label.color = (0.7, 0.7, 0.7, 1)  # Неактивный X
                self.game_ui.o_time_label.color = (0.18, 0.83, 0.45, 1)  # Активный O

    def make_bot_move(self):
        """Выполняет ход бота"""
        print(f"Bot move called. Game state: {self.game_logic.game_state}")
        print(f"Bot enabled: {self.game_logic.bot_enabled}")
        print(f"Current player: {self.game_logic.current_player}")
        print(f"Bot symbol: {self.game_logic.bot_symbol}")
        
        if (self.game_logic.game_state == 'playing' and 
            self.game_logic.bot_enabled and 
            self.game_logic.current_player == self.game_logic.bot_symbol):
            
            # Проверяем, есть ли доступные ходы
            empty_cells = self.game_logic.get_empty_cells()
            print(f"Empty cells available: {empty_cells}")
            if not empty_cells:
                print("No empty cells available")
                return
            
            bot_move = self.game_logic.bot.make_move(self.game_logic)
            print(f"Bot suggested move: {bot_move}")
            
            if bot_move and self.game_logic.is_valid_move(bot_move[0], bot_move[1]):
                i, j = bot_move
                current_player = self.game_logic.current_player
                print(f"Making bot move at {i},{j} for player {current_player}")
                
                success, winner = self.game_logic.make_move(i, j)
                print(f"Bot move success: {success}, winner: {winner}")
                
                if success:
                    cell = self.cells[i][j]
                    self.animate_move(cell, current_player)
                    
                    if self.game_logic.game_over:
                        if winner:
                            self.highlight_winning_line()
                        self.game_ui.update_score()
                        self.game_ui.show_game_over(winner)
                    elif not self.game_logic.get_empty_cells():
                        self.game_ui.show_game_over(None)  # Ничья
                    else:
                        print("Game continues after bot move")
            else:
                print("Invalid bot move suggested")
        else:
            print("Bot move conditions not met")

    def stop_all_animations(self):
        """Останавливает все активные анимации"""
        # Останавливаем анимации победной линии
        for cell, anim in list(self.winning_animations.items()):
            if anim:
                Animation.cancel_all(cell)  # Останавливаем все анимации для ячейки
        self.winning_animations.clear()
        
        # Останавливаем анимации всех ячеек
        for row in self.cells:
            for cell in row:
                Animation.cancel_all(cell)
                cell.opacity = 1  # Сбрасываем прозрачность
                cell.background_color = (0.2, 0.2, 0.2, 1)  # Сбрасываем цвет фона

class TicTacToeGame(BoxLayout):
    def __init__(self, player_side='X', difficulty='легко', grid_size=3, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(10)

        # Инициализация логики с выбранным размером поля
        self.game_logic = TicTacToeLogic(grid_size=grid_size)
        
        # Настройка бота
        from TicTacToeBot import TicTacToeBot
        bot = TicTacToeBot(difficulty=difficulty.lower())
        bot_symbol = 'O' if player_side == 'X' else 'X'
        print(f"Initializing bot with symbol: {bot_symbol}, difficulty: {difficulty}, grid size: {grid_size}")
        self.game_logic.set_bot(bot, bot_symbol)

        # Создаём интерфейс
        self.create_ui()
        
        # Устанавливаем O как первого игрока всегда
        self.game_logic.current_player = 'O'
        
        # Если бот играет за O, он ходит первым
        if bot_symbol == 'O':
            print("Bot (O) goes first, scheduling first move")
            Clock.schedule_once(lambda dt: self.board.make_bot_move(), 0.5)

        # Добавляем переменные для хранения текущих анимаций
        self.x_pulse_anim = None
        self.o_pulse_anim = None
        self.current_pulse_player = None

    def create_ui(self):
        # Создаем горизонтальный layout для бокового меню и игрового поля
        main_layout = BoxLayout(orientation='horizontal', spacing=dp(10))
        
        # Создаем боковое меню
        side_menu = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10),
            size_hint_x=0.3  # Занимает 30% ширины
        )
        
        # Заголовок меню
        menu_title = Label(
            text="Меню",
            size_hint_y=None,
            height=dp(40),
            font_size=dp(24),
            bold=True
        )
        side_menu.add_widget(menu_title)
        
        # Добавляем разделитель
        side_menu.add_widget(Widget(size_hint_y=None, height=dp(20)))
        
        # Создаем контейнер для таймеров
        timers_container = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            height=dp(80)
        )
        
        # Таймер для X
        x_timer = BoxLayout(
            size_hint_y=None,
            height=dp(35),
            spacing=dp(10)
        )
        self.x_icon = Label(
            text='X',
            color=(1, 0.28, 0.34, 1),  # Красный цвет
            font_size=dp(24),
            bold=True,
            size_hint_x=None,
            width=dp(30)
        )
        self.x_time_label = Label(
            text='0:00',
            color=(1, 1, 1, 1),
            font_size=dp(20)
        )
        x_timer.add_widget(self.x_icon)
        x_timer.add_widget(self.x_time_label)
        
        # Таймер для O
        o_timer = BoxLayout(
            size_hint_y=None,
            height=dp(35),
            spacing=dp(10)
        )
        self.o_icon = Label(
            text='O',
            color=(0.18, 0.83, 0.45, 1),  # Зеленый цвет
            font_size=dp(24),
            bold=True,
            size_hint_x=None,
            width=dp(30)
        )
        self.o_time_label = Label(
            text='0:00',
            color=(1, 1, 1, 1),
            font_size=dp(20)
        )
        o_timer.add_widget(self.o_icon)
        o_timer.add_widget(self.o_time_label)
        
        # Добавляем таймеры в контейнер
        timers_container.add_widget(x_timer)
        timers_container.add_widget(o_timer)
        
        # Добавляем контейнер с таймерами в боковое меню
        side_menu.add_widget(timers_container)
        
        # Добавляем метку для сообщения о победителе под счётом
        self.result_label = Label(
            text="",
            size_hint_y=None,
            height=dp(30),
            font_size=dp(20),
            color=(1, 1, 1, 0)  # Начально невидимый
        )
        side_menu.add_widget(self.result_label)
        
        # Счёт
        self.score_label = Label(
            text=f"X: {self.game_logic.points['X']} | O: {self.game_logic.points['O']}",
            size_hint_y=None,
            height=dp(30),
            font_size=dp(20)
        )
        side_menu.add_widget(self.score_label)
        
        # Добавляем разделитель
        side_menu.add_widget(Widget(size_hint_y=None, height=dp(20)))
        
        # Кнопки управления
        self.undo_button = Button(
            text="Отменить",
            background_color=(0.45, 0.49, 0.55, 1),
            size_hint_y=None,
            height=dp(40),
            on_press=self.undo_move
        )
        
        new_game_button = Button(
            text="Новая игра",
            background_color=(0.18, 0.83, 0.45, 1),
            size_hint_y=None,
            height=dp(40),
            on_press=self.new_game
        )
        
        reset_score_button = Button(
            text="Сброс счёта",
            background_color=(1, 0.28, 0.34, 1),
            size_hint_y=None,
            height=dp(40),
            on_press=self.reset_score
        )

        back_to_menu_button = Button(
            text="В главное меню",
            background_color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(40),
            on_press=self.back_to_menu
        )
        
        side_menu.add_widget(self.undo_button)
        side_menu.add_widget(new_game_button)
        side_menu.add_widget(reset_score_button)
        side_menu.add_widget(back_to_menu_button)
        
        # Добавляем растягивающийся виджет, чтобы прижать всё остальное к верху
        side_menu.add_widget(Widget())
        
        # Изменяем контейнер для игрового поля
        game_container = BoxLayout(
            orientation='vertical',
            padding=dp(10),
            size_hint=(0.7, 1)  # 70% ширины, полная высота
        )
        
        # Создаем игровое поле
        self.board = TicTacToeBoard(self.game_logic, self)
        
        # Добавляем поле напрямую в игровой контейнер
        game_container.add_widget(self.board)
        
        # Добавляем меню и игровой контейнер в главный layout
        main_layout.add_widget(side_menu)
        main_layout.add_widget(game_container)
        
        # Добавляем главный layout в окно
        self.add_widget(main_layout)
        
        # Запускаем обновление времени
        Clock.schedule_interval(self.update_time, 0.1)

        # Добавляем анимацию для кнопок меню
        for button in [self.undo_button, new_game_button, reset_score_button, back_to_menu_button]:
            button.bind(on_press=lambda x, btn=button: self.animate_button_press(btn))

    def update_score(self):
        """Обновление счета с анимацией"""
        old_text = self.score_label.text
        new_text = f"X: {self.game_logic.points['X']} | O: {self.game_logic.points['O']}"
        
        if old_text != new_text:
            # Анимация обновления счета
            anim = (
                Animation(font_size=dp(24), duration=0.1) +
                Animation(font_size=dp(20), duration=0.1)
            )
            self.score_label.text = new_text
            anim.start(self.score_label)

    def show_game_over(self, winner):
        """Показ окончания игры с анимацией"""
        if winner:
            text = f"Победил игрок {winner}!"
            color = (1, 0.28, 0.34, 1) if winner == 'X' else (0.18, 0.83, 0.45, 1)
        else:
            text = "Ничья!"
            color = (1, 1, 1, 1)
        
        self.result_label.text = text
        self.result_label.color = (*color[:3], 0)  # Начинаем с прозрачного
        
        # Анимация появления текста
        text_anim = (
            Animation(color=(*color[:3], 1), duration=0.5) +
            Animation(color=(*color[:3], 0.8), duration=0.2) +
            Animation(color=(*color[:3], 1), duration=0.2)
        )
        text_anim.start(self.result_label)

    def undo_move(self, instance):
        if self.game_logic.undo_move():
            self.board.reset_board()
            self.board.redraw_board()

    def new_game(self, instance):
        # Останавливаем анимации при новой игре
        if hasattr(self, 'board'):
            self.board.stop_all_animations()
        
        self.game_logic.reset_game()
        self.board.reset_board()
        # Обновляем время на 0:00
        self.x_time_label.text = '0:00'
        self.o_time_label.text = '0:00'
        self.x_time_label.color = (1, 0.28, 0.34, 1)  # Активный X
        self.o_time_label.color = (0.7, 0.7, 0.7, 1)  # Неактивный O
        # Скрываем сообщение о победе
        anim = Animation(color=(*self.result_label.color[:3], 0), duration=0.3)
        anim.start(self.result_label)
        # Разблокируем кнопку отмены хода
        self.undo_button.disabled = False
        self.undo_button.background_color = (0.45, 0.49, 0.55, 1)
        
        # Если бот ходит первым
        if self.game_logic.current_player == self.game_logic.bot_symbol:
            Clock.schedule_once(lambda dt: self.board.make_bot_move(), 0.5)

    def reset_score(self, instance):
        self.game_logic.reset_points()
        self.update_score()

    def on_touch_move(self, touch):
        # Добавляем поддержку жеста "смахивания" для отмены хода
        if touch.dx < -50:  # Смахивание влево
            self.undo_move(None)
            return True
        return super().on_touch_move(touch)

    def back_to_menu(self, instance):
        # Останавливаем анимации при возврате в меню
        if hasattr(self, 'board'):
            self.board.stop_all_animations()
        
        # Анимация затухания
        fade_out = Animation(opacity=0, duration=0.3)
        def on_complete(anim, widget):
            Clock.unschedule(self.update_time)
            app = App.get_running_app()
            app.show_start_menu()
        fade_out.bind(on_complete=on_complete)
        fade_out.start(self)

    def format_time(self, seconds):
        """Форматирует время в минуты и секунды"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"

    def update_time(self, dt):
        """Обновляет отображение времени с пульсацией"""
        if self.game_logic.game_state == 'playing':
            times = self.game_logic.get_time_spent()
            
            # Обновляем таймеры
            self.x_time_label.text = self.format_time(times['X'])
            self.o_time_label.text = self.format_time(times['O'])
            
            # Анимация активного игрока
            if self.game_logic.current_player == 'X':
                # Подсветка для X
                self.x_time_label.color = (1, 0.28, 0.34, 1)  # Активный красный
                self.o_time_label.color = (0.7, 0.7, 0.7, 1)  # Неактивный серый
                
                # Мягкая пульсация текста
                anim = (
                    Animation(opacity=0.7, duration=0.5) +
                    Animation(opacity=1, duration=0.5)
                )
                anim.repeat = True
                anim.start(self.x_icon)
                
                # Останавливаем пульсацию для O
                if hasattr(self, 'o_pulse_anim'):
                    Animation.cancel_all(self.o_icon)
                self.o_icon.opacity = 1
                
            else:
                # Подсветка для O
                self.o_time_label.color = (0.18, 0.83, 0.45, 1)  # Активный зеленый
                self.x_time_label.color = (0.7, 0.7, 0.7, 1)  # Неактивный серый
                
                # Мягкая пульсация текста
                anim = (
                    Animation(opacity=0.7, duration=0.5) +
                    Animation(opacity=1, duration=0.5)
                )
                anim.repeat = True
                anim.start(self.o_icon)
                
                # Останавливаем пульсацию для X
                if hasattr(self, 'x_pulse_anim'):
                    Animation.cancel_all(self.x_icon)
                self.x_icon.opacity = 1

    def make_bot_move(self):
        """Делегирует ход бота в board"""
        if hasattr(self, 'board'):
            self.board.make_bot_move()

    def animate_button_press(self, button):
        """Анимация нажатия кнопки"""
        original_color = button.background_color
        
        # Анимация нажатия
        anim = (
            Animation(
                background_color=(
                    original_color[0] * 0.8,
                    original_color[1] * 0.8,
                    original_color[2] * 0.8,
                    original_color[3]
                ),
                duration=0.1
            ) +
            Animation(
                background_color=original_color,
                duration=0.1
            )
        )
        anim.start(button)

class StartMenu(BoxLayout):
    def animate_button_hover(self, button, value):
        """Анимация при наведении на кнопку"""
        if value:  # Курсор наведен
            Animation(
                background_color=(
                    button.background_color[0] * 1.2,
                    button.background_color[1] * 1.2,
                    button.background_color[2] * 1.2,
                    button.background_color[3]
                ),
                duration=0.2
            ).start(button)
        else:  # Курсор убран
            Animation(
                background_color=button.background_color,
                duration=0.2
            ).start(button)

    def __init__(self, start_game_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(20)
        self.start_game_callback = start_game_callback

        # Заголовок
        title = Label(
            text="Крестики-нолики",
            font_size=dp(40),
            size_hint_y=None,
            height=dp(60),
            bold=True
        )
        self.add_widget(title)

        # Контейнер для выбора размера поля
        size_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            spacing=dp(10)
        )
        size_label = Label(
            text="Выберите размер поля:",
            font_size=dp(24)
        )
        size_buttons = BoxLayout(spacing=dp(10))
        
        self.size_buttons = []
        sizes = [3, 4, 5]
        for size in sizes:
            btn = Button(
                text=str(size),
                font_size=dp(20),
                background_color=(0.3, 0.3, 0.3, 1)
            )
            btn.bind(on_press=lambda x, s=size: self.select_size(s))
            size_buttons.add_widget(btn)
            self.size_buttons.append(btn)
        
        size_container.add_widget(size_label)
        size_container.add_widget(size_buttons)
        self.add_widget(size_container)

        # Контейнер для выбора стороны
        side_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            spacing=dp(10)
        )
        side_label = Label(
            text="Выберите сторону:",
            font_size=dp(24)
        )
        side_buttons = BoxLayout(spacing=dp(10))
        
        self.x_button = Button(
            text="X",
            font_size=dp(30),
            background_color=(1, 0.28, 0.34, 1)
        )
        self.o_button = Button(
            text="O",
            font_size=dp(30),
            background_color=(0.18, 0.83, 0.45, 1)
        )
        
        self.x_button.bind(on_press=lambda x: self.select_side('X'))
        self.o_button.bind(on_press=lambda x: self.select_side('O'))
        
        side_buttons.add_widget(self.x_button)
        side_buttons.add_widget(self.o_button)
        
        side_container.add_widget(side_label)
        side_container.add_widget(side_buttons)
        self.add_widget(side_container)

        # Контейнер для выбора сложности
        difficulty_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            spacing=dp(10)
        )
        difficulty_label = Label(
            text="Выберите сложность:",
            font_size=dp(24)
        )
        difficulty_buttons = BoxLayout(spacing=dp(10))
        
        difficulties = ['Легко', 'Средне', 'Сложно']
        self.difficulty_buttons = []
        
        for diff in difficulties:
            btn = Button(
                text=diff,
                font_size=dp(20),
                background_color=(0.3, 0.3, 0.3, 1)
            )
            btn.bind(on_press=lambda x, d=diff: self.select_difficulty(d))
            difficulty_buttons.add_widget(btn)
            self.difficulty_buttons.append(btn)
        
        difficulty_container.add_widget(difficulty_label)
        difficulty_container.add_widget(difficulty_buttons)
        self.add_widget(difficulty_container)

        # Кнопка старта
        self.start_button = Button(
            text="Начать игру",
            font_size=dp(26),
            size_hint_y=None,
            height=dp(60),
            background_color=(0.18, 0.83, 0.45, 1),
            disabled=True
        )
        self.start_button.bind(on_press=self.start_game)
        self.add_widget(self.start_button)

        self.selected_side = None
        self.selected_difficulty = None
        self.selected_size = None

        # Добавляем эффект при наведении для всех кнопок
        for btn in self.size_buttons + [self.x_button, self.o_button] + self.difficulty_buttons:
            btn.bind(
                on_enter=lambda x, b=btn: self.animate_button_hover(b, True),
                on_leave=lambda x, b=btn: self.animate_button_hover(b, False)
            )

    def select_size(self, size):
        self.selected_size = size
        for btn in self.size_buttons:
            if int(btn.text) == size:
                btn.background_color = (0.18, 0.83, 0.45, 1)
            else:
                btn.background_color = (0.3, 0.3, 0.3, 1)
        self.check_can_start()

    def select_side(self, side):
        self.selected_side = side
        self.x_button.background_color = (1, 0.28, 0.34, 1) if side == 'X' else (0.7, 0.28, 0.34, 1)
        self.o_button.background_color = (0.18, 0.83, 0.45, 1) if side == 'O' else (0.1, 0.5, 0.3, 1)
        self.check_can_start()

    def select_difficulty(self, difficulty):
        self.selected_difficulty = difficulty
        for btn in self.difficulty_buttons:
            if btn.text == difficulty:
                btn.background_color = (0.18, 0.83, 0.45, 1)
            else:
                btn.background_color = (0.3, 0.3, 0.3, 1)
        self.check_can_start()

    def check_can_start(self):
        self.start_button.disabled = not (self.selected_side and self.selected_difficulty and self.selected_size)

    def start_game(self, instance):
        self.start_game_callback(self.selected_side, self.selected_difficulty.lower(), self.selected_size)

class TicTacToeApp(App):
    def build(self):
        Window.clearcolor = (0.12, 0.12, 0.12, 1)
        self.root = BoxLayout()
        self.show_start_menu()
        return self.root

    def show_start_menu(self):
        start_menu = StartMenu(self.start_game)
        start_menu.opacity = 0
        self.root.clear_widgets()
        self.root.add_widget(start_menu)
        Animation(opacity=1, duration=0.3).start(start_menu)

    def start_game(self, side, difficulty, size):
        game = TicTacToeGame(player_side=side, difficulty=difficulty, grid_size=size)
        game.opacity = 0
        self.root.clear_widgets()
        self.root.add_widget(game)
        Animation(opacity=1, duration=0.3).start(game)

class ShadowButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        with self.canvas.before:
            Color(0, 0, 0, 0.2)
            self.shadow = Rectangle(
                pos=(self.x + dp(2), self.y - dp(2)),
                size=self.size
            )
        
        self.bind(pos=self.update_shadow, size=self.update_shadow)
    
    def update_shadow(self, *args):
        self.shadow.pos = (self.x + dp(2), self.y - dp(2))
        self.shadow.size = self.size

if __name__ == '__main__':
    TicTacToeApp().run()
