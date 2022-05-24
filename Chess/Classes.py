#
#
from enum import Enum

# maps key : val
rankToRow = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
rowToRank = {v: k for k, v in rankToRow.items()}
fileToColumn = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
columnToFile = {v: k for k, v in fileToColumn.items()}


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


class Piece:
    def __init__(self, square, color):
        self.color = color
        self.square = square
        if self.color == Color.White:
            self.nameAbv = "w"
        else:
            self.nameAbv = "b"


class Pawn(Piece):
    def __init__(self, square, color):
        super().__init__(square, color)
        self.materialValue = 1
        self.nameAbv = self.nameAbv + "p"


class King(Piece):
    def __init__(self, square, color):
        super().__init__(square, color)
        self.materialValue = 0
        self.nameAbv = self.nameAbv + "K"


class Queen(Piece):
    def __init__(self, square, color):
        super().__init__(square, color)
        self.materialValue = 9
        self.nameAbv = self.nameAbv + "Q"


class Rook(Piece):
    def __init__(self, square, color):
        super().__init__(square, color)
        self.materialValue = 5
        self.nameAbv = self.nameAbv + "R"


class Bishop(Piece):
    def __init__(self, square, color):
        super().__init__(square, color)
        self.materialValue = 3
        self.nameAbv = self.nameAbv + "B"


class Knight(Piece):
    def __init__(self, square, color):
        super().__init__(square, color)
        self.materialValue = 3
        self.nameAbv = self.nameAbv + "N"


class Square:
    def __init__(self, row, column, color, piece):
        self.row = row
        self.column = column
        self.color = color
        self.piece = piece


class Move:
    def __init__(self, start_square, end_square, board):
        self.startRow = start_square[0]
        self.startColumn = start_square[1]
        self.endRow = end_square[0]
        self.endColumn = end_square[1]
        self.pieceMoved = board[self.startRow][self.startColumn].piece
        self.pieceCaptured = board[self.endRow][self.endColumn].piece

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


