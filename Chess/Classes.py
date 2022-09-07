#
# Classes needed for chess game.
#
from collections import namedtuple
from enum import Enum
import random

ROW_SIZE = 8
COLUMN_SIZE = 8
MAX_DIAGONAL_SIZE = 8


class Color(Enum):
    White = 0
    Black = 1


class PieceType(Enum):
    King = 0
    Queen = 1
    Rook = 2
    Bishop = 3
    Knight = 4
    Pawn = 5

    @classmethod
    def get_promotable_pieces(cls):
        return [cls.Queen,
                cls.Rook,
                cls.Bishop,
                cls.Knight]


class Direction(Enum):
    Up = (-1, 0)
    Down = (1, 0)
    Left = (0, -1)
    Right = (0, 1)
    Up_Left = (-1, -1)
    Up_Right = (-1, 1)
    Down_Left = (1, -1)
    Down_Right = (1, 1)
    Knight_Left_Up = (-1, -2)
    Knight_Right_Up = (-1, 2)
    Knight_Left_Down = (1, -2)
    Knight_Right_Down = (1, 2)
    Knight_Up_Left = (-2, -1)
    Knight_Up_Right = (-2, 1)
    Knight_Down_Left = (2, -1)
    Knight_Down_Right = (2, 1)

    @classmethod
    def get_inverse_direction(cls, direction):
        return Direction((-direction.value[0], -direction.value[1]))

    @classmethod
    def get_knight_directions(cls):
        return [cls.Knight_Left_Up,
                cls.Knight_Right_Up,
                cls.Knight_Left_Down,
                cls.Knight_Right_Down,
                cls.Knight_Up_Left,
                cls.Knight_Up_Right,
                cls.Knight_Down_Left,
                cls.Knight_Down_Right]


# dicts
rankToRow = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
rowToRank = {v: k for k, v in rankToRow.items()}
fileToColumn = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
columnToFile = {v: k for k, v in fileToColumn.items()}

abvToType = {"K": PieceType.King,
             "Q": PieceType.Queen,
             "R": PieceType.Rook,
             "B": PieceType.Bishop,
             "N": PieceType.Knight,
             "p": PieceType.Pawn}
typeToAbv = {v: k for k, v in abvToType.items()}

typeToValue = {PieceType.King: 0,
               PieceType.Queen: 9,
               PieceType.Rook: 5,
               PieceType.Bishop: 3,
               PieceType.Knight: 3,
               PieceType.Pawn: 1}


def get_rank_file(row, column):
    return columnToFile[column] + rowToRank[row]


class Player:
    def __init__(self, color):
        self.color = color
        self.piece_list = []
        self.king = None
        self.material = 0
        match self.color:
            case Color.White:
                self.back_row = 7
            case Color.Black:
                self.back_row = 0

    def is_in_check(self, board):
        return self.king.square.is_seen(self, board)


class Piece:
    def __init__(self, player, square):
        self.square = square
        self.has_moved = False
        self.player = player
        self.color = player.color
        self.move_directions = []
        self.sees_directions = []
        self.max_move_distance = 8
        self.material_value = None
        if self.color == Color.White:
            self.nameAbv = "w"
        else:
            self.nameAbv = "b"


class Pawn(Piece):
    def __init__(self, player, square):
        super().__init__(player, square)
        self.material_value = 1
        self.nameAbv = self.nameAbv + "p"
        self.max_move_distance = 1
        match self.color:
            case Color.White:
                self.sees_directions = [Direction.Up_Left, Direction.Up_Right]
                self.move_directions = self.sees_directions + [Direction.Up]

            case Color.Black:
                self.sees_directions = [Direction.Down_Left, Direction.Down_Right]
                self.move_directions = self.sees_directions + [Direction.Down]

    def can_promote(self):
        if self.square.row in [0, 7]:
            return True
        else:
            return False


class Knight(Piece):
    def __init__(self, player, square):
        super().__init__(player, square)
        self.material_value = 3
        self.nameAbv = self.nameAbv + "N"
        self.max_move_distance = 1
        self.move_directions = self.sees_directions = [Direction.Knight_Left_Up,
                                                       Direction.Knight_Right_Up,
                                                       Direction.Knight_Left_Down,
                                                       Direction.Knight_Right_Down,
                                                       Direction.Knight_Up_Left,
                                                       Direction.Knight_Up_Right,
                                                       Direction.Knight_Down_Left,
                                                       Direction.Knight_Down_Right]


