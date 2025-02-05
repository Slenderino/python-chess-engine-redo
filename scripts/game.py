class Game:
    def __init__(self):
        self.board = Board()
    def get_board(self):
        return self.board.set_starter().repr
class Board:
    def set_starter(self):
        self.repr = ["r", "n", "b", "q", "k", "b", "n", "r",
                     "p", "p", "p", "p", "p", "p", "p", "p",
                     " ", " ", " ", " ", " ", " ", " ", " ",
                     " ", " ", " ", " ", " ", " ", " ", " ",
                     " ", " ", " ", " ", " ", " ", " ", " ",
                     " ", " ", " ", " ", " ", " ", " ", " ",
                     "P", "P", "P", "P", "P", "P", "P", "P",
                     "R", "N", "B", "Q", "K", "B", "N", "R"]
        self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        return self
    repr = [" " for _ in range(64)]
    fen = "8/8/8/8/8/8/8/8 w - - - -"