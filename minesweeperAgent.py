class MinesweeperSolver:
    def __init__(self, game):
        self.game = game
        self.rows = game.rows
        self.cols = game.cols
        self.known_flags = set()  # Internal tracking of flagged cells

    def get_neighbors(self, r, c):
        return [
            (r + dr, c + dc)
            for dr in [-1, 0, 1]
            for dc in [-1, 0, 1]
            if (dr != 0 or dc != 0) and 0 <= r + dr < self.rows and 0 <= c + dc < self.cols
        ]

    def analyze_board(self):
        safe_moves = set()
        new_flags = set()
        constraints = []

        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.game.view_board[r][c]
                if not cell.isdigit() or int(cell) == 0:
                    continue

                number = int(cell)
                neighbors = self.get_neighbors(r, c)
                flagged = [n for n in neighbors if n in self.known_flags]
                unknown = [
                    n for n in neighbors
                    if self.game.view_board[n[0]][n[1]] == ' ' and n not in self.known_flags
                ]

                remaining_mines = number - len(flagged)
                if remaining_mines == 0:
                    safe_moves.update(unknown)
                elif remaining_mines == len(unknown):
                    new_flags.update(unknown)
                elif unknown:
                    constraints.append((set(unknown), remaining_mines))

        # Subset-based inference
        for i in range(len(constraints)):
            cells_i, count_i = constraints[i]
            for j in range(len(constraints)):
                if i == j:
                    continue
                cells_j, count_j = constraints[j]

                # Check if i is a subset of j
                if cells_i < cells_j:
                    diff_cells = cells_j - cells_i
                    diff_count = count_j - count_i
                    if diff_count == 0:
                        safe_moves.update(diff_cells)
                    elif diff_count == len(diff_cells):
                        new_flags.update(diff_cells)

                # Or j is a subset of i
                elif cells_j < cells_i:
                    diff_cells = cells_i - cells_j
                    diff_count = count_i - count_j
                    if diff_count == 0:
                        safe_moves.update(diff_cells)
                    elif diff_count == len(diff_cells):
                        new_flags.update(diff_cells)

        return list(safe_moves), new_flags

    def find_safe_moves(self):
        safe, to_flag = self.analyze_board()

        # Update internal flag knowledge
        for pos in to_flag:
            self.known_flags.add(pos)

        return safe

    def make_moves(self):
        """Returns a tuple: (list of safe moves to click, list of flags to place)"""
        safe_moves, to_flag = self.analyze_board()
        #print("Moves: ", safe_moves)
        #print("Flags: ", list(to_flag))
        for pos in to_flag:
            self.known_flags.add(pos)
        return safe_moves, list(to_flag)