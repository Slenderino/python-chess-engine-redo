import pygame
import os
import game
import piecesets
import json

TEXT_COLOR = '#FFFFFF'
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
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SRCALPHA)
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

def get_text_properties(content: str, font: str, size: int, color=(0, 0, 0, 0), bold=False):
    font = pygame.font.SysFont(font, size, bold)
    text = font.render(content, True, color)
    return text


fullscreen = False
square_size = 100

outline_width = square_size//6
board_surface_size = (square_size * 8 + outline_width*2, square_size * 8 + outline_width*2)
board_surface = pygame.Surface(board_surface_size, pygame.SRCALPHA)

def draw_board():
    for i in range(64):
        col = i % 8  # | | | | | | | |
        row = i // 8  # - - - - - - - -
        # Se calcula el color de la casilla en base a la regla de que si la fila y columna sumadas son pares entonces la casilla es blanca
        pygame.draw.rect(board_surface, (LIGHT_SQUARE if (col + row)%2 == 0 else DARK_SQUARE),
                         # Se dibuja la casilla, en su columna y fila correspondiente, ajustada al outline
                         pygame.Rect(square_size*col+outline_width, square_size*row+outline_width, square_size, square_size))
    # Outline
    pygame.draw.rect(board_surface, BOARD_OUTLINE, pygame.Rect(0, 0, square_size * 8+ outline_width*2, square_size * 8 + outline_width*2), outline_width, 5)

def draw_board_pieces(game):
    global pieces
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
            board_surface.blit(pieces[char], (outline_width+square_size*col, outline_width+square_size*row))
            col+=1

def get_current_pieceset():
    global piece_set
    # config.json almacena el pieceset actual
    with open(os.path.join("..", "data", "config.json"), 'r') as config_file:
        config_data = json.load(config_file)
        piece_set = config_data.get("piece_set")
    return piece_set

def get_pieces_from_current_pieceset():
    piece_set = get_current_pieceset()
    piece_sizes = {
        'alpha': (2048, 2048),
        'cburnett': (45, 45),
        'mpchess': (38, 38),
        'pixel': (16, 16),
        'tatiana': (189, 189)
        }  # Las dimensiones de los svg's
    piece_files: dict[str: pygame.Surface] = piecesets.load_set(piece_set, dpi=300)
    surfaces = {}
    # Removes the first letter, classifying by the FEN notation the pieces
    for key, value in piece_files.items():
        new_key = key
        if key[0].lower() == 'b':  # De ser negra la pieza se convierte a minúscula
            new_key = new_key.lower()
        new_key = new_key[1:]  # Quitar el color a la pieza, puesto a que lo define si está en mayúscula o no

        # Ajustar dimensiones por pieceset
        if piece_set == 'alpha': value = pygame.transform.scale_by(value, 0.05)
        elif piece_set == 'cburnett': value = pygame.transform.scale_by(value, 2.15)
        elif piece_set == 'mpchess': value = pygame.transform.scale_by(value, 0.82)
        elif piece_set == 'pixel': value = pygame.transform.scale_by(value, 6)
        elif piece_set == 'tatiana': value = pygame.transform.scale_by(value, 0.17)
        surfaces[new_key] = value
    return surfaces

def set_pieceset(name):
    if name not in piecesets.list_sets().keys():  raise Exception('pieceset not found')  # Si no se encuentra el pieceset dentro de los disponibles
    with open(os.path.join("..", "data", "config.json"), 'w') as config_file:
        json.dump({"piece_set": str(name)}, config_file)

def draw_full_board(local_width, local_height, game):
    global board_rect
    draw_board()
    draw_board_pieces(game)
    board_surface_dest = (local_width / 2 - board_surface.get_width() / 2, local_height / 2 - board_surface.get_height() / 2)
    board_rect = (board_surface_dest[0]+outline_width, board_surface_dest[1]+outline_width, board_surface_size[0]-outline_width*2, board_surface_size[1]-outline_width*2)
    screen.blit(board_surface, board_surface_dest)



