import tkinter as tk
from tkinter import font
import random
from minesweeperAgent import MinesweeperSolver

action_delay = 100

class Game:
    def __init__(self, rows=8, cols=8, num_mines=10):
        self.rows = rows
        self.cols = cols
        self.num_mines = num_mines
        
        self.game_board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.view_board = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.mines_placed = False

    def place_mines(self, safe_r, safe_c):
        def is_in_safe_zone(r, c):
            return abs(r - safe_r) <= 1 and abs(c - safe_c) <= 1

        mines_placed = 0
        while mines_placed < self.num_mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            if self.game_board[r][c] != 'M' and not is_in_safe_zone(r, c):
                self.game_board[r][c] = 'M'
                mines_placed += 1

        self._calculate_adjacent_counts()
        self.mines_placed = True

    def _calculate_adjacent_counts(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.game_board[r][c] == 'M':
                    continue
                count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if self.game_board[nr][nc] == 'M':
                                count += 1
                self.game_board[r][c] = count

    def reveal_tile(self, r, c, revealed=None):
        if revealed is None:
            revealed = set()

        if (r, c) in revealed or self.view_board[r][c] != ' ':
            return

        revealed.add((r, c))
        val = self.game_board[r][c]
        self.view_board[r][c] = str(val)

        if val == 0:
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        self.reveal_tile(nr, nc, revealed)

    def click_tile(self, r, c):
        """Commit to clicking this tile:
        - If it's a mine, return 'M'
        - If it's a number, reveal it and return the value ('0'–'8')
        """
        if not self.mines_placed:
            self.place_mines(safe_r=r, safe_c=c)

        if self.view_board[r][c] != ' ':
            return self.view_board[r][c]  # Already revealed

        if self.game_board[r][c] == 'M':
            return 'M'

        self.reveal_tile(r, c)
        return self.view_board[r][c]
    
    def get_view(self, r, c):
        return self.view_board[r][c]
    
    def is_win(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.view_board[r][c] == ' ' and self.game_board[r][c] != 'M':
                    return False
        return True


# --- GUI setup ---

class MinesweeperGUI:
    def __init__(self, master):
        self.master = master

        # Create the menu bar
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)

        # Create "Game" menu
        game_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Game", menu=game_menu)

        # Add difficulty options
        game_menu.add_command(label="Beginner", command=lambda: self.set_difficulty(9, 9, 10))
        game_menu.add_command(label="Intermediate", command=lambda: self.set_difficulty(16, 16, 40))
        game_menu.add_command(label="Expert", command=lambda: self.set_difficulty(16, 30, 99))

        # Create "Solver" menu
        solver_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Solver", menu=solver_menu)

        solver_menu.add_command(label="Start Solver", command=self.run_solver)

        self.master.title("Minesweeper")
        self.rows = 8
        self.cols = 8
        self.mines = 10
        self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.game = Game(self.rows, self.cols, num_mines=10)
        self.game_over = False

        self.tile_font = font.Font(family="Courier", size=12, weight="bold")
        self.number_colors = {
        '1': '#0000FF',   # Blue
        '2': '#008000',   # Green
        '3': '#FF0000',   # Red
        '4': '#000080',   # Navy
        '5': '#800000',   # Maroon
        '6': '#008080',   # Teal
        '7': '#000000',   # Black
        '8': '#808080',   # Gray
        }

        # Main vertical container
        self.container = tk.Frame(self.master)
        self.container.pack()

        # Header at the top
        self.header = tk.Frame(self.container, bg='black')
        self.header.pack(fill='x')

        # Configure the grid to stretch equally left and right
        self.header.grid_columnconfigure(0, weight=1)
        self.header.grid_columnconfigure(1, weight=0)
        self.header.grid_columnconfigure(2, weight=1)

        # Column 0: Mine counter (left)
        self.mine_counter = tk.Label(
            self.header,
            text=str(self.game.num_mines),
            bg='black',
            fg='red',
            font=('Courier', 20, 'bold'),
            width=5
        )
        self.mine_counter.grid(row=0, column=0, sticky='w', padx=(15, 0), pady=5)

        # Column 1: Reset button (centered)
        self.reset_button = tk.Button(
            self.header,
            text='😐',
            font=('Courier', 20),
            width=2,
            command=self.reset_game,
            relief='raised'
        )
        self.reset_button.grid(row=0, column=1)

        # Column 2: Timer (right)
        self.timer_label = tk.Label(
            self.header,
            text='000',
            bg='black',
            fg='red',
            font=('Courier', 20, 'bold'),
            width=5
        )
        self.timer_label.grid(row=0, column=2, sticky='e', padx=(0, 15))


        self.flags = set()
        self.remaining_mines = self.game.num_mines
        self.time_elapsed = 0
        self.update_timer()
        self.create_board()

    def create_board(self):
        self.board_frame = tk.Frame(self.container)  # Game board under header
        self.board_frame.pack()

        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(
                    self.board_frame,
                    width=4, height=2,
                    bg='lightgray',
                    font=self.tile_font,
                    relief='raised',
                    bd=2,
                    padx=0,
                    pady=0,
                    anchor='center'
                )
                btn.grid(row=r, column=c, padx=1, pady=1)
                btn.config(command=lambda r=r, c=c: self.on_click(r, c))
                btn.bind("<Button-3>", lambda e, r=r, c=c: self.on_right_click(r, c))
                self.buttons[r][c] = btn

    def on_click(self, r, c):
        if self.game_over or (r, c) in self.flags:
            return

        result = self.game.click_tile(r, c)

        if result == 'M':
            self.end_game()
            return

        # Update the board view based on updated view_board
        for i in range(self.rows):
            for j in range(self.cols):
                val = self.game.get_view(i, j)
                if val != ' ':
                    color = self.number_colors.get(val, 'black')
                    self.buttons[i][j].config(
                        text=val if val != '0' and val != 'M' else '',
                        bg='#B0B0B0',
                        relief='sunken',
                        fg=color,
                        font=self.tile_font
                    )

        if self.game.is_win():
            self.game_over = True
            self.master.after_cancel(self.timer_job)
            self.reset_button.config(text='😎')

    def on_right_click(self, r, c):
        btn = self.buttons[r][c]

        if (r, c) in self.flags:
            self.flags.remove((r, c))
            self.remaining_mines += 1
            btn.config(text='', fg='black', bg='lightgray')
        else:
            if self.game.view_board[r][c] == ' ':
                self.flags.add((r, c))
                self.remaining_mines -= 1
                btn.config(text='🚩', fg='red', bg='lightgray')

        self.update_mine_counter()

    def update_timer(self):
        if self.game_over:
            return
        self.timer_label.config(text=f"{self.time_elapsed:03}")
        self.time_elapsed += 1
        self.timer_job = self.master.after(1000, self.update_timer)

    def reset_game(self):
        # 1. Reset game logic
        self.game = Game(self.rows, self.cols, self.mines)

        # 2. Reset flag tracking
        self.flags = set()
        self.remaining_mines = self.game.num_mines
        self.update_mine_counter()

        # 3. Reset timer
        self.time_elapsed = 0
        self.timer_label.config(text='000')

        # 4. Reset face
        self.reset_button.config(text='😐')

        # 5. Reset buttons
        for r in range(self.rows):
            for c in range(self.cols):
                btn = self.buttons[r][c]
                btn.config(
                    text='',
                    bg='lightgray',
                    fg='black',
                    relief='raised',
                    state='normal'
                )

        self.game_over = False
        self.update_timer()
        self.reset_button.config(text='😐')

    def update_mine_counter(self):
        self.mine_counter.config(text=f"{self.remaining_mines:03}")

    def end_game(self):
        self.game_over = True

        # Stop timer
        self.master.after_cancel(self.timer_job)

        # Show all mines
        for r in range(self.rows):
            for c in range(self.cols):
                if self.game.game_board[r][c] == 'M':
                    self.buttons[r][c].config(text='M', bg='red', fg='black', relief='sunken')

        # Change face
        self.reset_button.config(text='😵')

        # Disable all buttons (clicks will be ignored via self.game_over)

    def set_difficulty(self, rows, cols, mines):
        # Clear old board
        self.board_frame.destroy()

        # Update size and recreate
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.game = Game(rows, cols, num_mines=mines)
        self.buttons = [[None for _ in range(cols)] for _ in range(rows)]

        self.flags = set()
        self.remaining_mines = mines
        self.time_elapsed = 0
        self.game_over = False

        self.mine_counter.config(text=f"{self.remaining_mines:03}")
        self.timer_label.config(text='000')
        self.reset_button.config(text='😐')

        self.create_board()
        self.update_timer()

    def run_solver(self):
        if self.game_over:
            return

        self.solver = MinesweeperSolver(self.game)
        no_progress_counter = [0]
        action_queue = []

        def queue_actions(safe_moves, flags):
            # Queue flag placements
            for r, c in flags:
                if (r, c) not in self.flags:
                    action_queue.append(("flag", r, c))

            # Queue safe moves
            for r, c in safe_moves:
                if self.game.view_board[r][c] == ' ' and (r, c) not in self.flags:
                    action_queue.append(("click", r, c))

        def perform_next_action():
            if self.game_over or self.game.is_win():
                return

            if not action_queue:
                safe_moves, flags = self.solver.make_moves()
                if not safe_moves and not flags:
                    no_progress_counter[0] += 1
                else:
                    no_progress_counter[0] = 0

                if no_progress_counter[0] < 2:
                    queue_actions(safe_moves, flags)
                    self.master.after(100, perform_next_action)
                else:
                    print("Solver stuck — no new moves.")
                return

            action, r, c = action_queue.pop(0)

            if action == "flag":
                self.flags.add((r, c))
                self.remaining_mines -= 1
                self.buttons[r][c].config(text='🚩', fg='red', bg='lightgray')
                self.update_mine_counter()
            elif action == "click":
                self.buttons[r][c].config(bg='yellow')
                self.master.after(200, lambda r=r, c=c: self.on_click(r, c))

            self.master.after(action_delay, perform_next_action)  # Half-second delay after each action

         # Make the first click if nothing has been revealed
        revealed = any(
            self.game.view_board[r][c] != ' '
            for r in range(self.rows)
            for c in range(self.cols)
        )
        if not revealed:
            start_r, start_c = self.rows // 2, self.cols // 2
            self.on_click(start_r, start_c)
            self.master.after(500, perform_next_action)
        else:
            perform_next_action()

# --- Run the app ---
if __name__ == "__main__":
    root = tk.Tk()
    app = MinesweeperGUI(root)
    root.mainloop()