from __future__ import annotations
from operator import countOf

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

    def get_board(self) -> str:
        return self.board.get_starting_fen()

    def get_color_to_play(self) -> int:
        return WHITE if self.board.side_to_move == 'w' else BLACK

class Square:
    FILES = " abcdefgh" # extra space at the start for making both file and rank start at one
    def __init__(self, pos: str):
        self.file = Square.FILES.index(pos[0]) # assign file a number instead of letter
        self.rank = int(pos[1])

    def get(self) -> str:
        return str(Square.FILES[self.file])+str(self.rank)

    def get_offset(self, offset: tuple[int, int]) -> Square:
        if not (1 <= self.file+offset[0] <= 8 and 1 <= self.rank+offset[1] <= 8): return None # outside bounds
        return Square(Square.FILES[self.file+offset[0]]+str(self.rank+offset[1]))

    def to_1dimensional_index(self) -> int:
        return self.file-1 + (8-self.rank)*8

    def get_file(self) -> str:
        return str(Square.FILES[self.file])

    @staticmethod
    def all_squares() -> list[Square]:
        # in order to compy with the rest of the ordering in the engine,
        # we must start at a8 and finisgh in h1
        files = Square.FILES[1:]
        ranks = range(1, 9)[::-1]
        squares = []
        for rank in ranks:
            for file in files:
                squares.append(Square(file+str(rank)))
        return squares