def reload_pieces():
    global pieces

    # Draw message box while loading
    pygame.draw.rect(screen, 'teal', pygame.Rect(((WIDTH - 750) / 2), ((HEIGHT - 150) / 2) - 40, 750, 150))

    # Getting width and height for the text, allowing it to be centered
    text_width_height = get_text_properties('Please wait while the pieceset is loading.\nThis wait time varies heavily on the pieceset,\nbut it should take no longer than 5 seconds.',
                'couriernew', 25, (0, 0, 0, 0)).get_size()
    render_text(
        'Please wait while the pieceset is loading.\nThis wait time varies heavily on the pieceset,\nbut it should take no longer than 5 seconds.',
        'couriernew',
        25,
        'black',
        screen, x=WIDTH//2-text_width_height[0]//2, y=HEIGHT//2-text_width_height[1]//2-40) # Centering the text, with a y offset
    pygame.display.flip()
    pieces = get_pieces_from_current_pieceset()

game = game.Game()
reload_pieces()

piece_set = get_current_pieceset()

right_gui_surface = pygame.Surface((400, 832), pygame.SRCALPHA)

mouse_on_pieceset_selection = False
open_dropdown = False
mouse_on_dropdown_name = None
pieceset_selection_button_rect = (0, 0, 0, 0)
piecesets_dropdown = {}

board_rect = (0, 0, 0, 0)
draw_full_board(WIDTH, HEIGHT, game)

game_overlay_surface = pygame.Surface((board_rect[2], board_rect[3]), pygame.SRCALPHA)

def draw_right_gui():
    global pieceset_selection_button_rect
    #Dibujar el outline
    pygame.draw.rect(right_gui_surface, BOARD_OUTLINE, ((0, 0), right_gui_surface.get_size()), border_radius=5)

    # Obtener el tamaño del texto "Piece Set:", para poder centrarlo con respecto a la superficie
    piece_set_text_width_height = get_text_properties('Piece Set:', 'couriernew', 24, bold=True).get_size()
    render_text('Piece Set:', 'couriernew', 24, TEXT_COLOR, right_gui_surface, True,
                x=piece_set_text_width_height[0]//5,  # x es la anchura del texto dividido en 5,
                y=piece_set_text_width_height[1])  # y es la altura del texto, lo que significa que cabe exactamente un texto entre el inicio de este y el borde de arriba

    # Renderizar el rect que va a contener el texto del pieceset actual y guardar su rect
    selection_rect = pygame.draw.rect(right_gui_surface, '#663521', (piece_set_text_width_height[0]*1.4, piece_set_text_width_height[1], 123, 24)
                                      , border_radius=2) #                     se basa de la anchura del texto y  | misma altura que el texto    | el 123 es la anchura del texto más  | altura del texto
    #                                                                          la multiplica para distanciarse                                    largo más 10, 5 de espaciado por lado

    # Renderizar el texto del pieceset actual
    render_text(piece_set, 'couriernew', 24, TEXT_COLOR, right_gui_surface, True,
                x=piece_set_text_width_height[0]*1.4+5, # el offset del rect + 5 de espaciado para centrar el texto dentro del rect
                y=piece_set_text_width_height[1]).get_width() # la altura del rect


    # Establecemos el rect del botón que va a abrir el menú dropdown en una variable aparte, esto para que en el main loop se pueda verificar si el mouse se encuentra adentro o no
    pieceset_selection_button_rect = (piece_set_text_width_height[0]*1.4+selection_rect.width, piece_set_text_width_height[1], 24, 24)

    # Dibujamos el rect del botón, con el color dependiendo de si tiene el mouse encima o no
    pygame.draw.rect(right_gui_surface, ('#5b2723' if mouse_on_pieceset_selection else '#663521'), pieceset_selection_button_rect, border_radius=2)

    # Dibujamos el triángulo para abajo con coordenadas relativas a al botón
    pygame.draw.polygon(right_gui_surface, TEXT_COLOR, ((pieceset_selection_button_rect[0]+pieceset_selection_button_rect[2]/3, pieceset_selection_button_rect[1]+pieceset_selection_button_rect[3]/3),
                                                        (pieceset_selection_button_rect[0]+pieceset_selection_button_rect[2]/3*2, pieceset_selection_button_rect[1]+pieceset_selection_button_rect[3]/3),
                                                        (pieceset_selection_button_rect[0]+pieceset_selection_button_rect[2]/2, pieceset_selection_button_rect[1]+pieceset_selection_button_rect[3]/3*2)))

    if open_dropdown: handle_piecesets_dropdown()

    # Finalmente, dibujamos la superficie a la pantalla, con un offset que la dejará siempre al costado del tablero
    screen.blit(right_gui_surface, (current_width - 410, (70 + current_height - 900) / 2))

def handle_piecesets_dropdown():
    piecesets_list = piecesets.list_sets().keys()
    piece_set_text_width_height = get_text_properties('Piece Set:', 'couriernew', 24, bold=True).get_size()
    for idx, pieceset in enumerate(piecesets_list):
        pieceset_rect = (
            piece_set_text_width_height[0]*1.4,  # Same x for every rect
            (piece_set_text_width_height[1]-3)*(2+idx)-(3*idx),  # Adding 24 for every pieceset
            123, 24  # Final width and height
        )
        if mouse_on_dropdown_name:
            current_dropdown = mouse_on_dropdown_name
        else:
            current_dropdown = None
        piecesets_dropdown[pieceset] = pieceset_rect
        pygame.draw.rect(right_gui_surface, '#5b2723' if current_dropdown == pieceset else '#663521', pieceset_rect, border_radius=5)
        render_text(pieceset, 'couriernew', 24, TEXT_COLOR, right_gui_surface, True, x=pieceset_rect[0]+5, y=pieceset_rect[1])


def handle_mouse_detection():
    global mouse_on_pieceset_selection, mouse_on_dropdown_name
    mouse_pos = pygame.mouse.get_pos()
    right_gui_surface_dest = (current_width - 410, (70 + current_height - 900) / 2)
    pieceset_selection_button_rect_coords = (pieceset_selection_button_rect[0] + right_gui_surface_dest[0],  # Relative coords + offset = absolute coords
                                             pieceset_selection_button_rect[1] + right_gui_surface_dest[1],  # Relativa coords + offset = absolute coords
                                             pieceset_selection_button_rect[2],  # width
                                             pieceset_selection_button_rect[3]  # height
                                             )
    mouse_on_pieceset_selection = is_mouse_on_rect(pieceset_selection_button_rect_coords)
    clear = True
    for option, rect in piecesets_dropdown.items():
        if is_mouse_on_rect(rect, right_gui_surface_dest):
            mouse_on_dropdown_name = option
            clear = False
            break
    if clear: mouse_on_dropdown_name = None

def is_mouse_on_rect(rect: pygame.Rect | tuple[float, float, float, float], offset: None | tuple[float, float]=None) -> bool:
    if isinstance(rect, pygame.Rect):
        return rect.collidepoint(pygame.mouse.get_pos())

    x, y, width, height = rect
    if offset:
        x+= offset[0]
        y+= offset[1]
    mx, my = pygame.mouse.get_pos()
    return x <= mx <= x + width and y <= my <= y + height


# Main loop
while running:
    global current_width, current_height
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # From all events if user exits
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen  # Invert fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            elif event.key == pygame.K_r:
                # Reload pieces
                reload_pieces()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if mouse_on_pieceset_selection:
                open_dropdown = not open_dropdown
            elif open_dropdown and mouse_on_dropdown_name:
                open_dropdown = False
                set_pieceset(mouse_on_dropdown_name)
                reload_pieces()

    # Debug fill
    screen.fill("purple")


    if fullscreen:
        current_width, current_height = F_WIDTH, F_HEIGHT
    else:
        current_width, current_height = WIDTH, HEIGHT

    handle_mouse_detection()

    pygame.draw.rect(screen, BACKGROUND_COLOR, (0, 0, current_width, current_height))

    render_text('Chess Engine Redo', "couriernew", 52, TEXT_COLOR, screen, bold=True, x=0, y=10)

    draw_full_board(current_width, current_height, game)

    screen.blit(game_overlay_surface, (board_rect[0], board_rect[1]))

    draw_right_gui()

    # Fps tick and screen update
    fps = clock.tick(FPS)
    pygame.display.flip()

# When running == False
# quit pygame
pygame.quit()
