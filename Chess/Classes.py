#
# Classes needed for chess game.
#
from enum import Enum

# maps key : val
rankToRow = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
rowToRank = {v: k for k, v in rankToRow.items()}
fileToColumn = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
columnToFile = {v: k for k, v in fileToColumn.items()}


#
# @param (row, column)
# @returns rank + file as string
#
def get_rank_file(row, column):
    return columnToFile[column] + rowToRank[row]


class Color(Enum):
    White = 0
    Black = 1


class Player:
    def __init__(self, color):
        self.color = color
        self.piece_list = []
        self.material = 0
        self.is_in_check = False
        self.has_castled = False
        self.can_castle = False


class Piece:
    def __init__(self, color):
        self.has_moved = False
        self.color = color
        if self.color == Color.White:
            self.nameAbv = "w"
        else:
            self.nameAbv = "b"


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.materialValue = 1
        self.nameAbv = self.nameAbv + "p"


class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.materialValue = 0
        self.nameAbv = self.nameAbv + "K"


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.materialValue = 9
        self.nameAbv = self.nameAbv + "Q"


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.materialValue = 5
        self.nameAbv = self.nameAbv + "R"


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.materialValue = 3
        self.nameAbv = self.nameAbv + "B"


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.materialValue = 3
        self.nameAbv = self.nameAbv + "N"


class Square:
    def __init__(self, row, column, color, piece):
        self.row = row
        self.column = column
        self.color = color
        self.piece = piece


class Move:
    def __init__(self, start_coords, end_coords, board):
        self.startRow = start_coords[0]
        self.startColumn = start_coords[1]
        self.endRow = end_coords[0]
        self.endColumn = end_coords[1]
        self.pieceMoved = board.grid[self.startRow][self.startColumn].piece
        self.pieceCaptured = board.grid[self.endRow][self.endColumn].piece

    def get_chess_notation(self):
        return get_rank_file(self.startRow, self.startColumn) + get_rank_file(self.endRow, self.endColumn)

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.startColumn == other.startColumn \
                   and self.startRow == other.startRow \
                   and self.endColumn == other.endColumn \
                   and self.endRow == other.endRow
        else:
            return False


class Castle(Move):
    def __init__(self, start_coords, end_coords, board, rook_start_square, rook_end_square):
        super().__init__(start_coords, end_coords, board)
        self.rook = board.grid[rook_start_square[0]][rook_start_square[1]].piece
        self.rook_move = Move(rook_start_square, rook_end_square, board)


class EnPassant(Move):
    def __init__(self, start_coords, end_coords, board):
        super().__init__(start_coords, end_coords, board)
        self.pieceCaptured = board.grid[self.endRow +1][self.endColumn]


class Board:
    def __init__(self):
        self.grid = [[Square(0, 0, None, None) for _ in range(0, 8)] for _ in range(0, 8)]
        temp_color = Color.Black  # Used for populating grid with pieces.

        for row in range(0, 8):
            if row > 2:
                temp_color = Color.White
            for column in range(0, 8):
                temp_square = Square(row, column, Color((row + column) % 2), None)
                temp_piece = None
                self.grid[row][column] = temp_square
                match row:
                    case 0 | 7:
                        match column:
                            case 0 | 7:
                                temp_piece = Rook(temp_color)
                            case 1 | 6:
                                temp_piece = Knight(temp_color)
                            case 2 | 5:
                                temp_piece = Bishop(temp_color)
                            case 3:
                                temp_piece = Queen(temp_color)
                            case 4:
                                temp_piece = King(temp_color)
                    case 1 | 6:
                        temp_piece = Pawn(temp_color)

                self.grid[row][column].piece = temp_piece


def can_promote_pawn(move):
    match move.pieceMoved:
        case Pawn():
            if move.endRow == 0 or move.endRow == 7:
                return True
    return False


