#!/usr/bin/env python

from operator import lt, gt
from engine.chesspiece import Vec2
from engine.constants import BLACK, WHITE, INF
from engine.board import Chessboard

class ChessPlayer:
    def __init__(self, board, color, depth):
        self.board = board
        self.color = color
        self.depth = depth

    def evaluate(self):
        value = 0
        for piece in self.board.white_pieces+self.board.black_pieces:
            if piece.alive:
                value += piece.value
        return value
    
    def get_best_move(self, depth, alpha, beta, color):
        best_val = -color*INF
        best_move = None
        cmpr = gt if color == WHITE else lt
        moves = self.board.generate_all_moves(color)
        for move in moves:
            val = self.minimax(move, depth, alpha, beta, color == BLACK)
            if cmpr(val.y, best_val):
                best_val = val.y
                best_move = move
            #pruning
            if color == WHITE:
                alpha = max(alpha, val.y)
            else:
                beta = min(beta, val.y)
            if beta <= alpha:
                break
        return Vec2(best_move, best_val)
        

    def minimax(self, move, depth, alpha, beta, maximize):
        if depth == 0:
            return Vec2(move, self.evaluate())

        take = self.board.move(move.x, move.y)
        if maximize:
            res = self.get_best_move(depth - 1, alpha, beta, WHITE)
        else:
            res = self.get_best_move(depth - 1, alpha, beta, BLACK)
        self.board.restore(move.y, move.x, take)
        return res
    
    def next_move(self):
        data = self.minimax(Vec2(Vec2(0,0), Vec2(0,0)), self.depth, -INF, INF, self.color == WHITE).x
        piece = self.board.data[data.x.x][data.x.y]
        pos = data.y
        return (piece, pos)


if __name__ == "__main__":
    a = Chessboard()
    player = ChessPlayer(a, BLACK, 3)
    next_move = player.next_move()
    print(next_move)