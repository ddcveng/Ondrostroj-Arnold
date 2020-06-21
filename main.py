#!/usr/bin/env python

import pyglet
from constants import *
from game import Game
from board import Chessboard
from renderer import Renderer
from arnold import ChessPlayer

def main():
    r = Renderer(WIDTH, HEIGHT)
    pyglet.app.run()

if __name__ == "__main__":
    main()