class GameState:
    # Create game state, grid, players
    def __init__(self):
        self.player_white = Player(Color.White)
        self.player_black = Player(Color.Black)
        self.moveLog = []
        self.board = Board()
        self.player_moving = self.player_white
        self.player_waiting = self.player_black
        for row in range(8):
            for column in range(8):
                match row:
                    case 0 | 1 | 6 | 7:
                        match self.board.grid[row][column].piece.color.name:
                            case Color.White:
                                self.player_white.piece_list.append(self.board.grid[row][column].piece)
                                break
                            case Color.Black:
                                self.player_black.piece_list.append(self.board.grid[row][column].piece)
                                break

    def toggle_turn(self):
        temp_player = self.player_moving
        self.player_moving = self.player_waiting
        self.player_waiting = temp_player

    def make_move(self, move):
        match move:
            case Castle():
                self.make_move(move.rook_move)
        self.board.grid[move.endRow][move.endColumn].piece = move.pieceMoved
        self.board.grid[move.startRow][move.startColumn].piece = None
        self.moveLog.append(move)

    def undo_move(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board.grid[move.startRow][move.startColumn].piece = move.pieceMoved
            self.board.grid[move.endRow][move.endColumn].piece = move.pieceCaptured
            match move:
                case Castle():
                    self.board.grid[move.rook_move.startRow][move.rook_move.startColumn].piece = move.rook
                    self.board.grid[move.rook_move.endRow][
                        move.rook_move.endColumn].piece = move.rook_move.pieceCaptured
                    move.rook.has_moved = False
                    if move.pieceMoved:
                        move.pieceMoved.has_moved = False

    def is_in_check(self, player, opponent):
        valid_moves = self.get_possible_moves(opponent)
        for move in valid_moves:
            if move.pieceCaptured:
                match move.pieceCaptured:
                    case King():
                        player.is_in_check = True
                        return True
        player.is_in_check = False

    def can_castle(self, opponent, move):
        opponent_moves = self.get_possible_moves(opponent)
        kq_side = [[4, 5, 6], [4, 3, 2]]
        if move.endColumn == 6:
            side = kq_side[0]
        else:
            side = kq_side[1]

        for opponent_move in opponent_moves:
            if opponent_move.endRow == move.endRow and (opponent_move.endColumn in side):
                return False
        return True

    def promote_pawn(self, player, move, is_ai):
        new_piece = None
        user_selection = ' '
        if is_ai:
            user_selection = 'q'
        while new_piece is None:
            match user_selection:
                case 'q':
                    new_piece = Queen(self.player_moving.color)
                case 'r':
                    new_piece = Rook(self.player_moving.color)
                case 'b':
                    new_piece = Bishop(self.player_moving.color)
                case 'n':
                    new_piece = Knight(self.player_moving.color)
                case _:
                    user_selection = input("What would you like to promote to? (q, r, b, n) ")
        self.board.grid[move.endRow][move.endColumn].piece = new_piece
        player.piece_list.append(new_piece)

    def get_valid_moves(self, player, opponent):
        possible_moves = self.get_possible_moves(player)
        invalid_moves = []
        for move in possible_moves:
            self.make_move(move)
            match move:
                case Castle():
                    if not self.can_castle(opponent, move):
                        invalid_moves.append(move)
                case Move():
                    if self.is_in_check(player, opponent):
                        invalid_moves.append(move)
            self.undo_move()
        for move in invalid_moves:
            possible_moves.remove(move)
        return possible_moves
        # valid_moves = []
        # possible_moves = self.get_possible_moves(player)
        # for move in possible_moves:

    def get_possible_moves(self, player):
        moves = []
        for row in range(8):
            for column in range(8):
                square = self.board.grid[row][column]
                if square.piece:
                    if (square.piece.color == Color.White and player == self.player_white) or \
                            (square.piece.color == Color.Black and player == self.player_black):
                        match square.piece:
                            case King():
                                self.get_king_moves(row, column, moves, player, square)
                            case Queen():
                                self.get_queen_moves(row, column, moves)
                            case Rook():
                                self.get_rook_moves(row, column, moves)
                            case Bishop():
                                self.get_bishop_moves(row, column, moves)
                            case Knight():
                                self.get_knight_moves(row, column, moves)
                            case Pawn():
                                self.get_pawn_moves(row, column, moves)
        return moves

    def get_king_moves(self, r, c, moves, player, square):
        self.move_up(r, c, 1, moves)
        self.move_down(r, c, 1, moves)
        self.move_left(r, c, 1, moves)
        self.move_right(r, c, 1, moves)
        self.move_down_left(r, c, 1, moves)
        self.move_down_right(r, c, 1, moves)
        self.move_up_left(r, c, 1, moves)
        self.move_up_right(r, c, 1, moves)

        # Handles castling
        if not square.piece.has_moved and c == 4 and (r == 0 or r == 4):
            seven_zero = [7, 0]
            player_back_row = seven_zero[player.color.value]
            king_post_castle_col = [6, 2]
            rook_post_castle_col = [5, 3]
            castle_ranges = [[5, 7],  # King's side
                             [1, 4]]  # Queen's side
            for qk_side in range(2):
                rook_col = seven_zero[qk_side]
                temp_rook = self.board.grid[player_back_row][rook_col].piece
                if temp_rook:
                    can_castle = True
                    if not temp_rook.has_moved:
                        # Check space between K&R is empty
                        for x in range(castle_ranges[qk_side][0], castle_ranges[qk_side][1]):
                            if self.board.grid[player_back_row][x].piece:
                                can_castle = False
                        if can_castle:
                            moves.append(Castle((player_back_row, 4),
                                                (player_back_row, king_post_castle_col[qk_side]),
                                                self.board,
                                                (player_back_row, rook_col),
                                                (player_back_row, rook_post_castle_col[qk_side])))

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_rook_moves(self, r, c, moves):
        for distance in range(1, r + 1):
            self.move_up(r, c, distance, moves)
            if self.board.grid[r - distance][c].piece:
                break

        for distance in range(1, 8 - r):
            self.move_down(r, c, distance, moves)
            if self.board.grid[r + distance][c].piece:
                break

        for distance in range(1, c + 1):
            self.move_left(r, c, distance, moves)
            if self.board.grid[r][c - distance].piece:
                break

        for distance in range(1, 8 - c):
            self.move_right(r, c, distance, moves)
            if self.board.grid[r][c + distance].piece:
                break

    def get_bishop_moves(self, r, c, moves):
        for distance in range(1, 8):  # up and left
            if r - distance < 0 or c - distance < 0:
                break
            else:
                self.move_up_left(r, c, distance, moves)
                if self.board.grid[r - distance][c - distance].piece:
                    break

        for distance in range(1, 8):  # up and right
            if r - distance < 0 or c + distance > 7:
                break
            else:
                self.move_up_right(r, c, distance, moves)
                if self.board.grid[r - distance][c + distance].piece:
                    break

        for distance in range(1, 8):  # down and right
            if r + distance > 7 or c + distance > 7:
                break
            else:
                self.move_down_right(r, c, distance, moves)
                if self.board.grid[r + distance][c + distance].piece:
                    break

        for distance in range(1, 8):  # down and left
            if r + distance > 7 or c - distance < 0:
                break
            else:
                self.move_down_left(r, c, distance, moves)
                if self.board.grid[r + distance][c - distance].piece:
                    break

    def get_knight_moves(self, r, c, moves):
        values1 = [1, -1]
        values2 = [2, -2]
        for val2 in values2:
            if r + val2 in range(8):
                for val1 in values1:
                    if c + val1 in range(8):
                        if self.board.grid[r + val2][c + val1].piece is None:
                            moves.append(Move((r, c), (r + val2, c + val1), self.board))
                        elif self.board.grid[r + val2][c + val1].piece.color != self.board.grid[r][c].piece.color:
                            moves.append(Move((r, c), (r + val2, c + val1), self.board))

        for val1 in values1:
            if r + val1 in range(8):
                for val2 in values2:
                    if c + val2 in range(8):
                        if self.board.grid[r + val1][c + val2].piece is None:
                            moves.append(Move((r, c), (r + val1, c + val2), self.board))
                        elif self.board.grid[r + val1][c + val2].piece.color != self.board.grid[r][c].piece.color:
                            moves.append(Move((r, c), (r + val1, c + val2), self.board))

    def get_pawn_moves(self, r, c, moves):
        if self.board.grid[r][c].piece.color == Color.White:
            if self.board.grid[r - 1][c].piece is None:  # Up 1
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board.grid[r - 2][c].piece is None:  # Up 2
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # Capture Left
                if self.board.grid[r - 1][c - 1].piece and self.board.grid[r - 1][c - 1].piece.color == Color.Black:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c + 1 <= 7:  # Capture Right
                if self.board.grid[r - 1][c + 1].piece and self.board.grid[r - 1][c + 1].piece.color == Color.Black:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))

        if self.board.grid[r][c].piece.color == Color.Black:
            if self.board.grid[r + 1][c].piece is None:  # Down 1
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board.grid[r + 2][c].piece is None:  # Down 2
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # Capture Down Right
                if self.board.grid[r + 1][c - 1].piece and self.board.grid[r + 1][c - 1].piece.color == Color.White:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= 7:  # Capture Down Left
                if self.board.grid[r + 1][c + 1].piece and self.board.grid[r + 1][c + 1].piece.color == Color.White:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

    '''
        if r == 3:

            match c:
                case 0:
                    if self.board.grid[2][1].piece:
                        if self.board.grid[2][1].piece.isinstance(Pawn):

                case 1|2|3|4|5|6:
                    pass
                case 7:
                    pass

    '''

    def move_up_left(self, r, c, distance, moves):
        if r - distance >= 0 and c - distance >= 0:
            if self.board.grid[r - distance][c - distance].piece is None:
                moves.append(Move((r, c), (r - distance, c - distance), self.board))
            elif self.board.grid[r - distance][c - distance].piece.color != self.board.grid[r][c].piece.color:
                moves.append(Move((r, c), (r - distance, c - distance), self.board))

    def move_up_right(self, r, c, distance, moves):
        if r - distance >= 0 and c + distance <= 7:
            if self.board.grid[r - distance][c + distance].piece is None:
                moves.append(Move((r, c), (r - distance, c + distance), self.board))
            elif self.board.grid[r - distance][c + distance].piece.color != self.board.grid[r][c].piece.color:
                moves.append(Move((r, c), (r - distance, c + distance), self.board))

    def move_down_right(self, r, c, distance, moves):
        if r + distance <= 7 and c + distance <= 7:
            if self.board.grid[r + distance][c + distance].piece is None:
                moves.append(Move((r, c), (r + distance, c + distance), self.board))
            elif self.board.grid[r + distance][c + distance].piece.color != self.board.grid[r][c].piece.color:
                moves.append(Move((r, c), (r + distance, c + distance), self.board))

    def move_down_left(self, r, c, distance, moves):
        if r + distance <= 7 and c - distance >= 0:
            if self.board.grid[r + distance][c - distance].piece is None:
                moves.append(Move((r, c), (r + distance, c - distance), self.board))
            elif self.board.grid[r + distance][c - distance].piece.color != self.board.grid[r][c].piece.color:
                moves.append(Move((r, c), (r + distance, c - distance), self.board))

    def move_up(self, r, c, distance, moves):
        if r - distance >= 0:
            if self.board.grid[r - distance][c].piece is None:
                moves.append(Move((r, c), (r - distance, c), self.board))
            elif self.board.grid[r - distance][c].piece.color != self.board.grid[r][c].piece.color:
                moves.append(Move((r, c), (r - distance, c), self.board))

    def move_down(self, r, c, distance, moves):
        if r + distance <= 7:
            if self.board.grid[r + distance][c].piece is None:
                moves.append(Move((r, c), (r + distance, c), self.board))
            elif self.board.grid[r + distance][c].piece.color != self.board.grid[r][c].piece.color:
                moves.append(Move((r, c), (r + distance, c), self.board))

    def move_left(self, r, c, distance, moves):
        if c - distance >= 0:
            if self.board.grid[r][c - distance].piece is None:
                moves.append(Move((r, c), (r, c - distance), self.board))
            elif self.board.grid[r][c - distance].piece.color != self.board.grid[r][c].piece.color:
                moves.append(Move((r, c), (r, c - distance), self.board))

    def move_right(self, r, c, distance, moves):
        if c + distance <= 7:
            if self.board.grid[r][c + distance].piece is None:
                moves.append(Move((r, c), (r, c + distance), self.board))
            elif self.board.grid[r][c + distance].piece.color != self.board.grid[r][c].piece.color:
                moves.append(Move((r, c), (r, c + distance), self.board))
