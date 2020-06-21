#!/usr/bin/env python

from operator import lt, gt
from chesspiece import *
from constants import BLACK, WHITE, INF
from board import Chessboard
import random

class ChessPlayer:
    def __init__(self, board, color, depth):
        self.board = board
        self.color = color
        self.depth = depth
        self.best_move = None

    def evaluate(self):
        value = 0
        for piece in self.board.pieces[WHITE]+self.board.pieces[BLACK]:
            if piece.alive:
                value += piece.value
                value += piece.get_position_value()//10
        return value

    def negamax(self, depth, alfa, beta, color):
        if depth == 0:
            return color*self.evaluate()
        moves = self.board.generate_all_moves(color)
        castle = self.board.castle
        moves.sort(key=lambda e:self.board.is_empty(e.y), reverse=False)
        for move in moves:
            taken_piece = self.board.move(move.x, move.y)
            self.board.cleanup(color)
            val = -self.negamax(depth-1, -beta, -alfa,-color)
            self.board.restore(move.y, move.x, taken_piece)
            if val >= beta:
                return beta
            if val > alfa:
                alfa = val
                if depth == self.depth:
                    self.best_move = move
        self.board.castle = castle
        return alfa

    def next_move(self):
        self.negamax(self.depth, -INF, INF,self.color)
        piece = self.board.data[self.best_move.x.x][self.best_move.x.y]
        print(self.best_move)
        pos = self.best_move.y
        return (piece, pos)


if __name__ == "__main__":
    a = Chessboard()
    player = ChessPlayer(a, BLACK, 3)
    a.move(Vec2(5,7), Vec2(0, 0))
    print(a)
    print(player.next_move())
