#!/usr/bin/env python

import pyglet
from engine.constants import *
from engine.game import Game
from engine.board import Chessboard
from engine.renderer import Renderer
from player.arnold import ChessPlayer

def main():
    board = Chessboard()
    #arnold = ChessPlayer(board, BLACK, 3)
    game = Game(board, HUMAN, HUMAN)
    Renderer(WIDTH, HEIGHT, game)
    pyglet.app.run()

if __name__ == "__main__":
    main()