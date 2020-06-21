#!/usr/bin/env python

from chesspiece import *
from constants import *

class Chessboard:
    def __init__(self):
        self.pieces = {WHITE: [Pawn(i,1,WHITE) for i in range(8)] + [Rook(0,0,WHITE),Knight(1,0,WHITE),Bishop(2,0,WHITE),Queen(3,0,WHITE),
                                                                King(4,0,WHITE),Bishop(5,0,WHITE),Knight(6,0,WHITE),Rook(7,0,WHITE)],
                       BLACK: [Pawn(i,6,BLACK) for i in range(8)] + [Rook(0,7,BLACK),Knight(1,7,BLACK),Bishop(2,7,BLACK),Queen(3,7,BLACK),
                                                                King(4,7,BLACK),Bishop(5,7,BLACK),Knight(6,7,BLACK),Rook(7,7,BLACK)]}
        self.WHITE_KING = self.pieces[WHITE][12]
        self.BLACK_KING = self.pieces[BLACK][12]
        self.data =  [
                [self.pieces[WHITE][8],  self.pieces[WHITE][0], 0,0,0,0, self.pieces[BLACK][0], self.pieces[BLACK][8]],
                [self.pieces[WHITE][9],  self.pieces[WHITE][1], 0,0,0,0, self.pieces[BLACK][1], self.pieces[BLACK][9]],
                [self.pieces[WHITE][10], self.pieces[WHITE][2], 0,0,0,0, self.pieces[BLACK][2], self.pieces[BLACK][10]],
                [self.pieces[WHITE][11], self.pieces[WHITE][3], 0,0,0,0, self.pieces[BLACK][3], self.pieces[BLACK][11]],
                [self.pieces[WHITE][12], self.pieces[WHITE][4], 0,0,0,0, self.pieces[BLACK][4], self.pieces[BLACK][12]],
                [self.pieces[WHITE][13], self.pieces[WHITE][5], 0,0,0,0, self.pieces[BLACK][5], self.pieces[BLACK][13]],
                [self.pieces[WHITE][14], self.pieces[WHITE][6], 0,0,0,0, self.pieces[BLACK][6], self.pieces[BLACK][14]],
                [self.pieces[WHITE][15], self.pieces[WHITE][7], 0,0,0,0, self.pieces[BLACK][7], self.pieces[BLACK][15]]
            ]
        self.castle = Vec2()
        self.check = None
        self.robot_players = []

    def coords_to_chess(self, coords):
        return chr(ord(str(coords.x))+DECODE_OFFSET)+chr(ord(str(coords.y))+1)
    
    def move(self, pos1, pos2, direction = 1):
        if not self.is_on_board(pos1) or not self.is_on_board(pos2):
            print(f"{pos1} - {pos2}")
        take = self.data[pos2.x][pos2.y]
        if take:
            take.alive = 0
        piece = self.data[pos1.x][pos1.y]
        piece.pos = pos2
        piece.moved += direction
        self.data[pos2.x][pos2.y] = piece
        self.data[pos1.x][pos1.y] = 0
        return take
    
    def restore(self, pos1, pos2, take):
        if take:
            take.alive = 1
        self.move(pos1, pos2, -1)
        self.data[pos1.x][pos1.y] = take

    def checkmate(self):
        moves = self.generate_all_moves(self.check.color)
        if len(moves) == 0:
            return -self.check.color
        return 0
    
    def cleanup(self, turn):
        self.castle = Vec2()
        self.enpassant = None
        if self.check and self.check.color == turn:
            self.check = None

    def is_valid(self, pos):
        return self.is_on_board(pos) and self.is_empty(pos)
    
    def is_on_board(self, pos):
        return pos.x <= 7 and pos.x >= 0 and pos.y >= 0 and pos.y <= 7
    
    def is_enemy(self, color, pos):
        return self.is_on_board(pos) and not self.is_empty(pos) and color != self.data[pos.x][pos.y].color

    def is_empty(self, pos):
        return self.data[pos.x][pos.y] == 0

    def validate_moves(self, moves, piece, recursive = 0):
        valid_moves = []
        temp = []
        #basic moves
        for offset in moves:
            move = piece.pos + offset
            if self.is_on_board(move):
                if self.data[move.x][move.y] == 0:
                    valid_moves.append(move)
                elif self.is_enemy(piece.color, move):
                    temp.append(move)
        #extended moves
        if piece.continuous:
            for move in valid_moves:
                valid_offset = move - piece.pos
                for i in range(2,8):
                    pos = piece.pos + valid_offset*i
                    if self.is_valid(pos):
                        temp.append(pos)
                    else:
                        break
                if self.is_on_board(pos) and self.is_enemy(piece.color, pos):
                    temp.append(pos)
        valid_moves += temp
        #pawn shenanigans
        if isinstance(piece, Pawn):
            temp = []
            for move in valid_moves:
                if self.data[move.x][move.y] == 0:
                    temp.append(move)
            valid_moves = temp
            #initial double move
            if not piece.moved and len(valid_moves) != 0 and self.data[piece.pos.x][piece.pos.y+2*piece.color] == 0:            
                valid_moves.append(piece.pos + Vec2(0, 2*piece.color))
            #taking pieces
            take = piece.pos + Vec2(1,piece.color)
            if self.is_enemy(piece.color, take):
                valid_moves.append(take)
            take += Vec2(-2, 0)
            if self.is_enemy(piece.color, take):
                valid_moves.append(take)
        elif isinstance(piece, King) and not recursive:
            #castling
            queen_side = self.pieces[piece.color][int(11.5 - piece.color*3.5)]
            king_side  = self.pieces[piece.color][int(11.5 + piece.color*3.5)]
            if piece.moved == 0:
                castle = Vec2()
                if queen_side.moved == 0:
                    castle.x = queen_side
                if king_side.moved == 0:
                    castle.y = king_side
                #queen_side
                if castle.x and self.empty_inbetween(castle.x, piece):
                    self.castle.x = Vec2(piece.pos.x-2*piece.color, piece.pos.y)
                    valid_moves.append(self.castle.x)
                #king_side
                if castle.y and self.empty_inbetween(castle.y, piece):
                    self.castle.y = Vec2(piece.pos.x+2*piece.color, piece.pos.y)
                    valid_moves.append(self.castle.y)
        if not recursive:
            ally_king = self.BLACK_KING if piece.color == BLACK else self.WHITE_KING
            return self.remove_fatal_moves(valid_moves, piece, ally_king)
        else:
            return valid_moves

    def empty_inbetween(self, piece1, piece2):
        y = piece1.pos.y
        x1 = piece1.pos.x
        x2 = piece2.pos.x
        for x in range(min(x1,x2)+1, max(x1,x2)):
            if self.data[x][y] or self.is_endangered(Vec2(x,y), -piece1.color):
                return False
        return True

    def remove_fatal_moves(self, moves, moving_piece, endangered_piece):
        #remove moves from <moves> that would be fatal for <endangered_piece>
        temp = []
        start = moving_piece.pos
        for end in moves:
            take = self.move(start, end)
            if not self.is_endangered(endangered_piece.pos, -endangered_piece.color):
                temp.append(end)
            self.restore(end, start, take)
        return temp

    def generate_moves(self, piece, recursive = 0):
        if piece.alive:
            offsets = piece.get_moves()
            return self.validate_moves(offsets, piece, recursive)
        return []

    def generate_all_moves(self, color):
        pieces = self.pieces[color]
        moves = []
        for piece in pieces:
            endpoints = self.generate_moves(piece)
            for endpoint in endpoints:
                moves.append(Vec2(piece.pos, endpoint))
        return moves

    def is_endangered(self, pos, enemy_color):
        enemy_pieces = self.pieces[enemy_color]
        for piece in enemy_pieces:
            if self.can_endanger(pos, piece):
                return True
        return False

    def can_endanger(self, pos, piece):
        if piece.alive:
            moves = self.generate_moves(piece, 1)
            return pos in moves
        return False

    def __repr__(self):
        s = ""
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                s += f"{self.data[i][j]}\t"
            s += "\n"
        return s

if __name__ == "__main__":
    a = Chessboard()
    print(a)
    a.move(Vec2(1,0), Vec2(0,2))
    a.move(Vec2(6,0), Vec2(5,2))
    print(a)
    t = a.move(Vec2(0, 2), Vec2(0, 6))
    print(a)
    a.restore(Vec2(0, 6), Vec2(0, 2), t)
    a.restore(Vec2(0,2), Vec2(1, 0), 0)
    a.restore(Vec2(5, 2), Vec2(6, 0), 0)
    print(a)