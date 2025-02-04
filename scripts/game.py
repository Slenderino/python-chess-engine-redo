class Game:
    def __init__(self):
        self.board = Board()
    def get_board(self):
        return self.board.repr
class Board:
    repr = ["r" for _ in range(64)]