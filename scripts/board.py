SQUARE_SIZE = 100
LIGHT_SQUARE = "#828E82"
DARK_SQUARE = "#607B7D"

outline_width = SQUARE_SIZE//6
board_surface_size = (SQUARE_SIZE * 8 + outline_width*2, SQUARE_SIZE * 8 + outline_width*2)
def init_surface(pygame):
    board_surface = pygame.Surface(board_surface_size, pygame.SRCALPHA)
    return board_surface

def draw_board(pygame, board_surface, board_outline):
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


def get_baked_board_surface(pygame, board_outline, game, pieces, local_wh):
    local_width, local_height = local_wh
    board_surface = init_surface(pygame)
    draw_board(pygame, board_surface, board_outline)
    draw_board_pieces(game, board_surface, pieces)
    board_surface_dest = (local_width / 2 - board_surface.get_width() / 2, local_height / 2 - board_surface.get_height() / 2)
    board_rect = (board_surface_dest[0] + outline_width, board_surface_dest[1] + outline_width,
                  board_surface_size[0] - outline_width * 2, board_surface_size[1] - outline_width * 2)
    return board_surface, board_surface_dest