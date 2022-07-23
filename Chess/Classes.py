#
# Classes needed for chess game.
#
from enum import Enum
import random


class Color(Enum):
    White = 0
    Black = 1


class Type(Enum):
    King = 0
    Queen = 1
    Rook = 2
    Bishop = 3
    Knight = 4
    Pawn = 5


# maps key : val
rankToRow = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
rowToRank = {v: k for k, v in rankToRow.items()}
fileToColumn = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
columnToFile = {v: k for k, v in fileToColumn.items()}
abvToType = {"K": Type.King, "Q": Type.Queen, "R": Type.Rook, "B": Type.Bishop, "N": Type.Knight, "p": Type.Pawn}
typeToAbv = {v: k for k, v in abvToType.items()}
typeToValue = {Type.King: 0, Type.Queen: 9, Type.Rook: 5, Type.Bishop: 3, Type.Knight: 3, Type.Pawn: 1}


#
# @param (row, column)
# @returns rank + file as string
#
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
    def __init__(self, piece_type, color, square):
        self.square = square
        self.has_moved = False
        self.color = color
        self.type = piece_type
        self.value = typeToValue[self.type]
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


class Move:
    def __init__(self, start_square, end_square):
        #self.startRow = start_coords[0]
        #self.startColumn = start_coords[1]
        #self.endRow = end_coords[0]
        #self.endColumn = end_coords[1]
        self.start_square = start_square
        self.end_square = end_square
        self.pieceMoved = start_square.piece
        self.pieceCaptured = end_square.piece
        self.move_type = "move"

    def get_chess_notation(self):
        return get_rank_file(self.start_square.row, self.start_square.column) +\
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
        self.move_type = "castle"


class EnPassant(Move):
    def __init__(self, start_coords, end_coords, board):
        super().__init__(start_coords, end_coords, board)
        self.pieceCaptured = board.grid[self.endRow + 1][self.endColumn]
        self.move_type = "enpassant"


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
                temp_type = None
                match row:
                    case 0 | 7:
                        match column:
                            case 0 | 7:
                                temp_type = Type.Rook
                            case 1 | 6:
                                temp_type = Type.Knight
                            case 2 | 5:
                                temp_type = Type.Bishop
                            case 3:
                                temp_type = Type.Queen
                            case 4:
                                temp_type = Type.King
                    case 1 | 6:
                        temp_type = Type.Pawn

                if temp_type is not None:
                    temp_piece = Piece(temp_type, temp_color, temp_square)

                self.grid[row][column].piece = temp_piece


