#!/usr/bin/env python

from operator import lt, gt
from chesspiece import *
from constants import BLACK, WHITE, INF, DEPTH, ENDGAME
from board import Chessboard
import random

class ChessPlayer:
    def __init__(self, board, color, depth, max_depth):
        self.board = board
        self.color = color
        self.depth = depth
        self.max_depth = max_depth
        self.real_depth = 0
        self.best_move = None
        self.endgame = False
        self.terminal = False

    def evaluate(self):
        value = 0
        for piece in self.board.pieces[WHITE]+self.board.pieces[BLACK]:
            if piece.alive:
                value += piece.value
                value += piece.get_position_value()//10
            if self.endgame and isinstance(piece, King):
                value += 20*piece.color*len(self.board.generate_moves(piece))
        return value + random.randint(-5, 5)

    def negamax(self, depth, alfa, beta, color):
        if depth == 0 or self.real_depth == self.max_depth:
            return color*self.evaluate()
        moves = self.board.generate_all_moves(color)
        castle = self.board.castle
        moves.sort(key=lambda e:self.board.is_empty(e.y), reverse=False)
        l = len(moves)
        if l == 0:
            self.terminal = True
            return -color*10000 # terminal game state - someone won
        decrement = 1
        if l < 10:
            decrement = 0
        self.real_depth += 1
        for move in moves:
            taken_piece = self.board.move(move.x, move.y)
            self.board.cleanup(color)
            val = -self.negamax(depth-decrement, -beta, -alfa,-color)
            self.real_depth -= 1
            self.board.restore(move.y, move.x, taken_piece)
            if val >= beta:
                return beta
            if val > alfa:
                alfa = val
                if depth == self.depth:
                    self.best_move = move
            if self.terminal:
                break
        self.board.castle = castle
        return alfa

    def next_move(self):
        black_pieces = 0
        for piece in self.board.pieces[BLACK]:
            if piece.alive:
                black_pieces += 1
        white_pieces = 0
        for piece in self.board.pieces[WHITE]:
            if piece.alive:
                white_pieces += 1
        if black_pieces < ENDGAME or white_pieces < ENDGAME:
            self.endgame = True
        self.best_move = None
        self.terminal = False
        self.negamax(self.depth, -INF, INF,self.color)
        if self.best_move:
            piece = self.board.data[self.best_move.x.x][self.best_move.x.y]
            pos = self.best_move.y
            print(self.best_move)
            return (piece, pos)
        return (None, None)
