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
        return self.board.set_starter()
    def get_color_to_play(self):
        return WHITE if self.board.side_to_move == 'w' else BLACK
    def get_piece_legal_moves(self, square):

class Board:
    def __init__(self, fen=None):
        if fen == None:
            self = self.set_starter()
            return
        self.fen = fen
        dissected = self.fen.split
        self.side_to_move = dissected[1]
        self.castling_capabilities = None if dissected[2] == '-' else dissected[2]
        self.en_passant_square = None if dissected[3] == '-' else dissected[3]
        self.hm_since_irreversible = None if dissected[4]== '-' else dissected[4]
        self.full_moves = None if dissected[5] == '-' else dissected[5]

    def set_starter(self):
        self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.repr = Board._get_repr(self.fen)
        self.side_to_move = 'w'
        self.castling_capabilities = 'KQkq'
        self.en_passant_square = None
        self.hm_since_irreversible = 0
        self.full_moves = 1
        return self

    class SQUARE:
        def __init__(self, pos):
            self.file = pos[0]
            self.rank = int(pos[1])

    @staticmethod
    def _get_repr(fen) -> list[str]:
        board = fen.split()[0]
        build = []
        for char in board:
            if char == '/':
                continue
            elif char.isdecimal():
                for _ in range(int(char)):
                    build.append(" ")
            else:
                build.append(char)
        return build

class PieceMoves:
    def pawn(self, board, pos):