class GameState:
    # Create game state, grid, players
    def __init__(self):
        self.player_white = Player(Color.White)
        self.player_black = Player(Color.Black)
        self.moveLog = []
        self.board = Board()
        self.player_moving = self.player_white
        self.player_waiting = self.player_black

        # Add pieces to player lists
        for row in range(8):
            for column in range(8):
                match row:
                    case 0 | 1 | 6 | 7:
                        temp_piece = self.board.grid[row][column].piece
                        if temp_piece.color == Color.White:
                            self.player_white.piece_list.append(temp_piece)
                            if temp_piece.type == Type.King:
                                self.player_white.king = temp_piece
                        if temp_piece.color == Color.Black:
                            self.player_black.piece_list.append(temp_piece)
                            if temp_piece.type == Type.King:
                                self.player_black.king = temp_piece

    def toggle_turn(self):
        temp_player = self.player_moving
        self.player_moving = self.player_waiting
        self.player_waiting = temp_player

    def make_move(self, move):
        if move.move_type == "castle":
            self.make_move(move.rook_move)

        self.board.grid[move.endRow][move.endColumn].piece = move.pieceMoved
        move.pieceMoved.square = self.board.grid[move.endRow][move.endColumn]
        self.board.grid[move.startRow][move.startColumn].piece = None
        if move.pieceCaptured is not None:
            self.player_waiting.piece_list.remove(move.pieceCaptured)

        self.moveLog.append(move)

    def undo_move(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()

            # Moved Piece
            self.board.grid[move.startRow][move.startColumn].piece = move.pieceMoved  # Puts piece moved back
            move.pieceMoved.square = self.board.grid[move.startRow][move.startColumn]  # update piece moved square

            # Captured Piece
            self.board.grid[move.endRow][move.endColumn].piece = move.pieceCaptured  # puts captured piece back if any
            if move.pieceCaptured is not None:
                self.player_waiting.piece_list.append(move.pieceCaptured)  # adds captured piece back to players list

            # Handles Castling
            if move.move_type == "castle":
                self.board.grid[move.rook_move.startRow][move.rook_move.startColumn].piece = move.rook
                move.rook.square = self.board.grid[move.rook_move.startRow][move.rook_move.startColumn]
                self.board.grid[move.rook_move.endRow][move.rook_move.endColumn].piece = None
                move.rook.has_moved = False

                # needed for castle glitch
                # TODO Fix this
                if move.pieceMoved:
                    move.pieceMoved.has_moved = False

    def square_is_seen(self, square, player, opponent):
        square_row = square.row
        square_column = square.column

        # up down left right and diagonal
        direction_array = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1),
                           (-1, -2), (-1, 2), (1, -2), (1, 2), (-2, -1), (-2, 1), (2, -1), (2, 1)]
        for direction in range(16):
            row = square_row
            col = square_column
            row += direction_array[direction][0]
            col += direction_array[direction][1]
            distance = 1
            while row in range(8) and col in range(8):
                temp_piece = self.board.grid[row][col].piece
                if temp_piece is not None:
                    if temp_piece.color.name == opponent.color.name:
                        match direction:
                            case 0 | 1 | 2 | 3:
                                if temp_piece.type == Type.Rook or temp_piece.type == Type.Queen:
                                    return True
                                elif temp_piece.type == Type.King and distance == 1:
                                    return True
                            case 4 | 5 | 6 | 7:
                                if temp_piece.type == Type.King and distance == 1:
                                    return True
                                elif temp_piece.type == Type.Pawn:
                                    if square_row - row == 1 and player.color == Color.White:
                                        return True
                                    if row - square_row == 1 and player.color == Color.Black:
                                        return True
                                elif temp_piece.type == Type.Queen or temp_piece.type == Type.Bishop:
                                    return True
                            case _:
                                if temp_piece.type == Type.Knight:
                                    return True
                                else:
                                    break

                    break
                row += direction_array[direction][0]
                col += direction_array[direction][1]
                distance += 1
        return False

    def is_in_check(self, player, opponent):
        return self.square_is_seen(player.king.square, player, opponent)

    def is_legal_castle(self, player, opponent, move):
        if player.king.has_moved or move.rook.has_moved:
            return False
        else:
            kq_side = [[4, 5, 6], [4, 3, 2]]
            if move.endColumn == 6:
                side = kq_side[0]
            else:
                side = kq_side[1]

            for x in range(3):
                if self.square_is_seen(self.board.grid[player.back_row][side[x]], player, opponent):
                    return False
            return True

    def can_promote_pawn(self, move):
        if move.pieceMoved.type == Type.Pawn:
            if move.endRow == 0 or move.endRow == 7:
                return True
        return False

    def promote_pawn(self, player, move, is_ai):
        temp_type = None
        promotion_square = self.board.grid[move.endRow][move.endColumn]
        if is_ai:
            temp_type = Type(random.randint(1, 5))
        else:
            user_selection = " "
            while temp_type is None:
                if user_selection in ["Q", "R", "B", "N"]:
                    temp_type = abvToType[user_selection]
                else:
                    user_selection = input("What would you like to promote to? (Q, R, B, N): ")
        new_piece = Piece(temp_type, self.player_moving.color, promotion_square)
        promotion_square.piece = new_piece
        player.piece_list.append(new_piece)
        player.piece_list.remove(move.pieceMoved)
        move.pieceMoved = new_piece

    def get_valid_moves(self, player, opponent):
        possible_moves = self.get_possible_moves(player)
        invalid_moves = []
        for move in possible_moves:
            self.make_move(move)
            match move.move_type:
                case "castle":
                    if not self.is_legal_castle(player, opponent, move):
                        invalid_moves.append(move)
                case "enpassant":
                    pass
                case "move":
                    if self.is_in_check(player, opponent):
                        invalid_moves.append(move)
            self.undo_move()
        for move in invalid_moves:
            possible_moves.remove(move)
        return possible_moves

    def get_possible_moves(self, player):
        moves = []
        for piece in player.piece_list:
            row = piece.square.row
            column = piece.square.column
            match piece.type:
                case Type.King:
                    self.get_king_moves(piece, moves)
                case Type.Queen:
                    self.get_queen_moves(row, column, moves)
                case Type.Rook:
                    self.get_rook_moves(row, column, moves)
                case Type.Bishop:
                    self.get_bishop_moves(row, column, moves)
                case Type.Knight:
                    self.get_knight_moves(piece, moves)
                case Type.Pawn:
                    self.get_pawn_moves(piece, moves)
        return moves

    def get_king_moves(self,king, moves):
        r = king.square.row
        c = king.square.column
        self.move_up(r, c, 1, moves)
        self.move_down(r, c, 1, moves)
        self.move_left(r, c, 1, moves)
        self.move_right(r, c, 1, moves)
        self.move_down_left(r, c, 1, moves)
        self.move_down_right(r, c, 1, moves)
        self.move_up_left(r, c, 1, moves)
        self.move_up_right(r, c, 1, moves)

        self.get_castle_moves(king, moves)

    def get_castle_moves(self, king, moves):
        if not king.has_moved:
            king_post_castle_col = [6, 2]
            rook_post_castle_col = [5, 3]
            rook_col = [7, 0]
            castle_ranges = [[5, 7],  # King's side
                             [1, 4]]  # Queen's side
            for kq_side in range(2):
                temp_rook = self.board.grid[king.square.row][rook_col[kq_side]].piece
                if temp_rook:
                    if not temp_rook.has_moved:
                        can_castle = True
                        for x in range(castle_ranges[kq_side][0], castle_ranges[kq_side][1]):
                            if self.board.grid[king.square.row][x].piece:
                                can_castle = False
                        if can_castle:
                            moves.append(Castle((king.square.row, 4),
                                                (king.square.row, king_post_castle_col[kq_side]),
                                                self.board,
                                                (king.square.row, rook_col[kq_side]),
                                                (king.square.row, rook_post_castle_col[kq_side])))

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

    def get_knight_moves(self, knight, moves):
        direction_array = [(-1, -2), (-1, 2), (1, -2), (1, 2), (-2, -1), (-2, 1), (2, -1), (2, 1)]
        for direction in range(8):
            row = knight.square.row
            col = knight.square.column
            row += direction_array[direction][0]
            col += direction_array[direction][1]
            if row in range(8) and col in range(8):
                temp_piece = self.board.grid[row][col].piece
                if temp_piece is None:
                    moves.append(Move((knight.square.row, knight.square.column), (row, col), self.board))
                elif temp_piece.color.name != knight.color.name:
                    moves.append(Move((knight.square.row, knight.square.column), (row, col), self.board))

    def get_pawn_moves(self, pawn, moves):
        r = pawn.square.row
        c = pawn.square.column
        if r != (0 | 7):
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