class Bishop(Piece):
    def __init__(self, player, square):
        super().__init__(player, square)
        self.material_value = 3
        self.nameAbv = self.nameAbv + "B"
        self.move_directions = self.sees_directions = [Direction.Up_Left,
                                                       Direction.Up_Right,
                                                       Direction.Down_Left,
                                                       Direction.Down_Right]


class Rook(Piece):
    def __init__(self, player, square):
        super().__init__(player, square)
        self.material_value = 5
        self.nameAbv = self.nameAbv + "R"
        self.move_directions = self.sees_directions = [Direction.Up,
                                                       Direction.Down,
                                                       Direction.Left,
                                                       Direction.Right]
        self.castle_directions = [Direction.Left, Direction.Right]
        self.castle_move_distance = [2, 3]


class Queen(Piece):
    def __init__(self, player, square):
        super().__init__(player, square)
        self.material_value = 9
        self.nameAbv = self.nameAbv + "Q"
        self.move_directions = self.sees_directions = [Direction.Up,
                                                       Direction.Down,
                                                       Direction.Left,
                                                       Direction.Right,
                                                       Direction.Up_Left,
                                                       Direction.Up_Right,
                                                       Direction.Down_Left,
                                                       Direction.Down_Right]


class King(Piece):
    def __init__(self, player, square):
        super().__init__(player, square)
        self.material_value = 0
        self.nameAbv = self.nameAbv + "K"
        self.max_move_distance = 1
        self.move_directions = self.sees_directions = [Direction.Up,
                                                       Direction.Down,
                                                       Direction.Left,
                                                       Direction.Right,
                                                       Direction.Up_Left,
                                                       Direction.Up_Right,
                                                       Direction.Down_Left,
                                                       Direction.Down_Right]
        self.castle_directions = [Direction.Right, Direction.Left]
        self.castle_move_distance = 2


class Square:
    def __init__(self, row, column, color, piece):
        self.row = row
        self.column = column
        self.color = color
        self.piece = piece

    # Sets piece to square and square to piece
    def update_piece(self, piece):
        self.piece = piece
        if self.piece:
            self.piece.square = self

    def is_seen(self, player_moving, board):
        for direction in Direction:
            row = self.row + direction.value[0]
            column = self.column + direction.value[1]
            distance = 1
            while row in range(ROW_SIZE) and column in range(COLUMN_SIZE):
                potential_piece = board[row][column].piece
                if potential_piece:
                    if potential_piece.color != player_moving.color and distance <= potential_piece.max_move_distance and \
                            Direction.get_inverse_direction(direction) in potential_piece.sees_directions:
                        return True
                    else:
                        break
                else:
                    if direction in Direction.get_knight_directions():
                        break
                    row += direction.value[0]
                    column += direction.value[1]
                    distance += 1
        return False


class Move:
    def __init__(self, piece_moving, direction, distance, board):
        self.piece_moving = piece_moving
        self.direction = direction
        self.distance = distance
        self.board = board
        self.is_possible = False
        if self.in_bounds():
            self.start_square = piece_moving.square
            self.end_square = self.get_end_square()
            self.is_possible = self.potential_move_is_possible()
            self.pieceCaptured = self.end_square.piece

    def get_end_square(self):
        return self.board[self.piece_moving.square.row + self.direction.value[0] * self.distance][self.piece_moving.square.column + self.direction.value[1] * self.distance]

    def in_bounds(self):
        if (self.piece_moving.square.row + self.direction.value[0] * self.distance) in range(ROW_SIZE) and \
                (self.piece_moving.square.column + self.direction.value[1] * self.distance) in range(COLUMN_SIZE):
            return True
        else:
            return False

    def potential_move_is_possible(self):
        if isinstance(self.piece_moving, Pawn):
            if self.direction in [Direction.Up, Direction.Down]:
                if self.end_square.piece:
                    return False
                else:
                    return True
            else:
                if self.end_square.piece:
                    if self.end_square.piece.color != self.piece_moving.color:
                        return True
                    else:
                        return False
        if self.end_square.piece:
            if self.end_square.piece.color != self.piece_moving.color:
                return True
            else:
                return False
        else:
            return True

    def get_chess_notation(self):
        return get_rank_file(self.start_square.row, self.start_square.column) + \
               get_rank_file(self.end_square.row, self.end_square.column)

    def __eq__(self, other):
        return self.start_square == other.start_square and self.end_square == other.end_square


