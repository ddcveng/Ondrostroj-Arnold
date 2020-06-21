#!/usr/bin/env python

import random
import pyglet
from constants import *
from chesspiece import *

class Game:
    def __init__(self, board, white = HUMAN, black = HUMAN):
        self.white = white
        self.black = black
        self.players = {WHITE: white, BLACK: black}
        self.board = board
        self.highlight_coords = []
        self.highlights = []
        self.turn = WHITE
        self.num_vertexes = 0
        self.active_piece = None
        self.over = False
        self.turn_ended = False
        self.clock = pyglet.clock.get_default()
        self.last_move = None
        self.dead = 0
    
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
        if self.players[self.turn] != HUMAN: return
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
        piece.sprite.update(x=pos.x*GRID_SIZE+CENTER_CONST, y=pos.y*GRID_SIZE+CENTER_CONST)
        
        self.last_move = Vec2(piece.pos, pos)
        print(f"{self.board.coords_to_chess(piece.pos)} -> {self.board.coords_to_chess(pos)}")
        
        self.dead = self.board.move(piece.pos, pos)

    def manage_check(self, piece = None):
        if piece == None:
            piece = self.active_piece
        enemy_king = self.board.pieces[-piece.color][12]
        if self.board.can_endanger(enemy_king.pos, piece):
            self.board.check = enemy_king
            self.over = self.board.checkmate()
            return
        self.board.check = None

    def manage_castling(self, pos):
        castle_rook = None
        pos = Vec2(pos.x, pos.y) # copy pos into new object
        if self.board.castle.x and self.board.castle.x == pos:
            castle_rook = self.board.pieces[self.turn][int(11.5 - self.turn*3.5)]
            pos.x = pos.x+self.turn
        elif self.board.castle.y and self.board.castle.y == pos:
            castle_rook = self.board.pieces[self.turn][int(11.5 + self.turn*3.5)]
            pos.x = pos.x-self.turn
        if castle_rook:
            castle_rook.sprite.update(x=pos.x*GRID_SIZE+CENTER_CONST, y=pos.y*GRID_SIZE+CENTER_CONST)
            self.board.data[pos.x][pos.y] = castle_rook
            self.board.data[castle_rook.pos.x][castle_rook.pos.y] = 0
            castle_rook.pos = pos
            self.manage_check(castle_rook)

    
    def manage(self, pos):
        self.manage_check()
        self.manage_castling(pos)
    
    def manage_robots(self, _):
        player = self.players[self.turn]
        if player != HUMAN:
            piece, pos = player.next_move()
            if piece and pos:
                self.move_piece(pos, piece)
                self.manage(pos)
                self.end_turn()
            else:
                print(piece)
                print(pos)
                self.over = -player.color

    def end_turn(self):
        self.board.cleanup(self.turn)
        self.turn = -self.turn
        self.stop_highlighting()
        self.clock.schedule_once(self.manage_robots, .1)