class Piece:
    def __init__(self, piece: str | int):
        if type(piece) is str:
            self.fen_piece = piece
            self.engine_piece = self.fen_piece_to_engine_piece(piece)
        else:
            self.engine_piece = piece
            self.fen_piece = self.engine_piece_to_fen_piece(piece)
        self.color = Game.WHITE if format(self.engine_piece, '04b')[0] == '1' else Game.BLACK
        self.engine_type = int(format(self.engine_piece, '04b')[1:], 2)

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
        piece_index = int(piece[1:], 2) # cutoff piece engine color
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
        self.castling_capabilities: None | str = None if dissected[2] == '-' else dissected[2]
        self.en_passant_squares = None if dissected[3] == '-' else Square(dissected[3])
        self.hm_since_irreversible = None if dissected[4]== '-' else int(dissected[4])
        self.full_moves = None if dissected[5] == '-' else int(dissected[5])

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

    def get_file(self, file: str | int) -> list[Piece | None]:
        if type(file) is str:
            files = 'abcdefgh'
            file = files.index(file)
        else:
            file = file-1
        array_indices = [n*8+file for n in range(8)]
        array_values = [self.array[i] for i in array_indices]
        return array_values

    def get_rank(self, rank: int) -> list[Piece | None]:
        rank = 8-rank # 8th rank in chess is the top rank, counting from top to bottom means its the first rank
        return self.array[rank*8:rank*8+8]

    def is_square_being_attacked_by_color(self, square: Square, color: int) -> bool:
        files = "abcdefgh"
        ranks = range(1, 9)
        # loop all squares
        squares = Square.all_squares()
        for current_square in squares:
            # for each square in board
            if self.get_square(current_square):
                if self.get_square(current_square).color == color:
                    # target square has a piece of the correct color to check
                    for move in PieceMoves.generate_moves(self, current_square, True):
                        # for each possible move with that piece, if that move target end square matches, color controls square
                        # skipping pawn advances, as they do not control those squares
                        if move.end_square == square and not move.is_not_controlling: return True
        return False

    def instances_of_piece(self, piece: Piece) -> list[Square]:
        instances = []
        for square in Square.all_squares():
            if self.get_square(square):
                if self.get_square(square).fen_piece == piece.fen_piece:
                    instances.append(square)
        return instances

    def pieces_mask(self, color: int) -> list[bool]:
        mask = []
        for square in Square.all_squares():
            if self.get_square(square):
                if self.get_square(square).color == color:
                    mask.append(True)
                    continue
            mask.append(False)
        return mask

    def generate_legal_moves(self) -> list[Move]:
        pseudo_legal_moves = []
        legal_moves = []
        color = self.side_to_move
        mask = self.pieces_mask(color)
        for square in Square.all_squares():
            if mask[square.to_1dimensional_index()]: # little optimization to only look at squares with own pieces
                pseudo_legal_moves += PieceMoves.generate_moves(self, square)

        for move in pseudo_legal_moves:
            new_board = self.branch_move(move)

            #check king square after moving, in case of a king move
            own_king = new_board.instances_of_piece(Piece(Game.KING | color))
            # error checking
            if len(own_king) != 1:
                raise Exception(f"Invalid position, more or less than one {"white" if color == Game.WHITE else "black"} king.\nFEN:\n{new_board.fen}"+
                                f"\n{Piece(Game.KING | color)}")

            king_square = own_king[0]
            if not new_board.is_square_being_attacked_by_color(king_square, Game.WHITE-color): # color inverse
                legal_moves.append(move)
        return legal_moves

    def branch_move(self, move) -> Board:
        piece_moving = self.get_square(move.start_square)
        potential_piece_captured = self.get_square(move.end_square)
        new_board = self.array.copy()
        new_board[move.start_square.to_1dimensional_index()] = None # lift piece

        promoting = piece_moving.engine_type == Game.PAWN and (move.end_square.rank == 1 or move.end_square.rank == 8)
        if promoting:
            new_board[move.end_square.to_1dimensional_index()] = move.promotion # place down promotion piece
        else:
            new_board[move.end_square.to_1dimensional_index()] = piece_moving # place down original piece (possible capture)
        if move.is_en_passant:
            # obliterate pawn from up/down depending on color
            new_board[move.end_square.get_offset((0, -1) if piece_moving.color == Game.WHITE else (0, 1))] = None
        castling = piece_moving.engine_type == Game.KING and abs(move.start_square.file - move.end_square.file) == 2
        if castling:
            # if kingside
            if move.end_square.file == 7:
                new_board[move.end_square.get_offset((1, 0)).to_1dimensional_index()] = None # lift kingside rook
                new_board[move.start_square.get_offset((1, 0)).to_1dimensional_index()] = piece_moving.color | Game.ROOK # place kingside rook
            else: # move.end_square.file should be 3
                new_board[move.end_square.get_offset((-2, 0)).to_1dimensional_index()] = None # lift queenside rook
                new_board[move.start_square.get_offset((-1, 0)).to_1dimensional_index()] = piece_moving.color | Game.ROOK # place queenside rook

        # parse board
        new_fen = Board.array_to_fen(new_board)

        # toggle color to move
        new_side_to_move = 'b' if self.side_to_move == Game.WHITE else 'w'

        # castling rights
        new_castling_rights = self.castling_capabilities
        if self.castling_capabilities:
            if piece_moving.engine_type == Game.KING:
                # king moved, remove both castlings
                new_castling_rights = new_castling_rights.replace('K' if piece_moving.color == Game.WHITE else 'k', '')
                new_castling_rights = new_castling_rights.replace('Q' if piece_moving.color == Game.WHITE else 'q', '')
            else:
                if 'k' in new_castling_rights:
                    if move.end_square == Square('h8') or move.start_square == Square('h8'): # king rook square
                        # king rook captured or moved
                        new_castling_rights = new_castling_rights.replace('k', '')
                if 'K' in new_castling_rights:
                    if move.end_square == Square('h1') or move.start_square == Square('h1'): # king rook square
                        # king rook captured or moved
                        new_castling_rights = new_castling_rights.replace('K', '')
                if 'q' in new_castling_rights:
                    if move.end_square == Square('a8') or move.start_square == Square('a8'): # queen rook square
                        # queen rook captured or moved
                        new_castling_rights = new_castling_rights.replace('q', '')
                if 'Q' in new_castling_rights:
                    if move.end_square == Square('a1') or move.start_square == Square('a1'): # queen rook square
                        # queen rook captured or moved
                        new_castling_rights = new_castling_rights.replace('Q', '')
        if new_castling_rights == "": new_castling_rights = "-"

        # en passant squares
        new_en_passant = '-'
        left_square = move.end_square.get_offset((-1, 0))
        right_square = move.start_square.get_offset((1, 0))
        left_piece = self.get_square(left_square) if left_square else None
        right_piece = self.get_square(right_square) if right_square else None
        is_pawn_double_push = piece_moving.engine_type == Game.PAWN and ((move.start_square.rank == 2 and move.end_square.rank == 4) or (move.start_square.rank == 7 and move.end_square.rank == 5))
        if is_pawn_double_push:
            if left_piece:
                if left_piece.color != piece_moving.color and left_piece.engine_piece == Game.PAWN:
                    # enemy color pawn
                    # set en_passant square from color
                    new_en_passant = move.start_square.get_offset((0, -1)).get() if piece_moving.color == Game.BLACK else move.start_square.get_offset((0, 1)).get()
            # separate if statements to avoid AttributeError
            elif right_piece: # elif because either of them work, skips redundant reasignation
                if right_piece.color != piece_moving.color and right_piece.engine_piece == Game.PAWN:
                    # enemy color pawn
                    new_en_passant = move.start_square.get_offset((0, -1)).get() if piece_moving.color == Game.BLACK else move.start_square.get_offset((0, 1)).get()

        # irreversible half-move clock
        new_hm_since_irreversible = self.hm_since_irreversible + 1
        # reset if pawn move or capture
        if self.get_square(move.start_square).engine_piece == Game.PAWN or potential_piece_captured:
            new_hm_since_irreversible = 0

        # full move counter
        new_full_moves = self.full_moves
        # increment on black's move
        if piece_moving.color == Game.BLACK:
            new_full_moves += 1

        return Board(" ".join(
            [new_fen, new_side_to_move, new_castling_rights, new_en_passant, str(new_hm_since_irreversible), str(new_full_moves)]))



    @staticmethod
    def array_to_fen(array: list["Piece | None"]) -> str:
        fen = ""
        for index, piece in enumerate(array):
            if index != 0 and index % 8 == 0:
                fen += "/"  # rank separator
            if piece:
                fen += piece.fen_piece
            else:
                fen += "1"

        # merge consecutive 1s into their count
        compressed = ""
        count = 0
        for char in fen:
            if char == "1":
                count += 1
            else:
                if count > 0:
                    compressed += str(count)
                    count = 0
                compressed += char
        if count > 0:  # flush trailing 1s
            compressed += str(count)

        return compressed

