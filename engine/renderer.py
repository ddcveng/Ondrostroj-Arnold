#usr/bin/env python

import os
from engine.chesspiece import Vec2
import pyglet
from pyglet.window import mouse
from engine.constants import *

class Renderer(pyglet.window.Window):
    def __init__(self, width, height, game):
        super(Renderer, self).__init__(width=width, height=height)
        working_dir = os.path.dirname(os.path.realpath(__file__))
        pyglet.resource.path = [os.path.join(working_dir, 'res')]
        pyglet.resource.reindex()
        self.batch = pyglet.graphics.Batch()
        self.game = game
        self.board = game.board
        # setup sprites with initial parameters
        self.coords = []
        for i in range(0, 8):
            for j in range(i % 2, 8, 2):
                self.coords += [
                    OFFSET+GRID_SIZE*j,     OFFSET+GRID_SIZE*i,
                    OFFSET+GRID_SIZE*(j+1), OFFSET+GRID_SIZE*i,
                    OFFSET+GRID_SIZE*(j+1), OFFSET+GRID_SIZE*(i+1),
                    OFFSET+GRID_SIZE*j,     OFFSET+GRID_SIZE*(i+1)
                ]
        # calculate grid vertexes
        self.batch = pyglet.graphics.Batch()
        for i in range(8):
            for j in range(8):
                piece = self.board.data[i][j]
                if piece:
                    img = pyglet.resource.image(
                        f"{type(piece).__name__}_{piece.color}.png")
                    sprite = pyglet.sprite.Sprite(img,
                                                x=i*GRID_SIZE+OFFSET + (GRID_SIZE-img.width)/2,
                                                y=j*GRID_SIZE+OFFSET + (GRID_SIZE-img.height)/2,
                                                batch=self.batch)
                    piece.sprite = sprite
        # text to show when the game ends    
        self.game_over = pyglet.text.Label(text="",
                              bold=1,
                              font_size=WIDTH//10,
                              x=WIDTH*0.075,
                              y=0.45*HEIGHT,
                              anchor_x="left",
                              anchor_y="bottom",
                              color=(128, 0, 128, 255))
    
    def on_draw(self):
        self.clear()

        # background
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', [
                            0, 0, WIDTH, 0, WIDTH, HEIGHT, 0, HEIGHT]), ('c3B', [128, 0, 128]*4))
        # chessboard
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', [
                            OFFSET, OFFSET, WIDTH-OFFSET, OFFSET, WIDTH-OFFSET, HEIGHT-OFFSET, OFFSET, HEIGHT-OFFSET]), ('c3B', [255, 255, 255]*4))
        pyglet.graphics.draw(128, pyglet.gl.GL_QUADS,
                            ('v2f', self.coords), ('c3B', [191, 112, 48]*128))
        # avilable moves
        pyglet.graphics.draw(self.game.num_vertexes, pyglet.gl.GL_QUADS, ('v2f',
                                                                    self.game.highlight_coords), ('c3f', [0, 255, 0]*self.game.num_vertexes))
        # check if a king is in danger
        check = self.board.check
        if check:
            kingx = check.pos.x
            kingy = check.pos.y
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', [kingx*GRID_SIZE + OFFSET,
                                                                    kingy*GRID_SIZE+OFFSET,
                                                                    kingx*GRID_SIZE + OFFSET, 
                                                                    (kingy+1) * GRID_SIZE+OFFSET,
                                                                    (kingx+1)*GRID_SIZE + OFFSET, 
                                                                    (kingy+1) * GRID_SIZE+OFFSET,
                                                                    (kingx+1)*GRID_SIZE+OFFSET, 
                                                                    kingy*GRID_SIZE+OFFSET]),
                                ('c3B', [255, 0, 0]*4))
        # chesspieces
        self.batch.draw()

        # game over
        if self.game.over:
            self.game_over.text = "WHITE WINS" if self.board.check.color == BLACK else "BLACK WINS"
            self.game_over.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game.over:
            self.close()
            return
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