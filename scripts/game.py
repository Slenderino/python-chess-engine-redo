class Game:
    WHITE = 0b1000
    BLACK = 0b0000

    PAWN = 0b000
    KNIGHT = 0b001
    BISHOP = 0b010
    ROOK = 0b011
    QUEEN = 0b100
    KING = 0b101

    def __init__(self):
        self.board = Board()

    def get_board(self):
        return self.board.get_starting_fen()

    def get_color_to_play(self):
        return WHITE if self.board.side_to_move == 'w' else BLACK

    def get_piece_legal_moves(self, square):
        ...

class Square:
    FILES = " abcdefgh" # extra space at the start for making both file and rank start at one
    def __init__(self, pos):
        self.file = Square.FILES.index(pos[0]) # assign file a number instead of letter
        self.rank = int(pos[1])

    def get(self):
        return str(Square.FILES[self.file]+self.rank)

    def to_1dimensional_index(self):
        return self.file-1 + (8-self.rank)*8

class Piece:
    def __init__(self, piece: str | int):
        if type(piece) is str:
            self.fen_piece = piece
            self.engine_piece = fen_piece_to_engine_piece(piece)
        else:
            self.engine_piece = piece
            self.fen_piece = engine_piece_to_fen_piece(piece)

    @staticmethod
    def fen_piece_to_engine_piece(piece: str) -> int:
        if piece == " ": return None
        if piece.islower():
            # piece is black
            p_color = Game.BLACK
        else:
            p_color = Game.WHITE
        match piece.lower():
            case 'p':
                p_type = Game.PAWN
            case 'n':
                p_type = Game.KNIGHT
            case 'b':
                p_type = Game.BISHOP
            case 'r':
                p_type = Game.ROOK
            case 'q':
                p_type = Game.QUEEN
            case 'k':
                p_type = Game.KING
            case _:
                raise Exception("Invalid piece")

        return p_color | p_type

    @staticmethod
    def engine_piece_to_fen_piece(piece: int) -> str:
        if piece == " ": return None
        piece = bin(piece)[2:]
        piece_color = Game.WHITE if piece[0] else Game.BLACK
        pieces = 'pnbrqk'
        piece_index = int(piece[1:], 2)
        piece_type = pieces[piece_index]
        if piece_color == Game.WHITE:
            return piece_type.upper()
        return piece_type

class Board:
    def __init__(self, fen=None):
        if fen:
            self.fen = fen
        else:
            self.fen = self.get_starting_fen()
        self.array = self.get_array()
        dissected = self.fen.split()
        self.side_to_move = Game.WHITE if dissected[1] == 'w' else Game.BLACK
        self.castling_capabilities = None if dissected[2] == '-' else dissected[2]
        self.en_passant_square = None if dissected[3] == '-' else Square(dissected[3])
        self.hm_since_irreversible = None if dissected[4]== '-' else dissected[4]
        self.full_moves = None if dissected[5] == '-' else dissected[5]

    def get_starting_fen(self):
        return "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def get_array(self) -> list[str]:
        board = self.fen.split()[0]
        build = []
        for char in board:
            if char == '/':
                continue
            elif char.isdecimal():
                for _ in range(int(char)):
                    build.append(None)
            else:
                build.append(Piece(char))
        return build

    def get_square(self, square: Square):
        return self.array[square.to_1dimensional_index()]

    def get_file(self, file: str) -> list[int]:
        files = 'abcdefgh'
        file = files.index(file)
        array_indices = [n*8+file for n in range(8)]
        array_values = [self.array[i] for i in array_indices]
        return array_values

    def get_rank(self, rank: int):
        rank = 8-rank # 8th rank in chess is the top rank, counting from top to bottom means its the first rank
        return self.array[rank*8:rank*8+8]

class Move:
    def __init__(self, start_square: Square, end_square: Square, board: Board=None):
        self.start_square = start_square
        self.end_square = end_square
        self.engine_move = start_square.get() + end_square.get()
        if board:
            self.piece = board.get_square(start_square)
            self.is_capture = board.get_square(end_square) is not None
            piece_file = start_square.file
            board_file = board.get_file(piece_file)
            # Circular dependency with PieceMoves class, nedded for Standard Algebraic Notation disambiguation.


class PieceMoves:
    def pawn(self, board: Board, pos: Square):
        ...
        # Circular dependency with Move class, nedded for stroring and returning generated pseudo-legal moves.