class GameState:
    def __init__(self):
        # Create game state
        self.board = [[Square(0, 0, None, None) for _ in range(0, 8)] for _ in range(0, 8)]
        player1_white = Player(Color.White)
        player2_black = Player(Color.Black)
        temp_color = Color.Black

        for column in range(0, 8):
            if column > 2:
                temp_color = Color.White
            for row in range(0, 8):
                temp_square = Square(column, row, Color((column + row) % 2), None)
                temp_piece = None
                self.board[column][row] = temp_square
                match column:
                    case 0 | 7:
                        match row:
                            case 0 | 7:
                                temp_piece = Rook(temp_square, temp_color)
                            case 1 | 6:
                                temp_piece = Knight(temp_square, temp_color)
                            case 2 | 5:
                                temp_piece = Bishop(temp_square, temp_color)
                            case 3:
                                temp_piece = Queen(temp_square, temp_color)
                            case 4:
                                temp_piece = King(temp_square, temp_color)
                    case 1 | 6:
                        temp_piece = Pawn(temp_square, temp_color)

                if temp_piece:
                    self.board[column][row].piece = temp_piece
                    if temp_color == Color.Black:
                        player2_black.piece_list.append(temp_piece)
                    else:
                        player1_white.piece_list.append(temp_piece)

        self.currentTurn = Color.White
        self.moveLog = []

    def toggle_turn(self):
        self.currentTurn = Color(not self.currentTurn.value)

    def make_move(self, move):
        self.board[move.endRow][move.endColumn].piece = move.pieceMoved
        self.board[move.startRow][move.startColumn].piece = None
        self.moveLog.append(move)
        self.toggle_turn()

    def undo_move(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startColumn].piece = move.pieceMoved
            self.board[move.endRow][move.endColumn].piece = move.pieceCaptured
            self.toggle_turn()

    def is_in_check(self):
        pass

    def get_valid_moves(self):
        return self.get_possible_moves()

    def get_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                square = self.board[r][c]
                if square.piece:
                    if (square.piece.color == Color.White and self.currentTurn == Color.White) or \
                            (square.piece.color == Color.Black and self.currentTurn == Color.Black):
                        match square.piece:
                            case King():
                                self.get_king_moves(r, c, moves)
                            case Queen():
                                self.get_queen_moves(r, c, moves)
                            case Rook():
                                self.get_rook_moves(r, c, moves)
                            case Bishop():
                                self.get_bishop_moves(r, c, moves)
                            case Knight():
                                self.get_knight_moves(r, c, moves)
                            case Pawn():
                                self.get_pawn_moves(r, c, moves)
        return moves

    def get_king_moves(self, r, c, moves):
        self.move_up(r, c, 1, moves)
        self.move_down(r, c, 1, moves)
        self.move_left(r, c, 1, moves)
        self.move_right(r, c, 1, moves)

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_rook_moves(self, r, c, moves):
        for distance in range(1, r + 1):
            self.move_up(r, c, distance, moves)
            if self.board[r - distance][c].piece:
                break

        for distance in range(1, 8 - r):
            self.move_down(r, c, distance, moves)
            if self.board[r + distance][c].piece:
                break

        for distance in range(1, c + 1):
            self.move_left(r, c, distance, moves)
            if self.board[r][c - distance].piece:
                break

        for distance in range(1, 8 - c):
            self.move_right(r, c, distance, moves)
            if self.board[r][c + distance].piece:
                break

    def get_bishop_moves(self, r, c, moves):
        for distance in range(1, 8):  # up and left
            if r - distance < 0 or c - distance < 0:
                break
            else:
                self.move_up_left(r, c, distance, moves)
                if self.board[r - distance][c - distance].piece:
                    break

        for distance in range(1, 8):  # up and right
            if r - distance < 0 or c + distance > 7:
                break
            else:
                self.move_up_right(r, c, distance, moves)
                if self.board[r - distance][c + distance].piece:
                    break

        for distance in range(1, 8):  # down and right
            if r + distance > 7 or c + distance > 7:
                break
            else:
                self.move_down_right(r, c, distance, moves)
                if self.board[r + distance][c + distance].piece:
                    break

        for distance in range(1, 8):  # down and left
            if r + distance > 7 or c - distance < 0:
                break
            else:
                self.move_down_left(r, c, distance, moves)
                if self.board[r + distance][c - distance].piece:
                    break

    def get_knight_moves(self, r, c, moves):
        pass

    def get_pawn_moves(self, r, c, moves):
        if self.currentTurn == Color.White:
            if self.board[r - 1][c].piece is None:  # Up 1
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c].piece is None:  # Up 2
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # Capture Left
                if self.board[r - 1][c - 1].piece and self.board[r - 1][c - 1].piece.color == Color.Black:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c + 1 <= 7:  # Capture Right
                if self.board[r - 1][c + 1].piece and self.board[r - 1][c + 1].piece.color == Color.Black:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))

        if self.currentTurn == Color.Black:
            if self.board[r + 1][c].piece is None:  # Down 1
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c].piece is None:  # Down 2
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # Capture Down Right
                if self.board[r + 1][c - 1].piece and self.board[r + 1][c - 1].piece.color == Color.White:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= 7:  # Capture Down Left
                if self.board[r + 1][c + 1].piece and self.board[r + 1][c + 1].piece.color == Color.White:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

    '''
      Move diagonal board a given distance
      '''

    def move_up_left(self, r, c, distance, moves):
        if r - distance >= 0 and c - distance >= 0:
            if self.board[r - distance][c - distance].piece is None:
                moves.append(Move((r, c), (r - distance, c - distance), self.board))
            elif self.board[r - distance][c - distance].piece.color != self.board[r][c].piece.color:
                moves.append(Move((r, c), (r - distance, c - distance), self.board))

    def move_up_right(self, r, c, distance, moves):
        if r - distance >= 0 and c + distance <= 7:
            if self.board[r - distance][c + distance].piece is None:
                moves.append(Move((r, c), (r - distance, c + distance), self.board))
            elif self.board[r - distance][c + distance].piece.color != self.board[r][c].piece.color:
                moves.append(Move((r, c), (r - distance, c + distance), self.board))

    def move_down_right(self, r, c, distance, moves):
        if r + distance <= 7 and c + distance <= 7:
            if self.board[r + distance][c + distance].piece is None:
                moves.append(Move((r, c), (r + distance, c + distance), self.board))
            elif self.board[r + distance][c + distance].piece.color != self.board[r][c].piece.color:
                moves.append(Move((r, c), (r + distance, c + distance), self.board))

    def move_down_left(self, r, c, distance, moves):
        if r + distance <= 7 and c - distance >= 0:
            if self.board[r + distance][c - distance].piece is None:
                moves.append(Move((r, c), (r + distance, c - distance), self.board))
            elif self.board[r + distance][c - distance].piece.color != self.board[r][c].piece.color:
                moves.append(Move((r, c), (r + distance, c - distance), self.board))

    '''
    Move up board a given distance
    '''

    def move_up(self, r, c, distance, moves):
        if r - distance >= 0:
            if self.board[r - distance][c].piece is None:
                moves.append(Move((r, c), (r - distance, c), self.board))
            elif self.board[r - distance][c].piece.color != self.board[r][c].piece.color:
                moves.append(Move((r, c), (r - distance, c), self.board))

    '''
    Move down board a given distance
    '''

    def move_down(self, r, c, distance, moves):
        if r + distance <= 7:
            if self.board[r + distance][c].piece is None:
                moves.append(Move((r, c), (r + distance, c), self.board))
            elif self.board[r + distance][c].piece.color != self.board[r][c].piece.color:
                moves.append(Move((r, c), (r + distance, c), self.board))

    '''
    Move left a given distance
    '''

    def move_left(self, r, c, distance, moves):
        if c - distance >= 0:
            if self.board[r][c - distance].piece is None:
                moves.append(Move((r, c), (r, c - distance), self.board))
            elif self.board[r][c - distance].piece.color != self.board[r][c].piece.color:
                moves.append(Move((r, c), (r, c - distance), self.board))

    '''
    Move right a given distance
    '''

    def move_right(self, r, c, distance, moves):
        if c + distance <= 7:
            if self.board[r][c + distance].piece is None:
                moves.append(Move((r, c), (r, c + distance), self.board))
            elif self.board[r][c + distance].piece.color != self.board[r][c].piece.color:
                moves.append(Move((r, c), (r, c + distance), self.board))
