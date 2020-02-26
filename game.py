import random
from constants import *
from chesspiece import *
from copy import deepcopy

class Game:
    def __init__(self):#0-normal 1-random
        self.board = Chessboard()
        self.highlight_coords = []
        self.highlights = []
        self.turn = 1 #0-white 1-black
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
        self.active_piece = self.board.data[x][y]
        if self.active_piece and self.turn == self.active_piece.color:
            self.generate_highlights(self.board.generate_moves(self.active_piece))
            self.num_vertexes = len(self.highlights)*4

    def stop_highlighting(self):
        self.active_piece = None
        self.highlight_coords = []
        self.highlights = []
        self.num_vertexes = 0
    
    def checkmate(self):
        moves = []
        allies = self.board.white_pieces if self.board.check.color == WHITE else self.board.black_pieces
        for ally in allies:
            moves += self.board.generate_moves(ally)
        return len(moves) == 0


class Chessboard:
    def __init__(self):
        self.white_pieces = [Pawn(i,1,WHITE) for i in range(8)] + [Rook(0,0,WHITE),Knight(1,0,WHITE),Bishop(2,0,WHITE),King(3,0,WHITE),
                                                                Queen(4,0,WHITE),Bishop(5,0,WHITE),Knight(6,0,WHITE),Rook(7,0,WHITE)]
        self.black_pieces = [Pawn(i,6,BLACK) for i in range(8)] + [Rook(0,7,BLACK),Knight(1,7,BLACK),Bishop(2,7,BLACK),King(3,7,BLACK),
                                                                Queen(4,7,BLACK),Bishop(5,7,BLACK),Knight(6,7,BLACK),Rook(7,7,BLACK)]
        self.WHITE_KING = self.white_pieces[11]
        self.BLACK_KING = self.black_pieces[11]
        self.data =  [
                [self.white_pieces[8],  self.white_pieces[0], 0,0,0,0, self.black_pieces[0], self.black_pieces[8]],
                [self.white_pieces[9],  self.white_pieces[1], 0,0,0,0, self.black_pieces[1], self.black_pieces[9]],
                [self.white_pieces[10], self.white_pieces[2], 0,0,0,0, self.black_pieces[2], self.black_pieces[10]],
                [self.white_pieces[11], self.white_pieces[3], 0,0,0,0, self.black_pieces[3], self.black_pieces[11]],
                [self.white_pieces[12], self.white_pieces[4], 0,0,0,0, self.black_pieces[4], self.black_pieces[12]],
                [self.white_pieces[13], self.white_pieces[5], 0,0,0,0, self.black_pieces[5], self.black_pieces[13]],
                [self.white_pieces[14], self.white_pieces[6], 0,0,0,0, self.black_pieces[6], self.black_pieces[14]],
                [self.white_pieces[15], self.white_pieces[7], 0,0,0,0, self.black_pieces[7], self.black_pieces[15]]
            ]
        self.enpassant = None
        self.check = None
    
    def is_valid(self, pos):
        return self.is_on_board(pos) and not self.data[pos.x][pos.y]
    
    def is_on_board(self, pos):
        return pos.x <= 7 and pos.x >= 0 and pos.y >= 0 and pos.y <= 7
    
    def is_enemy(self, piece, pos):
        return self.data[pos.x][pos.y] and piece.color != self.data[pos.x][pos.y].color        

    def validate_moves(self, moves, piece, recursive = 0):
        valid_moves = []
        temp = []
        self.enpassant = None

        #basic moves
        for offset in moves:
            move = piece.pos + offset
            if self.is_on_board(move):
                if self.data[move.x][move.y] == 0:
                    valid_moves.append(move)
                elif self.is_enemy(piece, move):
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
                if self.is_on_board(pos) and self.is_enemy(piece, pos):
                    temp.append(pos)
        valid_moves += temp
                
        #pawn shenanigans
        if type(piece) == Pawn:
            temp = []
            for move in valid_moves:
                if self.data[move.x][move.y] == 0:
                    temp.append(move)
            valid_moves = temp

            #taking pieces
            take = piece.pos + Vec2(1,piece.color)
            if take.x <= 7 and take.y <= 7 and self.data[take.x][take.y] and self.data[take.x][take.y].color != piece.color:
                valid_moves.append(take)
            take += Vec2(-2, 0)
            if take.x >= 0 and take.y <= 7 and self.data[take.x][take.y] and self.data[take.x][take.y].color != piece.color:
                valid_moves.append(take)
            
            #enpassant
            if ((piece.pos.y == 4 and piece.color == WHITE) or 
                (piece.pos.y == 3 and piece.color == BLACK)):
                tempx = piece.pos.x+1
                tempy = piece.pos.y
                if tempx <= 7:
                    enpassant = self.data[tempx][tempy]
                    if type(enpassant) == Pawn and enpassant.moved_once:
                        valid_moves.append(piece.pos + Vec2(1,piece.color))
                        self.enpassant = Vec2(enpassant, Vec2(tempx, tempy))
                elif tempx-2 >= 0:
                    enpassant = self.data[tempx-2][tempy]
                    if type(enpassant) == Pawn and enpassant.moved_once:
                        valid_moves.append(piece.pos + Vec2(-1,piece.color))
                        self.enpassant = Vec2(enpassant, Vec2(tempx, tempy))
        
        if self.check and not recursive:
            valid_moves = self.remove_fatal_moves(valid_moves, piece, self.check)

        if not recursive:
            ally_king = self.BLACK_KING if piece.color == BLACK else self.WHITE_KING
            return self.remove_fatal_moves(valid_moves, piece, ally_king)
        else:
            return valid_moves
            
    def remove_fatal_moves(self, moves, moving_piece, endangered_piece):
        #remove moves from <moves> that would be fatal for <piece>
        temp = []
        for move in moves:
            #try this move
            original_piece = self.data[move.x][move.y]
            if original_piece:
                original_piece.pos = Vec2(-1,-1)
            piece_pos = moving_piece.pos
            self.data[move.x][move.y] = moving_piece
            self.data[moving_piece.pos.x][moving_piece.pos.y] = 0
            moving_piece.pos = move
            #can we make it without losing?
            if not self.is_endangered(endangered_piece.pos, -endangered_piece.color):
                temp.append(move)
            #restore our board
            moving_piece.pos = piece_pos
            self.data[moving_piece.pos.x][moving_piece.pos.y] = moving_piece
            self.data[move.x][move.y] = original_piece
            if original_piece:
                self.data[move.x][move.y].pos = move
        return temp 

    def generate_moves(self, piece, recursive = 0):
        offsets = piece.get_moves()
        return self.validate_moves(offsets, piece, recursive)

    def is_endangered(self, pos, enemy_color):
        enemy_pieces = self.black_pieces if enemy_color == BLACK else self.white_pieces
        for piece in enemy_pieces:
            if self.can_endanger(pos, piece):
                return True
        return False
    
    def can_endanger(self, pos, piece):
        moves = self.generate_moves(piece, 1)
        return pos in moves