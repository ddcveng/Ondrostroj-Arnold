#!/usr/bin/env python
from constants import WHITE, BLACK

class Vec2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        if type(other) == Vec2:
            return Vec2(self.x+other.x, self.y+other.y)
        else:
            return Vec2(self.x+other, self.y+other)

    def __sub__(self, other):
        return self.__add__(-other)
        
    def __mul__(self, t):
        return Vec2(self.x*t, self.y*t)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __neg__(self):
        return Vec2(-self.x, -self.y)
    
    def __repr__(self):
        return f"Vec2({self.x}, {self.y})"

class Chesspiece:
    # Piece-Square tables from https://www.chessprogramming.org/Simplified_Evaluation_Function
    position_values = []
    def __init__(self, x, y, color, continuous = 0):
        self.pos = Vec2(x, y)
        self.value = None
        self.continuous = continuous
        self.color = color
        self.sprite = None
        self.moved = 0
        self.alive = 1

    def get_moves(self):
        pass

    def __repr__(self):
        return str(self.value)
    
    def get_position_value(self):
        if self.color == WHITE:
            return self.__class__.position_values[self.pos.y][self.pos.x]
        else:
            return BLACK*self.__class__.position_values[7-self.pos.y][self.pos.x]

class Pawn(Chesspiece):
    position_values =  [[0,  0,  0,  0,  0,  0,  0,  0],
                        [5, 10, 10,-20,-20, 10, 10,  5],
                        [5,  5, 10, 25, 25, 10,  5,  5],
                        [5, -5,-10,  0,  0,-10, -5,  5],
                        [0,  0,  0, 20, 20,  0,  0,  0],
                        [10, 10, 20, 30, 30, 20, 10, 10],
                        [50, 50, 50, 50, 50, 50, 50, 50],
                        [100, 100, 100, 100, 100, 100, 100, 100]]
    def __init__(self, x, y, color):
        super().__init__(x,y,color)
        self.value = 10*self.color

    def get_moves(self):
        return [Vec2(0,self.color)]

class Rook(Chesspiece):
    position_values =  [[0,  0,  0,  5,  5,  0,  0,  0],
                        [-5,  0,  0,  0,  0,  0,  0, -5],
                        [-5,  0,  0,  0,  0,  0,  0, -5],
                        [-5,  0,  0,  0,  0,  0,  0, -5],
                        [-5,  0,  0,  0,  0,  0,  0, -5],
                        [-5,  0,  0,  0,  0,  0,  0, -5],
                        [5, 10, 10, 10, 10, 10, 10,  5],
                        [0,  0,  0,  0,  0,  0,  0,  0]]
    def __init__(self, x, y, color):#1-white -1-black
        super().__init__(x,y,color,1)
        self.value = 50*self.color
    
    def get_moves(self):
        return [Vec2(1,0), Vec2(-1,0), Vec2(0,1), Vec2(0,-1)]

class Knight(Chesspiece):
    position_values = [[-50,-40,-30,-30,-30,-30,-40,-50],
                        [-40,-20,  0,  5,  5,  0,-20,-40],
                        [-30,  5, 10, 15, 15, 10,  5,-30],
                        [-30,  0, 15, 20, 20, 15,  0,-30],
                        [-30,  5, 15, 20, 20, 15,  5,-30],
                        [-30,  0, 10, 15, 15, 10,  0,-30],
                        [-40,-20,  0,  0,  0,  0,-20,-40],
                        [-50,-40,-30,-30,-30,-30,-40,-50]]
    def __init__(self, x, y, color):#1-white -1-black
        super().__init__(x,y,color)
        self.value = 30*self.color
    
    def get_moves(self):
        return [Vec2(1,2), Vec2(-1,2), Vec2(2,1), Vec2(-2,1),
                Vec2(1,-2), Vec2(-1,-2), Vec2(2,-1), Vec2(-2,-1)]

class Bishop(Chesspiece):
    position_values = [[-20,-10,-10,-10,-10,-10,-10,-20],
                        [-10,  0,  0,  0,  0,  0,  0,-10],
                        [-10,  0,  5, 10, 10,  5,  0,-10],
                        [-10,  0, 10, 10, 10, 10,  0,-10],
                        [-10,  5,  5, 10, 10,  5,  5,-10],
                        [-10, 10, 10, 10, 10, 10, 10,-10],
                        [-10,  5,  0,  0,  0,  0,  5,-10],
                        [-20,-10,-10,-10,-10,-10,-10,-20]]
    def __init__(self, x, y, color):#1-white -1-black
        super().__init__(x,y,color,1)
        self.value = 31*self.color
    
    def get_moves(self):
        return [Vec2(1,1), Vec2(-1,-1), Vec2(1,-1), Vec2(-1,1)]

class Queen(Chesspiece):
    position_values = [[-20,-10,-10, -5, -5,-10,-10,-20],
                        [-10,  0,  5,  0,  0,  0,  0,-10],
                        [-10,  5,  5,  5,  5,  5,  0,-10],
                        [-5,  0,  5,  5,  5,  5,  0, 0],
                        [-5,  0,  5,  5,  5,  5,  0, -5],
                        [-10,  0,  5,  5,  5,  5,  0,-10],
                        [-10,  0,  0,  0,  0,  0,  0,-10],
                        [-20,-10,-10, -5, -5,-10,-10,-20]]
    def __init__(self, x, y, color):#1-white -1-black
        super().__init__(x,y,color,1)
        self.value = 90*self.color
    
    def get_moves(self):
        return [Vec2(1,0), Vec2(-1,0), Vec2(0,1), Vec2(0,-1), Vec2(1,1), Vec2(-1,-1), Vec2(1,-1), Vec2(-1,1)]

class King(Chesspiece):
    position_values = [[20, 30, 10,  0,  0, 10, 30, 20],
                        [20, 20,  0,  0,  0,  0, 20, 20],
                        [-10,-20,-20,-20,-20,-20,-20,-10],
                        [-20,-30,-30,-40,-40,-30,-30,-20],
                        [-30,-40,-40,-50,-50,-40,-40,-30],
                        [-30,-40,-40,-50,-50,-40,-40,-30],
                        [-30,-40,-40,-50,-50,-40,-40,-30],
                        [-30,-40,-40,-50,-50,-40,-40,-30]]
    def __init__(self, x, y, color):#1-white -1-black
        super().__init__(x,y,color)
        self.value = 900*self.color
    
    def get_moves(self):
        return [Vec2(1,0), Vec2(-1,0), Vec2(0,1), Vec2(0,-1), Vec2(1,1), Vec2(-1,-1), Vec2(1,-1), Vec2(-1,1)]

if __name__ == "__main__":
    a = King(4, 0, WHITE)
    b = King(3, 7, BLACK)
    print(a.get_position_value())
    print(b.get_position_value())