class Castle(Move):
    def __init__(self, piece_moving, direction, distance, board, rook, rook_direction, rook_distance):
        super().__init__(piece_moving, direction, distance, board)
        self.rook = rook
        self.rook_move = Move(self.rook, rook_direction, rook_distance, board)


class EnPassant(Move):
    def __init__(self, piece_moving, direction, distance, board):
        super().__init__(piece_moving, direction, distance, board)
        self.pieceCaptured = self.board[self.start_square.row][self.end_square.column].piece


def make_board(players):
    the_board = [[Square(0, 0, None, None) for _ in range(0, 8)] for _ in range(0, 8)]
    temp_player = players.black  # Used for populating with pieces.

    for row in range(ROW_SIZE):  # populate board with pieces
        if row == 2:
            temp_player = players.white
        for column in range(COLUMN_SIZE):
            temp_piece = None
            temp_square = Square(row, column, Color((row + column) % 2), None)
            match row:
                case 0 | 7:
                    match column:
                        case 0 | 7:
                            temp_piece = Rook(temp_player, temp_square)
                        case 1 | 6:
                            temp_piece = Knight(temp_player, temp_square)
                        case 2 | 5:
                            temp_piece = Bishop(temp_player, temp_square)
                        case 3:
                            temp_piece = Queen(temp_player, temp_square)
                        case 4:
                            temp_piece = King(temp_player, temp_square)
                case 1 | 6:
                    temp_piece = Pawn(temp_player, temp_square)

            # if piece creates abd sets to square and player
            if temp_piece:
                temp_player.piece_list.append(temp_piece)
                if isinstance(temp_piece, King):
                    temp_player.king = temp_piece

            temp_square.piece = temp_piece
            the_board[row][column] = temp_square

    return the_board


