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
    def __init__(self, pos: str):
        self.file = Square.FILES.index(pos[0]) # assign file a number instead of letter
        self.rank = int(pos[1])

    def get(self):
        return str(Square.FILES[self.file]+self.rank)

    def get_offset(self, offset: tuple[int, int]):
        return Square(Square.FILES[self.file+offset[0]]+(self.rank+offset[1]))

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
        self.color = Game.WHITE if bin(self.engine_piece)[2] else Game.BLACK

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

    def get_starting_fen(self) -> str:
        return "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def get_array(self) -> list[Piece | None]:
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

    def get_square(self, square: Square) ->  Piece | None:
        return self.array[square.to_1dimensional_index()]

    def get_file(self, file: str) -> list[Piece | None]:
        files = 'abcdefgh'
        file = files.index(file)
        array_indices = [n*8+file for n in range(8)]
        array_values = [self.array[i] for i in array_indices]
        return array_values

    def get_rank(self, rank: int) -> list[Piece | None]:
        rank = 8-rank # 8th rank in chess is the top rank, counting from top to bottom means its the first rank
        return self.array[rank*8:rank*8+8]

class Move:
    def __init__(self, start_square: Square, end_square: Square, promotion: Piece | None=None, board: Board=None):
        self.start_square = start_square
        self.end_square = end_square
        self.engine_move = start_square.get() + end_square.get()
        if board:
            # Support SAN format too!
            self.piece = board.get_square(start_square)
            self.is_capture = board.get_square(end_square) is not None
            board_file = board.get_file(start_square.file)
            PieceMoves.disambiguate_for(self)


class PieceMoves:
    @staticmethod
    def pawn(board: Board, pos: Square) -> list[Move]:
        # Error checking
        if pos.rank in [1, 8]: raise Exception("Pawn in first/last rank, impossible")

        moves = []
        pawn = board.get_square(pos)
        enemy_color = abs(Game.WHITE-pawn.color)
        forward = pos.get_offset((0, 1)) if pawn.color == Game.WHITE else pos.get_offset((0, -1))
        left_capture = pos.get_offset((-1, 1)) if pawn.color == Game.WHITE else pos.get_offset((-1, -1))
        right_capture = pos.get_offset((1, 1)) if pawn.color == Game.WHITE else pos.get_offset((1, -1))
        double_forward = pos.get_offset((0, 2)) if pawn.color == Game.WHITE else pos.get_offset((0, -2))
        promoting = forward.rank in [1, 8]
        promotable = [Game.KNIGHT, Game.BISHOP, Game.ROOK, Game.QUEEN,]
        if promoting:
            if not board.get_square(forward):
                for piece in promotable:
                    moves.append(Move(pos, forward, Piece(piece), board))
            if pos.file != 1:
                # Not in A file, check diagonal left capture
                if board.get_square(left_capture) and board.get_square(left_capture).color == enemy_color:
                    for piece in promotable:
                        moves.append(Move(pos, left_capture, Piece(piece), board))
            if pos.file != 8:
                # Not in H file, check diagonal right capture
                if board.get_square(right_capture) and board.get_square(right_capture).color == enemy_color:
                    for piece in promotable:
                        moves.append(Move(pos, right_capture, Piece(piece), board))
        # Double move and en passant skipped when promoting,
        # such situations are imposible to happen in any chess position
        else:
            if not board.get_square(forward):
                # Ahead clear
                moves.append(Move(pos, forward, board=board))
            if pos.file != 1:
                # Not in A file, check diagonal left capture
                if board.get_square(left_capture) and board.get_square(left_capture).color == enemy_color:
                    moves.append(Move(pos, left_capture, board=board))
            if pos.file != 8:
                # Not in H file, check diagonal right capture
                if board.get_square(right_capture) and board.get_square(right_capture).color == enemy_color:
                    moves.append(Move(pos, right_capture, board=board))
            if (pos.rank == 2 and pawn.color == Game.WHITE) or (pos.rank == 7 and pawn.color == Game.BLACK):
                if not board.get_square(double_forward) and not board.get_square(forward):
                    # Checks both final and intermediate square
                    moves.append(Move(pos, double_forward, board=board))
            if board.en_passant_square in [left_capture, right_capture]:
                if board.get_square(board.en_passant_square.get_offset((0,-1) if pawn.color == Game.WHITE else (0, 1))).color == enemy_color:
                    # En passant is possible in FEN and that the pawn en_passant references is of the opposite color
                    # (offset because pawn is in the square after the mentioned one in the FEN)
                    moves.append(Move(pos, board.en_passant_square, board=board))
        return moves

