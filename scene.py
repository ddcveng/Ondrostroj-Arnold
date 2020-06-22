import pyglet
from constants import *
from chesspiece import *
import game, board
from arnold import ChessPlayer
class Menu:
    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self.buttons = []
        self.animation = pyglet.resource.animation('ondro.gif')
        self.title = pyglet.sprite.Sprite(
            self.animation,
            x = (WIDTH-self.animation.get_max_width())/2,
            y = HEIGHT * 3 / 4,
            batch = self.batch
        )
        for i in range(3):
            img = pyglet.resource.image(
                f"B_{i}.png"
            )
            self.buttons.append(
                pyglet.sprite.Sprite(
                    img,
                    x=(i+1)*(WIDTH-3*img.width)/4 + i*img.width,
                    y=HEIGHT/5,
                    batch=self.batch,
                )
            )

    def draw(self):
        self.batch.draw()

    def on_click(self, x, y, button, modifiers):
        #print(f"GG{x} {y}")
        for i, sprite in enumerate(self.buttons):
            print(f"{sprite.x} {sprite.y}")
            distx = x - sprite.x
            disty = y-sprite.y
            if distx > 0 and distx < sprite.width and disty > 0 and disty < sprite.height:
                if i == 0:
                    return Game_Scene(HUMAN, HUMAN)
                elif i == 1:
                    bot = ChessPlayer(None, BLACK, DEPTH, MAXDEPTH)
                    return Game_Scene(HUMAN, bot)
                elif i == 2:
                    black = ChessPlayer(None, BLACK, DEPTH, MAXDEPTH)
                    white = ChessPlayer(None, WHITE, DEPTH, MAXDEPTH)
                    return Game_Scene(white, black)
        return self