class Move:
    def __init__(self, start_square: Square, end_square: Square, promotion: Piece | None=None, is_en_passant: bool = False, is_not_controlling: bool = False, board: Board=None):
        self.start_square = start_square
        self.end_square: Square = end_square
        self.engine_move = start_square.get() + end_square.get()
        self.promotion = promotion
        self.is_en_passant = is_en_passant
        self.is_not_controlling = is_not_controlling # pawn moves
        if board:
            self.current_board = board
            self.piece = board.get_square(start_square)
            self.is_capture = board.get_square(end_square) is not None

    def generate_san(self) -> str:
        if self.piece.engine_type == Game.PAWN:
            if self.start_square.file == self.end_square.file:
                # normal movement (e4)
                self.san = self.end_square.get()
            else:
                # capture (exd5)
                self.san = self.start_square.get_file() + "x" + self.end_square.get()
        else:
            # setting first letter of the san to be the piece
            self.san = self.piece.fen_piece.upper()
            # add disambiguation after piece type
            self.san += PieceMoves.disambiguate_for(self)
            # if capture indicate so
            if self.is_capture: self.san += 'x'
            # finally, end square
            self.san += self.end_square.get()
        return self.san


class PieceMoves:
    @staticmethod
    def disambiguate_for(move: Move) -> str:
        colliding_moves = []
        for m in move.current_board.generate_legal_moves():
            if m.end_square == move.end_square and m.piece == move.piece and m.start_square != move.start_square:
                # uh-oh, must disambiguate, both moves would come to the same san
                colliding_moves.append(m)
        if len(colliding_moves) == 0: return ''# early return

        rank_collision = any(m.start_square.rank == move.start_square.rank for m in colliding_moves)
        file_collision = any(m.start_square.file == move.start_square.file for m in colliding_moves)

        if rank_collision and file_collision:
            # double disambiguation
            return move.start_square.get()
        elif file_collision:
            # rank disambiguation
            return str(move.start_square.rank)
        # if only ranks collide or not rank nor file collide, use file
        return move.start_square.get_file()

    # TODO: write perft function (https://www.chessprogramming.org/Perft)

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
        promotable = [Game.KNIGHT, Game.BISHOP, Game.ROOK, Game.QUEEN]
        if promoting:
            if not board.get_square(forward):
                for piece in promotable:
                    moves.append(Move(pos, forward, Piece(piece), board=board, is_not_controlling=True))
            if pos.file != 1:
                # Not in A file, check diagonal left capture
                if board.get_square(left_capture) and board.get_square(left_capture).color == enemy_color:
                    for piece in promotable:
                        moves.append(Move(pos, left_capture, Piece(piece), board=board))
            if pos.file != 8:
                # Not in H file, check diagonal right capture
                if board.get_square(right_capture) and board.get_square(right_capture).color == enemy_color:
                    for piece in promotable:
                        moves.append(Move(pos, right_capture, Piece(piece), board=board))
        # Double move and en passant skipped when promoting,
        # such situations are imposible to happen in any chess position
        else:
            if not board.get_square(forward):
                # Ahead clear
                moves.append(Move(pos, forward, board=board, is_not_controlling=True))
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
                    moves.append(Move(pos, double_forward, board=board, is_not_controlling=True))
            if board.en_passant_squares in [left_capture, right_capture] and board.en_passant_squares:
                if board.get_square(board.en_passant_squares.get_offset((0, -1) if pawn.color == Game.WHITE else (0, 1))).color == enemy_color:
                    # En passant is possible in FEN and that the pawn en_passant references is of the opposite color
                    # (offset because pawn is in the square after the mentioned one in the FEN)
                    moves.append(Move(pos, board.en_passant_squares, board=board, is_en_passant=True))
        return moves

    @staticmethod
    def non_sliding_piece(board: Board, pos: Square, offsets) -> list[Move]:
        own_color = board.get_square(pos).color
        moves = []
        for target_offset in offsets:
            new_square = pos.get_offset(target_offset)
            if not new_square: continue # outside board
            target_square = board.get_square(new_square)
            if target_square:
                # if there's a piece
                if target_square.color == own_color:
                    # and is from the ally color, invalidate move
                    # if statements separated to evade AttributeError when checking None.color
                    continue
            # elif theres no piece or its from enemy color, count move
            moves.append(Move(pos, new_square, board=board))
        return moves

    @staticmethod
    def knight(board: Board, pos: Square) -> list[Move]:
        # hardcoded knight offsets
        offsets = [(-1, 2), (1, 2), (-2, 1), (2, 1), (-2, -1), (2, -1), (-1, -2), (1, -2)]
        return PieceMoves.non_sliding_piece(board, pos, offsets)

    @staticmethod
    def sliding_piece(board: Board, pos: Square, direction_offsets: list[tuple[int, int]]) -> list[Move]:
        own_color = board.get_square(pos).color
        moves = []
        for direction in direction_offsets:
            # inital offset square
            current_target_square = pos.get_offset(direction)
            if not current_target_square: continue # outside board
            while not board.get_square(current_target_square): # while current square empty
                # add move option
                moves.append(Move(pos, current_target_square, board=board))
                # offset current square
                current_target_square = current_target_square.get_offset(direction)
                if not current_target_square: break # reached board end
            if not current_target_square: continue # reached board end, skip color check
            # current square not empty
            # add move anyway if capture
            if board.get_square(current_target_square).color != own_color:
                # if enemy piece, capture available
                moves.append(Move(pos, current_target_square, board=board))
        return moves

    @staticmethod
    def bishop(board: Board, pos: Square) -> list[Move]:
        directions = [(-1, 1), (1, 1), (-1, -1), (-1, 1)]
        return PieceMoves.sliding_piece(board, pos, directions)

    @staticmethod
    def rook(board: Board, pos: Square) -> list[Move]:
        directions = [(0, 1), (-1, 0), (1, 0), (0, -1)]
        return PieceMoves.sliding_piece(board, pos, directions)

    @staticmethod
    def queen(board: Board, pos: Square) -> list[Move]:
        directions = [(-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1)]
        return PieceMoves.sliding_piece(board, pos, directions)

    @staticmethod
    def king(board: Board, pos: Square, ignore_castling: bool=False) -> list[Move]:
        offsets = [(-1, 1), (0, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (0, -1), (1, -1)] # same as queen
        base_moves = PieceMoves.non_sliding_piece(board, pos, offsets)
        if ignore_castling: return base_moves
        castling_moves = []
        color = board.get_square(pos).color
        enemy_color = abs(Game.WHITE-color)
        # king-side castling
        if board.get_square(pos).fen_piece in board.castling_capabilities:
            # check clear path
            if (not board.get_square(pos.get_offset((1, 0)))) and (not board.get_square(pos.get_offset((2, 0)))):
                # bishop space and knight space unnocupied
                if ((not board.is_square_being_attacked_by_color(pos, enemy_color)) # king in peace
                and (not board.is_square_being_attacked_by_color(pos.get_offset((1, 0)), enemy_color)) # bishop space in peace
                and (not board.is_square_being_attacked_by_color(pos.get_offset((2, 0)), enemy_color))): # knight space in peace
                    castling_moves.append(Move(pos, pos.get_offset((2, 0)), board=board))
        # queen-side castling
        fen = 'q' if color == Game.BLACK else 'Q'
        if fen in board.castling_capabilities:
            # check clear path
            if ((not board.get_square(pos.get_offset((-1, 0)))) # no queen
            and (not board.get_square(pos.get_offset((-2, 0)))) # no bishop
            and (not board.get_square(pos.get_offset((-3, 0))))): # no knight
                # space clear
                # check for squares not being attacked
                if ((not board.is_square_being_attacked_by_color(pos, enemy_color)) # king in peace
                and (not board.is_square_being_attacked_by_color(pos.get_offset((-1, 0)), enemy_color)) # queen space in peace
                and (not board.is_square_being_attacked_by_color(pos.get_offset((-2, 0))), enemy_color)):  # bishop space in peace
                    # no knight needed, king does not traverse there
                    castling_moves.append(Move(pos, pos.get_offset((-2, 0)), board=board))

        return base_moves + castling_moves

    @staticmethod
    def generate_moves(board: Board, pos: Square, ignore_castling: bool=False) -> list[Move]:
        piece_type = board.get_square(pos).engine_type
        match piece_type:
            case Game.PAWN:
                return PieceMoves.pawn(board, pos)
            case Game.KNIGHT:
                return PieceMoves.knight(board, pos)
            case Game.BISHOP:
                return PieceMoves.bishop(board, pos)
            case Game.ROOK:
                return PieceMoves.rook(board, pos)
            case Game.QUEEN:
                return PieceMoves.queen(board, pos)
            case Game.KING:
                """
                ignore castling to avoid infinite recursion, castling irrelevant for controlling squares
                :: when utilizing this function to see which squares the enemy is controlling, if castling was included, then we would need
                to check which squares the enemy of the enemy (ally) color is controlling, and if we include castling in that calculation, 
                we would need to check enemy controlling squares and so on, so, for checking square control, we need to ignore castlings, and that
                is possible without consequences, because a castling move is not counted as controlling that square (which will always be covered
                by the tower anyway)
                """
                return PieceMoves.king(board, pos, ignore_castling)
            case _:
                return []
