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

class Pawn(Chesspiece):
    def __init__(self, x, y, color):
        super().__init__(x,y,color)
        self.value = 10*self.color
    
    def get_moves(self):
        temp = [Vec2(0,self.color)]
        if (self.pos.y == 1 and self.color == 1) or (self.pos.y == 6 and self.color == -1):
            temp.append(Vec2(0,2*self.color))
        return temp

class Rook(Chesspiece):
    def __init__(self, x, y, color):#1-white -1-black
        super().__init__(x,y,color,1)
        self.value = 50*self.color
    
    def get_moves(self):
        return [Vec2(1,0), Vec2(-1,0), Vec2(0,1), Vec2(0,-1)]

class Knight(Chesspiece):
    def __init__(self, x, y, color):#1-white -1-black
        super().__init__(x,y,color)
        self.value = 30*self.color
    
    def get_moves(self):
        return [Vec2(1,2), Vec2(-1,2), Vec2(2,1), Vec2(-2,1),
                Vec2(1,-2), Vec2(-1,-2), Vec2(2,-1), Vec2(-2,-1)]

class Bishop(Chesspiece):
    def __init__(self, x, y, color):#1-white -1-black
        super().__init__(x,y,color,1)
        self.value = 30*self.color
    
    def get_moves(self):
        return [Vec2(1,1), Vec2(-1,-1), Vec2(1,-1), Vec2(-1,1)]

class Queen(Chesspiece):
    def __init__(self, x, y, color):#1-white -1-black
        super().__init__(x,y,color,1)
        self.value = 90*self.color
    
    def get_moves(self):
        return [Vec2(1,0), Vec2(-1,0), Vec2(0,1), Vec2(0,-1), Vec2(1,1), Vec2(-1,-1), Vec2(1,-1), Vec2(-1,1)]

class King(Chesspiece):
    def __init__(self, x, y, color):#1-white -1-black
        super().__init__(x,y,color)
        self.value = 900*self.color
    
    def get_moves(self):
        return [Vec2(1,0), Vec2(-1,0), Vec2(0,1), Vec2(0,-1), Vec2(1,1), Vec2(-1,-1), Vec2(1,-1), Vec2(-1,1)]