class Game_Scene:
    def __init__(self, white, black):
        self.batch = pyglet.graphics.Batch()
        self.board = board.Chessboard()
        if white != HUMAN:
            white.board = self.board
        if black != HUMAN:
            black.board = self.board
        self.game = game.Game(self.board, white, black)
        self.coords = []
        self.board_markings = []
        self.set_intial_values()
        self.graveyard = {WHITE:{Pawn:0, Knight:0, Bishop:0, Rook:0, Queen:0},
                          BLACK:{Pawn:0, Knight:0, Bishop:0, Rook:0, Queen:0}}
        self.game.clock.schedule_once(self.game.manage_robots, 0.5)
    
    def set_intial_values(self):
        self.calculate_grid_squares()
        self.setup_sprites()
        self.setup_text()
    
    def calculate_grid_squares(self):
        for i in range(0, 8):
            for j in range(i % 2, 8, 2):
                self.coords += [
                    OFFSET+GRID_SIZE*j,     OFFSET+GRID_SIZE*i,
                    OFFSET+GRID_SIZE*(j+1), OFFSET+GRID_SIZE*i,
                    OFFSET+GRID_SIZE*(j+1), OFFSET+GRID_SIZE*(i+1),
                    OFFSET+GRID_SIZE*j,     OFFSET+GRID_SIZE*(i+1)
                ]
    
    def setup_sprites(self):
        for i in range(8):
            for j in range(8):
                piece = self.board.data[i][j]
                if piece:
                    img = pyglet.resource.image(
                        f"{type(piece).__name__}_{piece.color}.png")
                    sprite = pyglet.sprite.Sprite(img,
                                        x=i*GRID_SIZE+CENTER_CONST,
                                        y=j*GRID_SIZE+CENTER_CONST,
                                        batch=self.batch)
                    piece.sprite = sprite
    
    def setup_text(self):
        self.game_over = pyglet.text.Label(
                            text="",
                            bold=1,
                            font_size=GRID_SIZE,
                            x=WIDTH/2+OFFSET,
                            y=HEIGHT/2,
                            anchor_x="left",
                            anchor_y="bottom",
                            color=(255, 205, 0, 255),
                            batch = self.batch)
        self.turn_text = pyglet.text.Label(
                            text=T_TURN[WHITE],
                            font_size = GRID_SIZE,
                            x = WIDTH/2+GRID_SIZE,
                            y = HEIGHT/2,
                            anchor_x="left",
                            anchor_y="top",
                            color=C_TURN[WHITE],
                            batch = self.batch)
        self.last_move_text = pyglet.text.Label(
                            text="",
                            font_size = GRID_SIZE,
                            x = WIDTH/2 + GRID_SIZE + OFFSET,
                            y = HEIGHT/2 - GRID_SIZE - OFFSET,
                            anchor_x="left",
                            anchor_y="top",
                            color=C_TURN[BLACK],
                            batch = self.batch)
        for i in range(8):
            self.board_markings.append(pyglet.text.Label(
                text=chr(ASCII_OFFSET+i),
                font_size=GRID_SIZE//5,
                x = OFFSET+CENTER_CONST+i*GRID_SIZE,
                y = OFFSET//2,
                anchor_x="center",
                anchor_y="center",
                color=C_TURN[BLACK],
                batch = self.batch
            ))
            self.board_markings.append(pyglet.text.Label(
                text=chr(i+DECODE_OFFSET),
                font_size=GRID_SIZE//5,
                x = OFFSET//2,
                y = OFFSET+CENTER_CONST+i*GRID_SIZE,
                anchor_x="center",
                anchor_y="center",
                color=C_TURN[BLACK],
                batch = self.batch
            ))
    
    def update_text(self):
        #game over
        if self.game.over:
            self.game_over.text = f"{T_TURN[self.game.over]} wins"
            #self.game_over.draw()
        self.turn_text.text = f"{T_TURN[self.game.turn]} turn"
        self.turn_text.color = C_TURN[self.game.turn]
        #self.turn_text.draw()
        if self.game.last_move:
            self.last_move_text.text = f"{self.board.coords_to_chess(self.game.last_move.x)} -> {self.board.coords_to_chess(self.game.last_move.y)}"
            self.last_move_text.color = C_TURN[-self.game.turn]
    
    def move_dead_pieces(self, piece):
        if piece:
            if isinstance(piece, King):
                self.game.over = -piece.color
                return
            x = 0
            for key, value in self.graveyard[piece.color].items():
                x += value
                if isinstance(piece, key):
                    break
            y = 7 if piece.color == WHITE else 6
            piece.sprite.update(x=x*(OFFSET+5)+WIDTH//2, y=y*GRID_SIZE+CENTER_CONST)
            piece.alive = 0
            self.graveyard[piece.color][type(piece)] += 1
            for p in self.board.pieces[piece.color]:
                if abs(p.value) > abs(piece.value) and p.alive == 0:
                    p.sprite.x += OFFSET+5
        return 0

    def draw(self):
        self.game.dead = self.move_dead_pieces(self.game.dead)
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                            ('v2f', [OFFSET, OFFSET, WIDTH/2-OFFSET-1, OFFSET, WIDTH/2-OFFSET-1, HEIGHT-OFFSET-1, OFFSET, HEIGHT-OFFSET-1]),
                            ('c3B', [255, 255, 255]*4))
        # black squares in the front
        pyglet.graphics.draw(128, pyglet.gl.GL_QUADS,
                            ('v2f', self.coords),
                            ('c3B', [191, 112, 48]*128))
        # avilable moves
        pyglet.graphics.draw(self.game.num_vertexes, 
                            pyglet.gl.GL_QUADS, 
                            ('v2f', self.game.highlight_coords),
                            ('c3f', [0, 255, 0]*self.game.num_vertexes))
        # check if a king is in danger
        check = self.board.check
        if check:
            kingx = check.pos.x
            kingy = check.pos.y
            pyglet.graphics.draw(4,
                                pyglet.gl.GL_QUADS,
                                ('v2f', [kingx*GRID_SIZE + OFFSET,
                                        kingy*GRID_SIZE+OFFSET,
                                        kingx*GRID_SIZE + OFFSET, 
                                        (kingy+1) * GRID_SIZE+OFFSET,
                                        (kingx+1)*GRID_SIZE + OFFSET, 
                                        (kingy+1) * GRID_SIZE+OFFSET,
                                        (kingx+1)*GRID_SIZE+OFFSET, 
                                        kingy*GRID_SIZE+OFFSET]),
                                ('c3B', [255, 0, 0]*4))
        self.update_text()
        # chesspieces
        self.batch.draw()
    
    def on_click(self, x, y, button, modifiers):
        if self.game.over:
            return Menu()
        x = (x-OFFSET)//GRID_SIZE
        y = (y-OFFSET)//GRID_SIZE
        pos = Vec2(x, y)
        if self.board.is_on_board(pos):
            if not self.game.active_piece:
                self.game.highlight_moves(x, y)
            else:
                if pos in self.game.highlights:  # if the clicked square is highlited, then move there
                    '''Move piece to highlighted location'''
                    self.game.move_piece(pos)
                    self.game.manage(pos)
                    self.game.end_turn()
                elif self.board.data[pos.x][pos.y]:
                    '''Another piece was selected'''
                    self.game.stop_highlighting()
                    self.game.highlight_moves(x, y)
                else:
                    '''Clicked on an empty square'''
                    self.game.stop_highlighting()
        return self
