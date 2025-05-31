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

        # Step 1: Collect local constraints from number cells
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.game.view_board[r][c]
                if not cell.isdigit() or int(cell) == 0:
                    continue

                neighbors = self.get_neighbors(r, c)
                unknown = set(
                    (nr, nc)
                    for (nr, nc) in neighbors
                    if self.game.view_board[nr][nc] == ' ' and (nr, nc) not in self.known_flags
                )
                flagged = set(
                    (nr, nc)
                    for (nr, nc) in neighbors
                    if (nr, nc) in self.known_flags
                )

                remaining_mines = int(cell) - len(flagged)
                if remaining_mines < 0:
                    continue  # too many flags (user error), skip

                if not unknown:
                    continue

                # Basic rules
                if remaining_mines == 0:
                    safe_moves.update(unknown)
                elif remaining_mines == len(unknown):
                    new_flags.update(unknown)
                else:
                    constraints.append({
                        'source': (r, c),
                        'cells': unknown,
                        'count': remaining_mines
                    })

        # Step 2: Subset inference
        for i, c1 in enumerate(constraints):
            for j, c2 in enumerate(constraints):
                if i == j:
                    continue
                # If c1 is a subset of c2
                if c1['cells'].issubset(c2['cells']):
                    diff = c2['cells'] - c1['cells']
                    diff_count = c2['count'] - c1['count']
                    if diff_count == 0:
                        safe_moves.update(diff)
                    elif diff_count == len(diff):
                        new_flags.update(diff)

        # Step 3: Disjoint pair inference
        for i, c1 in enumerate(constraints):
            for j, c2 in enumerate(constraints):
                if i == j:
                    continue
                if c1['cells'].isdisjoint(c2['cells']):
                    combined_cells = c1['cells'] | c2['cells']
                    combined_count = c1['count'] + c2['count']
                    for k, c3 in enumerate(constraints):
                        if k == i or k == j:
                            continue
                        if c3['cells'] >= combined_cells and c3['count'] == combined_count:
                            leftover = c3['cells'] - combined_cells
                            if leftover:
                                safe_moves.update(leftover)

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
        print("Moves: ", safe_moves)
        print("Flags: ", list(to_flag))
        for pos in to_flag:
            self.known_flags.add(pos)
        return safe_moves, list(to_flag)