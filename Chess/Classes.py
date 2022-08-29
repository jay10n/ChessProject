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
    def get_piece_directions(cls, piece_type):
        match piece_type:
            case PieceType.King | PieceType.Queen:
                return cls.get_rook_directions() + cls.get_bishop_directions()
            case PieceType.Rook:
                return cls.get_rook_directions()
            case PieceType.Bishop:
                return cls.get_bishop_directions()
            case PieceType.Knight:
                return cls.get_knight_directions()
            case PieceType.Pawn:
                return cls.get_bishop_directions()

    '''
    @classmethod
    def get_pawn_directions(cls):
        if piece_color == Color.White:
            return [cls.Up]
        else:
            return [cls.Down]
            '''

    @classmethod
    def get_bishop_directions(cls):
        return [cls.Up_Left,
                cls.Up_Right,
                cls.Down_Left,
                cls.Down_Right]

    @classmethod
    def get_rook_directions(cls):
        return [cls.Up,
                cls.Down,
                cls.Left,
                cls.Right]

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

    '''
    @classmethod
    def get_standard_directions(cls):
        return [cls.Up,
                cls.Down,
                cls.Left,
                cls.Right,
                cls.Up_Left,
                cls.Up_Right,
                cls.Down_Left,
                cls.Down_Right]
                '''


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


class Piece:
    def __init__(self, piece_type, player, square):
        self.square = square
        self.has_moved = False
        self.player = player
        self.color = player.color
        self.type = piece_type
        self.material = typeToValue[piece_type]
        self.directions = []
        if self.color == Color.White:
            self.nameAbv = "w"
        else:
            self.nameAbv = "b"
        self.nameAbv += typeToAbv[self.type]


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


class Move:
    def __init__(self, start_square, end_square):
        self.start_square = start_square
        self.end_square = end_square
        self.piece_moved = start_square.piece
        self.pieceCaptured = end_square.piece

    def __init__(self, piece_to_move, direction, distance):
        pass

    def get_chess_notation(self):
        return get_rank_file(self.start_square.row, self.start_square.column) + \
               get_rank_file(self.end_square.row, self.end_square.column)

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.start_square.column == other.start_square.column \
                   and self.start_square.row == other.start_square.row \
                   and self.end_square.column == other.end_square.column \
                   and self.end_square.row == other.end_square.row
        else:
            return False


class Castle(Move):
    def __init__(self, start_square, end_square, rook_start_square, rook_end_square):
        super().__init__(start_square, end_square)
        self.rook = rook_start_square.piece
        self.rook_move = Move(rook_start_square, rook_end_square)


class EnPassant(Move):
    def __init__(self, start_square, end_square, piece_captured):
        super().__init__(start_square, end_square)
        self.pieceCaptured = piece_captured


