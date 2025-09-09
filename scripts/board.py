import pygame

SQUARE_SIZE = 100
LIGHT_SQUARE = "#828E82"
DARK_SQUARE = "#607B7D"

outline_width = SQUARE_SIZE//6
board_surface_size = (SQUARE_SIZE * 8 + outline_width*2, SQUARE_SIZE * 8 + outline_width*2)


def init_surface():
    board_surface = pygame.Surface(board_surface_size, pygame.SRCALPHA)
    return board_surface

def draw_board(board_surface, board_outline):
    """
    Draws the board squares on the given surface.
    :param board_surface: Surface to draw on the squares.
    :param board_outline: The thickness of the board outline.
    :return:
    """
    for i in range(64):
        col = i % 8  # | | | | | | | |
        row = i // 8  # - - - - - - - -
        # Se calcula el color de la casilla en base a la regla de que si la fila y columna sumadas son pares entonces la casilla es blanca
        pygame.draw.rect(board_surface, (LIGHT_SQUARE if (col + row)%2 == 0 else DARK_SQUARE),
                         # Se dibuja la casilla, en su columna y fila correspondiente, ajustada al outline
                         pygame.Rect(SQUARE_SIZE*col+outline_width, SQUARE_SIZE*row+outline_width, SQUARE_SIZE, SQUARE_SIZE))
    # Outline
    pygame.draw.rect(board_surface, board_outline, pygame.Rect(0, 0, SQUARE_SIZE * 8 + outline_width * 2, SQUARE_SIZE * 8 + outline_width * 2), outline_width, 5)

def draw_board_pieces(game, board_surface, pieces):
    """
    Draws the specified chess pieces from current position in game onto the given surface.
    :param game: Game from where to get the position.
    :param board_surface: Surface to draw on the pieces.
    :param pieces: Pieceset to use.
    :return:
    """
    state = game.get_board().fen
    board = state.split()[0]
    # Board contiene el estado del tablero actual
    col = 0
    row = 0
    for char in board:
        if char == '/':
            row+=1
            col=0
        elif char.isdecimal():
            col+=int(char)
        else:
            row+=col//8
            col=col%8
            board_surface.blit(pieces[char], (outline_width+SQUARE_SIZE*col, outline_width+SQUARE_SIZE*row))
            col+=1


def get_baked_board_surface(board_outline, game, pieces, local_width_height):
    """
    A function designed to instantiate and do all the processing needed for a frame of the board surface
    :param board_outline: The outline thickness, in px
    :param game: Game containing current position for the drawing of the pieces
    :param pieces: Current selected pieceset
    :param local_width_height: Current dimensions of the window
    :return: The processed board surface and where to draw it.
    """
    local_width, local_height = local_width_height
    board_surface = init_surface()
    board_surface_dest = (local_width / 2 - board_surface.get_width() / 2, local_height / 2 - board_surface.get_height() / 2)  # center the board surface
    board_rect = (board_surface_dest[0] + outline_width, board_surface_dest[1] + outline_width,
                  board_surface_size[0] - outline_width * 2, board_surface_size[1] - outline_width * 2)  # gets the usable board rect

    draw_board(board_surface, board_outline)
    draw_board_pieces(game, board_surface, pieces)
    update(board_rect, board_surface)
    return board_surface, board_surface_dest


def update(board_rect, board_surface):
    """
    Overlays and logic management for the interactable board.
    :param board_rect: The delimiters of the usable board in contrast with the board entire surface
    :param board_surface: The surface on which to apply the changes
    :return:
    """
    # get relative mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_x -= board_rect[0]
    mouse_y -= board_rect[1]

    # check mouse inside board
    if not (0 < mouse_x < board_rect[2] and 0 < mouse_y < board_rect[3]):
        # mouse outside
        return

    # get mouse file and rank
    mouse_file, mouse_rank = mouse_x // SQUARE_SIZE, mouse_y // SQUARE_SIZE

    overlay_surface = pygame.Surface((board_rect[2], board_rect[3]), pygame.SRCALPHA)

    #higligh mouse square
    pygame.draw.rect(overlay_surface, (20, 20, 20, 50), (mouse_file * SQUARE_SIZE, mouse_rank * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    board_surface.blit(overlay_surface, (outline_width, outline_width))