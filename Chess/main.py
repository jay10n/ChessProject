#
# Title: Chess Project
# About:
# Author: Jayton Schmeeckle
#         jvschmeeckle@gmail.com
# Date:
#
from collections import namedtuple

import pygame as p
from Chess import Classes, ChessAI
import time

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

# Sets up UI
colors = [p.Color("white"), p.Color("grey")]
selected_coordinate = namedtuple('Coordinate', ['row', 'column'])
selected_squares = namedtuple('square_selection', ['start_square', 'end_square'])


# selected_squares = []


def set_coordinate(row, column):
    selected_coordinate.row = row
    selected_coordinate.column = column


# Clears mouse selections
def clear_selections():
    selected_coordinate(None, None)
    selected_squares(None, None)


def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for x in pieces:
        IMAGES[x] = p.transform.scale(p.image.load("images/" + x + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    # Sets up GUI
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    load_images()

    # Set up Game State
    player_white_is_human = True
    player_black_is_human = True
    is_running = True
    gs = Classes.GameState()
    valid_moves = gs.get_valid_moves(gs.player_moving)
    move_made = animate = game_over = False  # flags
    square_selected = None
    print("\n------ " + gs.player_moving.color.name + "'s Turn! ------\n")

    # Run Game
    while is_running:
        is_human_turn = (gs.player_moving.color == Classes.Color.White and player_white_is_human) or \
                        (gs.player_moving.color == Classes.Color.Black and player_black_is_human)

        # When the player makes an action with mouse or keyboard
        for e in p.event.get():
            if is_human_turn:

                # Mouse Handlers
                if e.type == p.MOUSEBUTTONDOWN:
                    if not game_over:
                        location = p.mouse.get_pos()  # x,y pos. mouse
                        selected_column = location[0] // SQ_SIZE  # x pos
                        selected_row = location[1] // SQ_SIZE  # y pos

                        if selected_coordinate == (selected_row, selected_column):  # same square selected twice
                            clear_selections()
                        else:  # unique square selected
                            set_coordinate(selected_row, selected_column)
                            square_selected = gs.board[selected_coordinate.row][selected_coordinate.column]
                            if selected_squares.start_square is None:
                                selected_squares.start_square = square_selected
                            else:
                                selected_squares.end_square = square_selected

                        if selected_squares.start_square and selected_squares.end_square:  # Two squares selected
                            '''
                            move = Classes.Move(selected_squares[0], selected_squares[1])
                            if move in valid_moves:
                                the_move = valid_moves[valid_moves.index(move)]  # TODO fix castling error
                                '''
                            the_move = None
                            for move in valid_moves:
                                if move == selected_squares:
                                    the_move = move
                                    break

                            if the_move:
                                gs.make_move(the_move)
                                animate = move_made = True
                                the_move.piece_moving.has_moved = True
                                if gs.can_promote_pawn(the_move):  # handles pawn promotion
                                    draw_game_state(screen, gs, valid_moves, square_selected)
                                    clock.tick(MAX_FPS)
                                    p.display.flip()
                                    gs.promote_pawn(gs.player_moving, the_move, False)
                                clear_selections()
                                square_selected = None
                            else:
                                selected_squares(None, None)
                                selected_squares.start_square = gs.board[selected_coordinate.row][selected_coordinate.column]

                # Key Handlers
                elif e.type == p.QUIT:
                    is_running = False
                elif e.type == p.KEYDOWN:
                    if e.key == p.K_z:
                        gs.undo_move()
                        animate = False
                        move_made = True
                    elif e.key == p.K_r:
                        gs = Classes.GameState()
                        valid_moves = gs.get_valid_moves(gs.player_moving)
                        clear_selections()
                        square_selected = None
                        move_made = animate = False

        # Ai Move Handling
        if not is_human_turn and not game_over:
            ai_move = ChessAI.get_random_move(valid_moves)
            # time.sleep(1)
            gs.make_move(ai_move)
            # animate = True
            move_made = ai_move.piece_moving.has_moved = True
            if gs.can_promote_pawn(ai_move):
                draw_game_state(screen, gs, valid_moves, square_selected)
                clock.tick(MAX_FPS)
                p.display.flip()
                gs.promote_pawn(gs.player_moving, ai_move, True)

        # handle post move
        if move_made:
            if animate:
                animate_move(gs.moveLog[-1], screen, gs.board, clock)
            gs.toggle_turn()
            valid_moves = gs.get_valid_moves(gs.player_moving)
            print("===========================\n")
            if len(valid_moves) == 0:
                game_over = True
            else:
                print("------ " + gs.player_moving.color.name + "'s Turn! ------\n")
                if gs.player_moving.is_in_check(gs.board):
                    print(gs.player_moving.color.name + " is in Check!")
            move_made = False

        # update gui
        if not gs.checkmate and not gs.stalemate:
            draw_game_state(screen, gs, valid_moves, square_selected)
            clock.tick(MAX_FPS)
            p.display.flip()

            if game_over:
                if gs.player_moving.is_in_check(gs.board):
                    gs.checkmate = True
                    draw_text(screen, gs.player_waiting.color.name + " wins by Checkmate!")
                else:
                    gs.stalemate = True
                    draw_text(screen, "Stalemate!")


def animate_move(move, screen, board, clock):
    delta_row = move.end_square.row - move.start_square.row
    delta_column = move.end_square.column - move.start_square.column
    frames_per_square = 10
    frame_count = (abs(delta_row) + abs(delta_column)) * frames_per_square
    for frame in range(frame_count + 1):
        row, column = (move.start_square.row + delta_row * frame / frame_count, move.start_square.column + delta_column * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)

        # cover end square during animation
        temp_square = p.Rect(move.end_square.column * SQ_SIZE, move.end_square.row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, p.Color("white" if move.end_square.color == Classes.Color.White else "grey"), temp_square)

        # draw captured piece
        if move.pieceCaptured:
            screen.blit(IMAGES[move.pieceCaptured.nameAbv], temp_square)

        # draw moving piece
        screen.blit(IMAGES[move.piece_moving.nameAbv], p.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def highlight_squares(screen, gs, valid_moves, the_square):
    pass
    '''
    surface = p.Surface((SQ_SIZE, SQ_SIZE))
    surface.set_alpha(100)  # transparency 0 -> 255
    surface.fill(p.Color('red'))

    if gs.is_in_check(gs.player_moving, gs.player_waiting):
        screen.blit(surface, (gs.player_moving.king.square.column * SQ_SIZE, gs.player_moving.king.square.row * SQ_SIZE))

    if the_square:
        if the_square.piece:
            if (gs.player_moving == gs.players.white and the_square.piece.color == Classes.Color.White) or \
                    (gs.player_moving == gs.players.black and the_square.piece.color == Classes.Color.Black):

                # Highlight selected square
                surface.fill(p.Color('orange'))
                screen.blit(surface, (the_square.column * SQ_SIZE, the_square.row * SQ_SIZE))

                # highlight moves
                for move in valid_moves:
                    surface.fill(p.Color('yellow'))
                    if move.start_square == the_square:
                        if move.end_square.piece:
                            surface.fill(p.Color('green'))
                        screen.blit(surface, (move.end_square.column * SQ_SIZE, move.end_square.row * SQ_SIZE))
                        
                        '''


def draw_text(screen, text):
    font = p.font.SysFont("San Fransisco", 32, True, False)
    text_object = font.render(text, 0, p.Color('Grey'))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - text_object.get_width() / 2, HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color('Black'))
    screen.blit(text_object, text_location.move(2, 2))
    p.display.flip()


def draw_game_state(screen, gs, valid_moves, the_square):
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, the_square)
    draw_pieces(screen, gs.board)


def draw_board(screen):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            if board[r][c].piece:
                screen.blit(IMAGES[board[r][c].piece.nameAbv], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()