class GameState:
    # Create game state, players
    def __init__(self):
        self.checkmate = False
        self.stalemate = False
        self.players = namedtuple('Players', ['white', 'black'])
        self.players.white = Player(Color.White)
        self.players.black = Player(Color.Black)
        self.player_moving = self.players.white
        self.player_waiting = self.players.black
        self.board = make_board(self.players)
        self.moveLog = []

    def toggle_turn(self):
        temp_player = self.player_moving
        self.player_moving = self.player_waiting
        self.player_waiting = temp_player

    def make_move(self, move):
        if isinstance(move, Castle):
            self.make_move(move.rook_move)
        elif isinstance(move, EnPassant):
            move.pieceCaptured.square.piece = None

        # updates the moved piece and start square
        move.end_square.update_piece(move.piece_moving)
        move.start_square.update_piece(None)

        if move.pieceCaptured:
            self.player_waiting.piece_list.remove(move.pieceCaptured)

        self.moveLog.append(move)

    def undo_move(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            move.start_square.update_piece(move.piece_moving)

            if isinstance(move, Castle):
                move.rook_move.start_square.update_piece(move.rook)
                move.rook_move.end_square.update_piece(None)
                move.rook.has_moved = False
                move.piece_moving.has_moved = False

            if isinstance(move, EnPassant):
                move.pieceCaptured.square.update_piece(move.pieceCaptured)
                move.end_square.update_piece(None)
            else:
                move.end_square.update_piece(move.pieceCaptured)

            if move.pieceCaptured:
                self.player_waiting.piece_list.append(move.pieceCaptured)  # adds captured piece back to players list

    def is_legal_castle(self, player, move):
        if player.king.has_moved or move.rook.has_moved:
            return False
        else:
            if move.end_square.column == 6:
                side = [4, 5, 6]  # King's Side
            else:
                side = [4, 3, 2]  # Queen's Side

            for x in range(3):
                if self.board[player.back_row][side[x]].is_seen(player, self.board):
                    return False
            return True

    @staticmethod
    def can_promote_pawn(move):
        if isinstance(move.piece_moving, Pawn):
            if move.end_square.row == 0 or move.end_square.row == 7:
                return True
        return False

    @staticmethod
    def promote_pawn(player, move, is_ai):
        promotion_square = move.end_square
        '''
        if is_ai:
            # TODO fix warning
            # temp_type = PieceType.get_promotable_pieces()[random.randint(4)]
            temp_piece = Queen(player,promotion_square)
        else:
            user_selection = " "
            while temp_type is None:
                if user_selection in ["Q", "R", "B", "N"]:
                    temp_type = abvToType[user_selection]
                else:
                    user_selection = input("What would you like to promote to? (Q, R, B, N): ")
                    '''
        player.piece_list.remove(move.piece_moving)
        move.end_square.piece = None
        new_piece = Queen(player, promotion_square)
        new_piece.has_moved = True
        promotion_square.piece = new_piece
        player.piece_list.append(new_piece)

    def get_valid_moves(self, player):
        possible_moves = self.add_possible_moves(player)
        invalid_moves = []

        for move in possible_moves:
            self.make_move(move)
            match move:
                case Castle():
                    if not self.is_legal_castle(player, move):
                        invalid_moves.append(move)
                case EnPassant():
                    if player.is_in_check(self.board):
                        invalid_moves.append(move)
                case Move():
                    if player.is_in_check(self.board):
                        invalid_moves.append(move)
            self.undo_move()

        for move in invalid_moves:
            possible_moves.remove(move)
        return possible_moves

    def add_possible_moves(self, player):
        moves = []
        for piece in player.piece_list:
            if isinstance(piece, King):
                self.add_castle_moves(piece, moves)
            if isinstance(piece, Pawn):
                self.add_pawn_moves(piece, moves)
            for direction in piece.move_directions:
                for distance in range(1, 8):
                    potential_move = Move(piece, direction, distance, self.board)
                    if potential_move.is_possible:
                        moves.append(potential_move)
                        if potential_move.pieceCaptured or isinstance(piece, Knight):
                            break
                    else:
                        break
        return moves

    def add_castle_moves(self, piece_to_move, moves):
        if not piece_to_move.has_moved:
            rook_col = [7, 0]
            castle_ranges = [[5, 7],  # King's side
                             [1, 4]]  # Queen's side
            for kq_side in range(2):
                temp_rook = self.board[piece_to_move.square.row][rook_col[kq_side]].piece
                if temp_rook:
                    if not temp_rook.has_moved:
                        can_castle = True
                        for x in range(castle_ranges[kq_side][0], castle_ranges[kq_side][1]):
                            if self.board[piece_to_move.square.row][x].piece:
                                can_castle = False
                        if can_castle:
                            moves.append(
                                Castle(piece_to_move, piece_to_move.castle_directions[kq_side], piece_to_move.castle_move_distance, self.board, temp_rook,
                                       temp_rook.castle_directions[kq_side],
                                       temp_rook.castle_move_distance[kq_side]))

    def add_ep(self, pawn, opponent_pawn, left_right, moves):
        # left = -1 right = 1
        adjacent_piece = self.board[pawn.square.row][pawn.square.column + left_right].piece
        if adjacent_piece == opponent_pawn:
            if pawn.color == Color.White:
                if left_right == -1:
                    direction = Direction.Up_Left
                else:
                    direction = Direction.Up_Right
                moves.append(
                    EnPassant(pawn, direction, 1, self.board))
            else:
                if left_right == -1:
                    direction = Direction.Down_Left
                else:
                    direction = Direction.Down_Right
                moves.append(
                    EnPassant(pawn, direction, 1, self.board))

    def get_enpassant(self, pawn, moves):
        left = -1
        right = 1
        if (pawn.color == Color.White and pawn.square.row == 3) or (pawn.color == Color.Black and pawn.square.row == 4):
            previous_move = self.moveLog[len(self.moveLog) - 1]
            if isinstance(previous_move.piece_moving, Pawn):
                if abs(previous_move.start_square.row - previous_move.end_square.row) == 2:
                    if pawn.square.column == 0:
                        self.add_ep(pawn, previous_move.piece_moving, right, moves)
                    elif pawn.square.column == 7:
                        self.add_ep(pawn, previous_move.piece_moving, left, moves)
                    else:
                        self.add_ep(pawn, previous_move.piece_moving, right, moves)
                        self.add_ep(pawn, previous_move.piece_moving, left, moves)

    def add_pawn_moves(self, pawn, moves):
        self.get_enpassant(pawn, moves)
        potential_move = None
        match pawn.color:
            case Color.White:
                if not pawn.has_moved and self.board[pawn.square.row - 1][pawn.square.column].piece is None:
                    potential_move = Move(pawn, Direction.Up, 2, self.board)
            case Color.Black:
                if not pawn.has_moved and self.board[pawn.square.row + 1][pawn.square.column].piece is None:
                    potential_move = Move(pawn, Direction.Up, 2, self.board)
        if potential_move:
            if potential_move.is_possible:
                moves.append(potential_move)
