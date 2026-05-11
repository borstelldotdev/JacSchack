from src.logic.board_mailbox import BoardMailbox
from src.logic.eval import evaluate

class NegaMax:
    def __init__(self):
        pass

    def nega_max(self, board: BoardMailbox, depth: int):
        if depth == 0 or len(board.my_moves) == 0:
            return evaluate(board)
        return max(-self.nega_max(board.make_move(x), depth - 1) for x in board.my_moves)

    def make_decision(self, board: BoardMailbox, depth: int):
        best_eval, best_move = -99999999, None
        for move in board.my_moves:
            new_board = board.make_move(move)
            evaluation = -self.nega_max(new_board, depth)
            print(move, evaluation)
            if evaluation > best_eval:
                best_eval = evaluation
                best_move = move

        return best_move