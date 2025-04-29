class Piece:
    def __init__(self, color):
        self.color = color

    def get_possible_moves(self, board, position):
        raise NotImplementedError

    def __str__(self):
        return self.symbol


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '♙' if color == 'black' else '♟'

    def get_possible_moves(self, board, position):
        moves = []
        r, c = position
        direction = -1 if self.color == 'white' else 1
        start_row = 6 if self.color == 'white' else 1

        if board.is_empty((r + direction, c)):
            moves.append((r + direction, c))
            if r == start_row and board.is_empty((r + 2 * direction, c)):
                moves.append((r + 2 * direction, c))

        for dc in [-1, 1]:
            nr, nc = r + direction, c + dc
            if board.is_enemy((nr, nc), self.color):
                moves.append((nr, nc))
        return moves


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '♖' if color == 'black' else '♜'

    def get_possible_moves(self, board, position):
        return board.get_straight_moves(position, self.color)


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '♘' if color == 'black' else '♞'

    def get_possible_moves(self, board, position):
        moves = []
        r, c = position
        directions = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                      (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if board.is_within_bounds((nr, nc)) and not board.is_friendly((nr, nc), self.color):
                moves.append((nr, nc))
        return moves


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '♗' if color == 'black' else '♝'

    def get_possible_moves(self, board, position):
        return board.get_diagonal_moves(position, self.color)


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '♕' if color == 'black' else '♛'

    def get_possible_moves(self, board, position):
        return board.get_straight_moves(position, self.color) + board.get_diagonal_moves(position, self.color)


class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.symbol = '♔' if color == 'black' else '♚'

    def get_possible_moves(self, board, position):
        moves = []
        r, c = position
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if board.is_within_bounds((nr, nc)) and not board.is_friendly((nr, nc), self.color):
                    moves.append((nr, nc))
        return moves


class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_pieces()

    def setup_pieces(self):
        layout = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col in range(8):
            self.board[1][col] = Pawn('black')
            self.board[6][col] = Pawn('white')
            self.board[0][col] = layout[col]('black')
            self.board[7][col] = layout[col]('white')

    def display(self):
        print("    a  b  c  d  e  f  g  h")
        print("  --------------------------")
        for r in range(8):
            print(8 - r, "|", end=" ")
            for c in range(8):
                piece = self.board[r][c]
                print(piece.symbol if piece else ".", end="  ")
            print("|", 8 - r)
        print("  --------------------------")
        print("    a  b  c  d  e  f  g  h")

    def is_within_bounds(self, pos):
        r, c = pos
        return 0 <= r < 8 and 0 <= c < 8

    def is_empty(self, pos):
        r, c = pos
        return self.is_within_bounds(pos) and self.board[r][c] is None

    def is_friendly(self, pos, color):
        r, c = pos
        return self.is_within_bounds(pos) and self.board[r][c] and self.board[r][c].color == color

    def is_enemy(self, pos, color):
        r, c = pos
        return self.is_within_bounds(pos) and self.board[r][c] and self.board[r][c].color != color

    def get_straight_moves(self, pos, color):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return self._get_moves(pos, directions, color)

    def get_diagonal_moves(self, pos, color):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self._get_moves(pos, directions, color)

    def _get_moves(self, pos, directions, color):
        r, c = pos
        moves = []
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while self.is_within_bounds((nr, nc)):
                if self.is_empty((nr, nc)):
                    moves.append((nr, nc))
                elif self.is_enemy((nr, nc), color):
                    moves.append((nr, nc))
                    break
                else:
                    break
                nr += dr
                nc += dc
        return moves


class Game:
    def __init__(self):
        self.board = Board()
        self.current_turn = 'white'

    def parse_move(self, move_str):
        files = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        try:
            start, end = move_str.split()
            r1, c1 = 8 - int(start[1]), files[start[0]]
            r2, c2 = 8 - int(end[1]), files[end[0]]
            return (r1, c1), (r2, c2)
        except (KeyError, IndexError, ValueError):
            return None, None

    def play(self):
        while True:
            self.board.display()
            move = input(f"{self.current_turn}'s move (e.g., 'e2 e4'): ").strip()
            start, end = self.parse_move(move)

            if not start or not end:
                print("Invalid input format. Try again.")
                continue

            piece = self.board.board[start[0]][start[1]]
            if not piece or piece.color != self.current_turn:
                print("Invalid piece selection. Try again.")
                continue

            if end not in piece.get_possible_moves(self.board, start):
                print("Illegal move. Try again.")
                continue

            self.board.board[end[0]][end[1]] = piece
            self.board.board[start[0]][start[1]] = None
            self.current_turn = 'black' if self.current_turn == 'white' else 'white'


if __name__ == "__main__":
    Game().play()
