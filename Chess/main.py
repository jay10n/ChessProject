#
import pygame as p
from Chess import Classes

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
    gs = Classes.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False  # flag to check valid moves
    load_images()
    running = True
    selected_square = ()
    player_clicks = []

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # Mouse Handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # x,y pos. mouse
                column = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if selected_square == (row, column):  # same square selected
                    selected_square = ()  # reset
                    player_clicks = []
                else:
                    selected_square = (row, column)
                    player_clicks.append(selected_square)
                if len(player_clicks) == 2:
                    move = Classes.Move(player_clicks[0], player_clicks[1], gs.board)
                    if move in valid_moves:
                        gs.make_move(move)
                        # print(move.get_chess_notation())
                        move_made = True
                    selected_square = ()
                    player_clicks = []

            # Key Handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undo_move()
                    move_made = True

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

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
            if board[r][c].piece:
                screen.blit(IMAGES[board[r][c].piece.nameAbv], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()
