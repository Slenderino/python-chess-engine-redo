import pygame
import os
import game
import piecesets
import json
import re

TEXT_COLOR = '#8E4A49'
BOARD_OUTLINE = '#5F464B'
BACKGROUND_COLOR = "#3a606e"
LIGHT_SQUARE = "#828E82"
DARK_SQUARE = "#607B7D"

# Initialization
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,30"
pygame.init()
pygame.font.init()

# Width and Height
WIDTH, HEIGHT = 1679, 970
F_WIDTH, F_HEIGHT = 1680, 1050

# Fps
FPS = 60

# Window
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Chess Engine Redo")

# Clock
clock = pygame.time.Clock()

if __name__ == "__main__":
    running = True
else:
    running = False


def render_text(content: str, font: str, size: int, color, surface, bold=False, italic=False, antialias=False,
                center_x=0, center_y=0, x=0, y=0):
    font = pygame.font.SysFont(font, size, bold)
    text = font.render(content, True, color)
    if center_x:
        textpos = text.get_rect(centerx=surface.get_width() / center_x + 1, y=y)
    elif center_y:
        textpos = text.get_rect(x=x, centery=surface.get_height() / center_y + 1)
    elif center_x and center_y:
        textpos = text.get_rect(centerx=surface.get_width() / (center_x + 1),
                                centery=surface.get_height() / (center_y + 1))
    else:
        textpos = text.get_rect(x=x, y=y)
    surface.blit(text, textpos)
    return text


fullscreen = False
square_size = 50

outline_width = square_size//6
board_surface = pygame.Surface((square_size * 8 + outline_width*2, square_size * 8 + outline_width*2), pygame.SRCALPHA)

def draw_board():
    for i in range(64):
        col = i % 8  # | | | | | | | |
        row = i // 8  # - - - - - - - -
        pygame.draw.rect(board_surface, (LIGHT_SQUARE if (col + row)%2 == 0 else DARK_SQUARE),
                         pygame.Rect(square_size*col+outline_width, square_size*row+outline_width, square_size, square_size))
    # Outline
    pygame.draw.rect(board_surface, BOARD_OUTLINE, pygame.Rect(0, 0, square_size * 8+ outline_width*2, square_size * 8 + outline_width*2), outline_width, 5)

def draw_board_pieces(piece_quality = 50):
    board = game.get_board()
    pieces = get_pieces_from_current_pieceset()
    for index, piece in enumerate(board):
        col = index % 8
        row = index // 8
        if piece == ' ':
            continue
        board_surface.blit(pieces[piece], (square_size*col+outline_width, square_size*row+outline_width))


def get_pieces_from_current_pieceset():
    with open(os.path.join("..", "data", "config.json"), 'r') as config_file:
        config_data = json.load(config_file)
        piece_set = config_data.get("piece_set")
    piece_files = piecesets.load_set(piece_set, scale=1)
    pieces = {}
    # Removes the first letter, classifying by the FEN notation the pieces
    for key, value in piece_files.items():
        new_key = key
        if key[0].lower() == 'b':
            new_key = new_key.lower()
        new_key = new_key[1:]
        pieces[new_key] = value
    return pieces


def draw_full_board():
    draw_board()
    draw_board_pieces()
    if not fullscreen:
        screen.blit(board_surface, (WIDTH/2-board_surface.get_width()/2, HEIGHT/2-board_surface.get_height()/2))
    else:
        screen.blit(board_surface, (F_WIDTH/2-board_surface.get_width()/2, F_HEIGHT/2-board_surface.get_height()/2))

game = game.Game()

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # From all events if user exits
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    # Debug fill
    screen.fill("purple")

    if fullscreen:
        width, height = F_WIDTH, F_HEIGHT
    else:
        width, height = WIDTH, HEIGHT

    pygame.draw.rect(screen, BACKGROUND_COLOR, (0, 0, width, height))

    render_text('Chess Engine Redo', "couriernew", 52, TEXT_COLOR, screen, bold=True, x=0, y=10)

    draw_full_board()

    # Fps tick and screen update
    fps = clock.tick(FPS)
    pygame.display.flip()

# When running == False
# quit pygame
pygame.quit()
