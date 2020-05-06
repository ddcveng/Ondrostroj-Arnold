from operator import lt, gt
from chesspiece import Vec2
from constants import BLACK, WHITE
from game import Chessboard

INF = 1110

class ChessPlayer:
    def __init__(self, board):
        self.board = board

    def evaluate(self):
        #todo oneliner with lambda
        value = 0
        for piece in self.board.white_pieces+self.board.black_pieces:
            if piece.alive:
                value += piece.value
        return value

    # def minimax(self, position, depth, color):
    #     stack = []
    #     val = -color*INF
    #     stack.append(MovesData([], self.board.generate_all_moves(color)))
    #     while stack:
    #         #daj synov na stack kym nieje depth 0 resp kym su synovia
    #         pos = stack[-1]
    
    def get_best_move(self, depth, color):
        best_val = -color*INF
        best_move = None
        cmpr = gt if color == WHITE else lt
        moves = self.board.generate_all_moves(color)
        for move in moves:
            val = self.minimax(move, depth, color == BLACK)
            if cmpr(val.y, best_val):
                best_val = val.y
                best_move = move
        return Vec2(best_move, best_val)
        

    def minimax(self, move, depth, maximize):
        if depth == 0:
            return Vec2(move, self.evaluate())

        take = self.board.move(move.x, move.y)
        if maximize:
            # max_val = -INF
            # white_moves = self.board.generate_all_moves(WHITE)
            # for move in white_moves:
            #     val = self.minimax(move, depth - 1, False)
            #     max_val = max(max_val, val)
            # return max_val
            res = self.get_best_move(depth - 1, WHITE)

        else:
            # min_val = INF
            # black_moves = self.board.generate_all_moves(BLACK)
            # for move in black_moves:
            #     val = self.minimax(move, depth - 1, True)
            #     min_val = min(min_val, val)
            # return min_val
            res = self.get_best_move(depth - 1, BLACK)
        self.board.restore(move.y, move.x, take)
        return res

if __name__ == "__main__":
    a = Chessboard()
    player = ChessPlayer(a)
    next_move = player.minimax(Vec2(Vec2(0,1), Vec2(0,2)), 4, False)
    print(next_move)