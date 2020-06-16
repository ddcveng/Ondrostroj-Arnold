#!/usr/bin/env python

import random
from engine.constants import *
from engine.chesspiece import *

class Game:
    def __init__(self, board, white = HUMAN, black = HUMAN):
        self.white = white
        self.black = black
        self.board = board
        self.highlight_coords = []
        self.highlights = []
        self.turn = WHITE
        self.num_vertexes = 0
        self.active_piece = None
        self.over = False
    
    def generate_highlights(self, moves):
        self.highlight_coords = []
        for move in moves:
            i,j = move.x, move.y
            self.highlights.append(move)
            self.highlight_coords += [
                OFFSET+GRID_SIZE*i,     OFFSET+GRID_SIZE*j,
                OFFSET+GRID_SIZE*(i+1), OFFSET+GRID_SIZE*j,
                OFFSET+GRID_SIZE*(i+1), OFFSET+GRID_SIZE*(j+1),
                OFFSET+GRID_SIZE*i,     OFFSET+GRID_SIZE*(j+1)
            ]
    
    def highlight_moves(self, x, y):
        self.board.cleanup(self.turn)
        self.active_piece = self.board.data[x][y]
        if self.active_piece and self.turn == self.active_piece.color:
            self.generate_highlights(self.board.generate_moves(self.active_piece))
            self.num_vertexes = len(self.highlights)*4
 
    def stop_highlighting(self):
        self.active_piece = None
        self.highlight_coords = []
        self.highlights = []
        self.num_vertexes = 0
    
    def move_piece(self, pos, piece = None):#!!!!!
        if piece == None:
            piece = self.active_piece
        else:
            self.active_piece = piece
        piece.sprite.x = pos.x*GRID_SIZE+CENTER_CONST
        piece.sprite.y = pos.y*GRID_SIZE+CENTER_CONST

        take = self.board.move(piece.pos, pos)
        if take:
            take.sprite.batch = None
            take.pos = Vec2(-1, -1)
            take.alive = 0

    def manage_check(self):
        enemy_king = self.board.black_pieces[12] if self.active_piece.color == WHITE else self.board.white_pieces[12]
        if self.board.can_endanger(enemy_king.pos, self.active_piece):
            self.board.check = enemy_king
            self.over = self.board.checkmate()
        elif self.board.check:
            self.board.check = None
    
    def manage_pawns(self):
        if isinstance(self.active_piece, Pawn) and self.active_piece.moved == 0:
            self.active_piece.moved = 1
        # enpassant
        t = self.board.enpassant
        if t:
            t.x.sprite.batch = None
            self.board.data[t.y.x][t.y.y] = 0

    def manage_castling(self, pos):
        castle_rook = None
        if self.board.castle.x == pos:
            castle_rook = self.board.white_pieces[8] if self.turn == WHITE else self.board.black_pieces[15]
            pos.x = pos.x+self.turn
        elif self.board.castle.y == pos:
            castle_rook = self.board.white_pieces[15] if self.turn == WHITE else self.board.black_pieces[8]
            pos.x = pos.x-self.turn
        if castle_rook:
            castle_rook.sprite.x = pos.x*GRID_SIZE+CENTER_CONST
            castle_rook.sprite.y = pos.y*GRID_SIZE+CENTER_CONST
            self.board.data[pos.x][pos.y] = castle_rook
            self.board.data[castle_rook.pos.x][castle_rook.pos.y] = 0
            castle_rook.pos = pos
    
    def manage(self, pos):
        self.manage_check()
        self.manage_pawns()
        self.manage_castling(pos)

    def end_turn(self):
        self.turn = -self.turn
        self.stop_highlighting()
        if self.turn == WHITE:
            if self.white != HUMAN:
                piece, pos = self.white.next_move()
                self.move_piece(pos, piece)
                self.end_turn()
        else:
            if self.black != HUMAN:
                piece, pos = self.black.next_move()
                self.move_piece(pos, piece)
                self.end_turn()