def make_board(players):
    the_board = [[Square(0, 0, None, None) for _ in range(0, 8)] for _ in range(0, 8)]
    temp_player = players.black  # Used for populating with pieces.

    # populate board with pieces
    for row in range(ROW_SIZE):
        if row == 2:
            temp_player = players.white

        for column in range(COLUMN_SIZE):
            temp_piece = None
            temp_type = None
            temp_square = Square(row, column, Color((row + column) % 2), None)

            match row:
                case 0 | 7:
                    match column:
                        case 0 | 7:
                            temp_type = PieceType.Rook
                            # temp_type = PieceType.Queen
                        case 1 | 6:
                            temp_type = PieceType.Knight
                            # temp_type = PieceType.Queen

                        case 2 | 5:
                            temp_type = PieceType.Bishop
                            # temp_type = PieceType.Queen
                        case 3:
                            temp_type = PieceType.Queen
                            # temp_type = PieceType.Queen
                        case 4:
                            temp_type = PieceType.King
                case 1 | 6:
                    temp_type = PieceType.Pawn
                    # temp_type = PieceType.Queen

            # if piece creates abd sets to square and player
            if temp_type:
                temp_piece = Piece(temp_type, temp_player, temp_square)
                temp_player.piece_list.append(temp_piece)
                if temp_type == PieceType.King:
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
        move.end_square.update_piece(move.piece_moved)
        move.start_square.update_piece(None)

        if move.pieceCaptured:
            self.player_waiting.piece_list.remove(move.pieceCaptured)

        self.moveLog.append(move)

    def undo_move(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            move.start_square.update_piece(move.piece_moved)

            if isinstance(move, Castle):
                move.rook_move.start_square.update_piece(move.rook)
                move.rook_move.end_square.update_piece(None)
                move.rook.has_moved = False
                move.piece_moved.has_moved = False

            if isinstance(move, EnPassant):
                move.pieceCaptured.square.update_piece(move.pieceCaptured)
                move.end_square.update_piece(None)
            else:
                move.end_square.update_piece(move.pieceCaptured)

            if move.pieceCaptured:
                self.player_waiting.piece_list.append(move.pieceCaptured)  # adds captured piece back to players list

    def square_is_seen(self, square, player, opponent):
        for direction in Direction:
            row = square.row + direction.value[0]
            col = square.column + direction.value[1]
            distance = 1
            knight_move = False
            while row in range(ROW_SIZE) and col in range(COLUMN_SIZE) and not knight_move:
                temp_piece = self.board[row][col].piece
                if temp_piece is not None:
                    if temp_piece.color == opponent.color:
                        match direction:
                            case Direction.Up | Direction.Down | Direction.Left | Direction.Right:
                                if temp_piece.type == PieceType.King and distance == 1:
                                    return True
                                elif temp_piece.type == PieceType.Rook or temp_piece.type == PieceType.Queen:
                                    return True
                            case Direction.Up_Left | Direction.Up_Right | Direction.Down_Left | Direction.Down_Right:
                                if temp_piece.type == PieceType.King and distance == 1:
                                    return True
                                elif temp_piece.type == PieceType.Pawn:
                                    if square.row - row == 1 and player.color == Color.White:
                                        return True
                                    if row - square.row == 1 and player.color == Color.Black:
                                        return True
                                elif temp_piece.type == PieceType.Queen or temp_piece.type == PieceType.Bishop:
                                    return True
                            case _:
                                if temp_piece.type == PieceType.Knight:
                                    return True
                                else:
                                    break

                    break
                row += direction.value[0]
                col += direction.value[1]
                distance += 1
                if distance == 2 and direction in Direction.get_knight_directions():
                    knight_move = True
        return False

    def is_in_check(self, player, opponent):
        return self.square_is_seen(player.king.square, player, opponent)

    def is_legal_castle(self, player, opponent, move):
        if player.king.has_moved or move.rook.has_moved:
            return False
        else:
            if move.end_square.column == 6:
                side = [4, 5, 6]  # King's Side
            else:
                side = [4, 3, 2]  # Queen's Side

            for x in range(3):
                if self.square_is_seen(self.board[player.back_row][side[x]], player, opponent):
                    return False
            return True

    @staticmethod
    def can_promote_pawn(move):
        if move.piece_moved.type == PieceType.Pawn:
            if move.end_square.row == 0 or move.end_square.row == 7:
                return True
        return False

    @staticmethod
    def promote_pawn(player, move, is_ai):
        temp_type = None
        promotion_square = move.end_square
        if is_ai:
            # TODO fix warning
            temp_type = PieceType.get_promotable_pieces()[random.randint(4)]
        else:
            user_selection = " "
            while temp_type is None:
                if user_selection in ["Q", "R", "B", "N"]:
                    temp_type = abvToType[user_selection]
                else:
                    user_selection = input("What would you like to promote to? (Q, R, B, N): ")
        player.piece_list.remove(move.piece_moved)
        move.end_square.piece = None
        new_piece = Piece(temp_type, player, promotion_square)
        new_piece.has_moved = True
        promotion_square.piece = new_piece
        player.piece_list.append(new_piece)

    def get_valid_moves(self, player, opponent):
        possible_moves = self.add_possible_moves(player)
        invalid_moves = []

        for move in possible_moves:
            self.make_move(move)
            match move:
                case Castle():
                    if not self.is_legal_castle(player, opponent, move):
                        invalid_moves.append(move)
                case EnPassant():
                    if self.is_in_check(player, opponent):
                        invalid_moves.append(move)
                case Move():
                    if self.is_in_check(player, opponent):
                        invalid_moves.append(move)
            self.undo_move()

        for move in invalid_moves:
            possible_moves.remove(move)
        return possible_moves

    def add_possible_moves(self, player):
        moves = []
        for piece in player.piece_list:
            match piece.type:
                case PieceType.Pawn:
                    self.add_pawn_moves(piece, moves)
                case _:
                    self.add_piece_moves(piece, moves)

        return moves

    def add_king_moves(self, piece_to_move, moves):
        for direction in Direction.get_piece_directions(PieceType.King):
            self.add_move(piece_to_move, direction, 1, moves)
        self.add_castle_moves(piece_to_move, moves)

    def add_castle_moves(self, piece_to_move, moves):
        if not piece_to_move.has_moved:
            king_post_castle_col = [6, 2]
            rook_post_castle_col = [5, 3]
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
                            final_king_square = self.board[piece_to_move.square.row][king_post_castle_col[kq_side]]
                            final_rook_square = self.board[temp_rook.square.row][rook_post_castle_col[kq_side]]
                            moves.append(Castle(piece_to_move.square,
                                                final_king_square,
                                                temp_rook.square,
                                                final_rook_square))

    def add_piece_moves(self, piece, moves):
        for direction in Direction.get_piece_directions(piece.type):
            for distance in range(1, 8):
                if self.potential_move_in_bounds(piece, direction, distance):
                    potential_square = self.get_potential_square(piece, direction, distance)
                    if self.potential_move_is_possible(piece, potential_square):
                        moves.append(Move(piece.square, potential_square))
                    if potential_square.piece or piece.type in [PieceType.Knight, PieceType.King]:
                        break
                else:
                    break

    def get_potential_square(self, piece, direction, distance):
        return self.board[piece.square.row + direction.value[0] * distance][piece.square.column + direction.value[1] * distance]

    def potential_move_in_bounds(self, piece, direction, distance):
        if (piece.square.row + direction.value[0] * distance) in range(ROW_SIZE) and (piece.square.column + direction.value[1] * distance) in range(COLUMN_SIZE):
            return True
        else:
            return False

    def potential_move_is_possible(self, piece, potential_square):
        if potential_square.piece:
            if potential_square.piece.color != piece.color:
                return True
            else:
                return False
        else:
            return True

    '''
    def add_queen_moves(self, piece, moves):
        self.add_rook_moves(piece, moves)
        self.add_bishop_moves(piece, moves)

    def add_rook_moves(self, piece, moves):
        row = piece.square.row
        column = piece.square.column

        for distance in range(1, row + 1):
            self.add_move(piece, Direction.Up, distance, moves)
            if self.board[row - distance][column].piece:
                break

        for distance in range(1, ROW_SIZE - row):
            self.add_move(piece, Direction.Down, distance, moves)
            if self.board[row + distance][column].piece:
                break

        for distance in range(1, column + 1):
            self.add_move(piece, Direction.Left, distance, moves)
            if self.board[row][column - distance].piece:
                break

        for distance in range(1, COLUMN_SIZE - column):
            self.add_move(piece, Direction.Right, distance, moves)
            if self.board[row][column + distance].piece:
                break

        return moves
        

    def add_bishop_moves(self, piece, moves):
        row = piece.square.row
        column = piece.square.column
        for distance in range(1, MAX_DIAGONAL_SIZE):  # up and left
            if row - distance < 0 or column - distance < 0:
                break
            else:
                self.add_move(piece, Direction.Up_Left, distance, moves)
                if self.board[row - distance][column - distance].piece:
                    break

        for distance in range(1, MAX_DIAGONAL_SIZE):  # up and right
            if row - distance < 0 or column + distance > 7:
                break
            else:
                self.add_move(piece, Direction.Up_Right, distance, moves)
                if self.board[row - distance][column + distance].piece:
                    break

        for distance in range(1, MAX_DIAGONAL_SIZE):  # down and right
            if row + distance > 7 or column + distance > 7:
                break
            else:
                self.add_move(piece, Direction.Down_Right, distance, moves)
                if self.board[row + distance][column + distance].piece:
                    break

        for distance in range(1, MAX_DIAGONAL_SIZE):  # down and left
            if row + distance > 7 or column - distance < 0:
                break
            else:
                self.add_move(piece, Direction.Down_Left, distance, moves)
                if self.board[row + distance][column - distance].piece:
                    break

        return moves

    def add_knight_moves(self, knight, moves):
        for direction in Direction.get_knight_directions():
            row = knight.square.row + direction.value[0]
            column = knight.square.column + direction.value[1]
            # row += direction.value[0]
            # column += direction.value[1]
            if row in range(ROW_SIZE) and column in range(COLUMN_SIZE):
                temp_square = self.board[row][column]
                temp_piece = temp_square.piece
                if temp_piece is None:
                    moves.append(Move(knight.square, temp_square))
                elif temp_piece.color.name != knight.color.name:
                    moves.append(Move(knight.square, temp_square))
                    
                    '''

    def add_ep(self, pawn, opponent_pawn, left_right, moves):
        # left = -1 right = 1
        adjacent_piece = self.board[pawn.square.row][pawn.square.column + left_right].piece
        if adjacent_piece == opponent_pawn:
            if pawn.color == Color.White:
                moves.append(
                    EnPassant(pawn.square, self.board[pawn.square.row - 1][pawn.square.column + left_right],
                              opponent_pawn))
            else:
                moves.append(
                    EnPassant(pawn.square, self.board[pawn.square.row + 1][pawn.square.column + left_right],
                              opponent_pawn))

    def get_enpassant(self, pawn, moves):
        left = -1
        right = 1
        if (pawn.color == Color.White and pawn.square.row == 3) or (pawn.color == Color.Black and pawn.square.row == 4):
            previous_move = self.moveLog[len(self.moveLog) - 1]
            if previous_move.piece_moved.type == PieceType.Pawn:
                if abs(previous_move.start_square.row - previous_move.end_square.row) == 2:
                    if pawn.square.column == 0:
                        self.add_ep(pawn, previous_move.piece_moved, right, moves)
                    elif pawn.square.column == 7:
                        self.add_ep(pawn, previous_move.piece_moved, left, moves)
                    else:
                        self.add_ep(pawn, previous_move.piece_moved, right, moves)
                        self.add_ep(pawn, previous_move.piece_moved, left, moves)

    def add_pawn_moves(self, pawn, moves):
        row = pawn.square.row
        column = pawn.square.column
        self.get_enpassant(pawn, moves)

        if row != 7 and row != 0:
            match pawn.color:
                case Color.White:
                    self.add_move(pawn, Direction.Up, 1, moves)
                    if not pawn.has_moved and self.board[row - 1][column].piece is None:
                        self.add_move(pawn, Direction.Up, 2, moves)
                    self.add_move(pawn, Direction.Up_Left, 1, moves)
                    self.add_move(pawn, Direction.Up_Right, 1, moves)
                case Color.Black:
                    self.add_move(pawn, Direction.Down, 1, moves)
                    if not pawn.has_moved and self.board[row + 1][column].piece is None:
                        self.add_move(pawn, Direction.Down, 2, moves)
                    self.add_move(pawn, Direction.Down_Left, 1, moves)
                    self.add_move(pawn, Direction.Down_Right, 1, moves)

    def add_move(self, piece, direction, distance, moves):
        row = piece.square.row + (direction.value[0] * distance)
        column = piece.square.column + (direction.value[1] * distance)
        if row in range(ROW_SIZE) and column in range(COLUMN_SIZE):
            temp_square = self.board[row][column]
            match piece.type:
                case PieceType.Pawn:
                    if temp_square.piece is None:
                        if direction == Direction.Up or direction == Direction.Down:
                            moves.append(Move(piece.square, temp_square))
                    elif temp_square.piece.color != piece.color and direction != Direction.Up and \
                            direction != Direction.Down:
                        moves.append(Move(piece.square, temp_square))
                case _:
                    if temp_square.piece is None:
                        moves.append(Move(piece.square, temp_square))
                    elif temp_square.piece.color != piece.color:
                        moves.append(Move(piece.square, temp_square))
