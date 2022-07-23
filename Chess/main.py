#
# Title: Chess Project
# About:
# Author: Jayton Schmeeckle
#         jvschmeeckle@gmail.com
# Date:
#
import pygame as p
from Chess import Classes, ChessAI
import time

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for x in pieces:
        IMAGES[x] = p.transform.scale(p.image.load("images/" + x + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    load_images()

    player_white_human = False
    player_black_human = False
    running = True
    selected_square = ()
    selected_squares = []

    gs = Classes.GameState()
    valid_moves = gs.get_valid_moves(gs.player_moving, gs.player_waiting)
    move_made = False  # flag to check valid moves
    print("\n------ " + gs.player_moving.color.name + "'s Turn! ------\n")

    # Run the game
    while running:

        is_human_turn = (gs.player_moving.color == Classes.Color.White and player_white_human) or \
                        (gs.player_moving.color == Classes.Color.Black and player_black_human)

        # When the player makes an action with mouse or keyboard
        for e in p.event.get():
            if is_human_turn and len(valid_moves) >= 1:
                if e.type == p.QUIT:
                    running = False

                # Mouse Handlers
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()  # x,y pos. mouse
                    column = location[0] // SQ_SIZE  # x pos
                    row = location[1] // SQ_SIZE  # y pos

                    if selected_square == (row, column):  # same square selected then reset
                        selected_square = ()
                        selected_squares = []
                    else:
                        selected_square = (row, column)
                        selected_squares.append(selected_square)

                    if len(selected_squares) == 2:
                        move = Classes.Move(gs.board.grid[selected_squares[0][0]][selected_squares[0][1]],gs.board.grid[selected_squares[1][0]][selected_squares[1][1]], gs.board)
                        if move in valid_moves:
                            the_move = valid_moves[valid_moves.index(move)]
                            gs.make_move(the_move)
                            move_made = True
                            selected_square = ()
                            selected_squares = []
                            if move_made:
                                print(move.get_chess_notation())
                                move.pieceMoved.has_moved = True
                                if gs.can_promote_pawn(move):
                                    draw_game_state(screen, gs)
                                    clock.tick(MAX_FPS)
                                    p.display.flip()
                                    gs.promote_pawn(gs.player_moving, move, False)
                        else:
                            selected_squares = [selected_square]

                # Key Handlers
                elif e.type == p.KEYDOWN:
                    if e.key == p.K_z:
                        gs.undo_move()
                        move_made = True
        # Ai Moves
        if not is_human_turn and len(valid_moves) >= 1:
            ai_move = ChessAI.get_random_move(valid_moves)
            #time.sleep(.09)
            gs.make_move(ai_move)
            move_made = True
            ai_move.pieceMoved.has_moved = True
            if gs.can_promote_pawn(ai_move):
                draw_game_state(screen, gs)
                clock.tick(MAX_FPS)
                p.display.flip()
                gs.promote_pawn(gs.player_moving, ai_move, True)

        # handle post move
        if move_made:
            gs.toggle_turn()
            valid_moves = gs.get_valid_moves(gs.player_moving, gs.player_waiting)
            print("===========================\n")
            print("------ " + gs.player_moving.color.name + "'s Turn! ------\n")
            if gs.is_in_check(gs.player_moving, gs.player_waiting):
                print(gs.player_moving.color.name + " is in Check!")
            move_made = False

        # update gui
        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def draw_game_state(screen, gs):
    draw_board(screen)
    draw_pieces(screen, gs.board)


def draw_board(screen):
    colors = [p.Color("white"), p.Color("grey")]

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            if board.grid[r][c].piece:
                screen.blit(IMAGES[board.grid[r][c].piece.nameAbv],
                            p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()
