import pyglet
from pyglet.window import mouse
from constants import *
import game as g
from chesspiece import Vec2, Pawn

"""todo: move board out of game"""

pyglet.resource.path = ['res']
pyglet.resource.reindex()

window = pyglet.window.Window(width=WIDTH, height=HEIGHT)

game = g.Game()

# figurke
batch = pyglet.graphics.Batch()
for i in range(8):
    for j in range(8):
        piece = game.board.data[i][j]
        if piece:
            img = pyglet.resource.image(
                f"{type(piece).__name__}_{piece.color}.png")
            sprite = pyglet.sprite.Sprite(img,
                                          x=i*GRID_SIZE+OFFSET +
                                          (GRID_SIZE-img.width)/2,
                                          y=j*GRID_SIZE+OFFSET +
                                          (GRID_SIZE-img.height)/2,
                                          batch=batch)
            piece.sprite = sprite

coords = []
for i in range(0, 8):
    for j in range(i % 2, 8, 2):
        coords += [
            OFFSET+GRID_SIZE*j,     OFFSET+GRID_SIZE*i,
            OFFSET+GRID_SIZE*(j+1), OFFSET+GRID_SIZE*i,
            OFFSET+GRID_SIZE*(j+1), OFFSET+GRID_SIZE*(i+1),
            OFFSET+GRID_SIZE*j,     OFFSET+GRID_SIZE*(i+1)
        ]

game_over = pyglet.text.Label(text="",
                              bold=1,
                              font_size=WIDTH//10,
                              x=WIDTH*0.075,
                              y=0.45*HEIGHT,
                              anchor_x="left",
                              anchor_y="bottom",
                              color=(128, 0, 128, 255))


@window.event
def on_draw():
    window.clear()

    # background
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', [
                         0, 0, WIDTH, 0, WIDTH, HEIGHT, 0, HEIGHT]), ('c3B', [128, 0, 128]*4))
    # chessboard
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', [
                         OFFSET, OFFSET, WIDTH-OFFSET, OFFSET, WIDTH-OFFSET, HEIGHT-OFFSET, OFFSET, HEIGHT-OFFSET]), ('c3B', [255, 255, 255]*4))
    pyglet.graphics.draw(128, pyglet.gl.GL_QUADS,
                         ('v2f', coords), ('c3B', [191, 112, 48]*128))
    # avilable moves
    pyglet.graphics.draw(game.num_vertexes, pyglet.gl.GL_QUADS, ('v2f',
                                                                 game.highlight_coords), ('c3f', [0, 255, 0]*game.num_vertexes))
    # check if a king is in danger
    if game.board.check:
        kingx = game.board.check.pos.x
        kingy = game.board.check.pos.y
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', [kingx*GRID_SIZE+OFFSET, kingy*GRID_SIZE+OFFSET,
                                                             kingx*GRID_SIZE +
                                                             OFFSET, (kingy+1) *
                                                             GRID_SIZE+OFFSET,
                                                             (kingx+1)*GRID_SIZE +
                                                             OFFSET, (kingy+1) *
                                                             GRID_SIZE+OFFSET,
                                                             (kingx+1)*GRID_SIZE+OFFSET, kingy*GRID_SIZE+OFFSET]),
                             ('c3B', [255, 0, 0]*4))
    # chesspieces
    batch.draw()

    # game over
    if game.over:
        game_over.text = "WHITE WINS" if game.board.check.color == BLACK else "BLACK WINS"
        game_over.draw()


@window.event
def on_mouse_press(x, y, button, modifiers):
    if game.over:
        window.close()
        return
    x = (x-OFFSET)//GRID_SIZE
    y = (y-OFFSET)//GRID_SIZE
    pos = Vec2(x, y)
    if game.board.is_on_board(pos):
        if not game.active_piece:
            game.highlight_moves(x, y)
        else:
            if pos in game.highlights:  # if the clicked square is highlited, then move there
                game.active_piece.sprite.x = x*GRID_SIZE+CENTER_CONST
                game.active_piece.sprite.y = y*GRID_SIZE+CENTER_CONST

                take = game.board.data[x][y]
                if take:
                    take.sprite.batch = None
                    take.pos = Vec2(-1, -1)
                    take.alive = 0
                game.board.data[x][y] = game.active_piece
                game.board.data[game.active_piece.pos.x][game.active_piece.pos.y] = 0
                game.active_piece.pos = pos

                # check
                enemy_king = game.board.black_pieces[11] if game.active_piece.color == WHITE else game.board.white_pieces[11]
                if game.board.can_endanger(enemy_king.pos, game.active_piece):
                    game.board.check = enemy_king
                    game.over = game.board.checkmate()
                elif game.board.check:
                    game.board.check = None

                if isinstance(game.active_piece, Pawn) and game.active_piece.moved == 0:
                    game.active_piece.moved = 1

                # enpassant
                t = game.board.enpassant
                if t:
                    t.x.sprite.batch = None
                    game.board.data[t.y.x][t.y.y] = 0

                # castling
                castle_rook = None
                if game.board.castle.x == pos:
                    castle_rook = game.board.white_pieces[8] if game.turn == WHITE else game.board.black_pieces[15]
                    pos.x = pos.x+game.turn
                elif game.board.castle.y == pos:
                    castle_rook = game.board.white_pieces[15] if game.turn == WHITE else game.board.black_pieces[8]
                    pos.x = pos.x-game.turn
                if castle_rook:
                    castle_rook.sprite.x = pos.x*GRID_SIZE+CENTER_CONST
                    castle_rook.sprite.y = pos.y*GRID_SIZE+CENTER_CONST
                    game.board.data[pos.x][pos.y] = castle_rook
                    game.board.data[castle_rook.pos.x][castle_rook.pos.y] = 0
                    castle_rook.pos = pos

                game.turn = -game.turn
                game.stop_highlighting()
            elif game.board.data[pos.x][pos.y]:
                game.stop_highlighting()
                game.highlight_moves(x, y)
            else:
                game.stop_highlighting()


pyglet.app.run()
