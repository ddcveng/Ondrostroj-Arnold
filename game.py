import random
from constants import *
from chesspiece import *

class Game:
    def __init__(self):
        self.board = Chessboard()
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


class Chessboard:
    def __init__(self):
        self.white_pieces = [Pawn(i,1,WHITE) for i in range(8)] + [Rook(0,0,WHITE),Knight(1,0,WHITE),Bishop(2,0,WHITE),Queen(3,0,WHITE),
                                                                King(4,0,WHITE),Bishop(5,0,WHITE),Knight(6,0,WHITE),Rook(7,0,WHITE)]
        self.black_pieces = [Pawn(i,6,BLACK) for i in range(8)] + [Rook(0,7,BLACK),Knight(1,7,BLACK),Bishop(2,7,BLACK),Queen(3,7,BLACK),
                                                                King(4,7,BLACK),Bishop(5,7,BLACK),Knight(6,7,BLACK),Rook(7,7,BLACK)]
        self.WHITE_KING = self.white_pieces[12]
        self.BLACK_KING = self.black_pieces[12]
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
        self.castle = Vec2(Vec2(), Vec2())
        self.check = None

    def coords_to_chess(self, coords):
        return chr(ord(str(coords.x))+DECODE_OFFSET)+chr(ord(str(coords.y))+1)
    
    def move(self, pos1, pos2):
        tmp = self.data[pos2.x][pos2.y]
        self.data[pos2.x][pos2.y] = self.data[pos1.x][pos1.y]
        self.data[pos1.x][pos1.y] = 0
        return tmp
    
    def restore(self, pos1, pos2, take):
        self.move(pos1, pos2)
        self.data[pos1.x][pos1.y] = take

    def checkmate(self):
        moves = []
        allies = self.white_pieces if self.check.color == WHITE else self.black_pieces
        for ally in allies:
            moves += self.generate_moves(ally)
        return len(moves) == 0
    
    def cleanup(self, turn):
        self.castle = Vec2(Vec2(), Vec2())
        if self.enpassant and self.enpassant.x.color == turn:
            self.enpassant = None
        ally_pawns = self.white_pieces[0:8] if turn == 1 else self.black_pieces[0:8]
        for piece in ally_pawns:
            if piece.moved != 0:
                piece.moved = 2
    
    def is_valid(self, pos):
        return self.is_on_board(pos) and not self.data[pos.x][pos.y]
    
    def is_on_board(self, pos):
        return pos.x <= 7 and pos.x >= 0 and pos.y >= 0 and pos.y <= 7
    
    def is_enemy(self, piece, pos):
        return self.data[pos.x][pos.y] and piece.color != self.data[pos.x][pos.y].color        

    def validate_moves(self, moves, piece, recursive = 0):
        valid_moves = []
        temp = []

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
                    if type(enpassant) == Pawn and enpassant.moved == 1:
                        valid_moves.append(piece.pos + Vec2(1,piece.color))
                        self.enpassant = Vec2(enpassant, Vec2(tempx, tempy))
                elif tempx-2 >= 0:
                    enpassant = self.data[tempx-2][tempy]
                    if type(enpassant) == Pawn and enpassant.moved == 1:
                        valid_moves.append(piece.pos + Vec2(-1,piece.color))
                        self.enpassant = Vec2(enpassant, Vec2(tempx-2, tempy))
        
        elif type(piece) == King and not recursive:
            #castling
            queen_side = self.white_pieces[8] if piece.color == WHITE else self.black_pieces[15]
            king_side  = self.white_pieces[15] if piece.color == WHITE else self.black_pieces[8]
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
    
    def generate_all_moves(self, color):
        pieces = self.white_pieces if color == WHITE else self.black_pieces
        moves = []
        for piece in pieces:
            endpoints = self.generate_moves(piece)
            for endpoint in endpoints:
                moves.append(Vec2(piece.pos, endpoint))
        return moves

    def is_endangered(self, pos, enemy_color):
        enemy_pieces = self.black_pieces if enemy_color == BLACK else self.white_pieces
        for piece in enemy_pieces:
            if self.can_endanger(pos, piece):
                return True
        return False
    
    def can_endanger(self, pos, piece):
        moves = self.generate_moves(piece, 1)
        return pos in moves
    

if __name__ == '__main__':
    a = Chessboard()
    print(a.generate_moves(a.white_pieces[0]))