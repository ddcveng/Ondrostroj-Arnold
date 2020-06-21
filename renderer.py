#usr/bin/env python

import os
import pyglet
from pyglet.window import mouse
from chesspiece import *
from constants import *
from scene import Menu

class Renderer(pyglet.window.Window):
    def __init__(self, width, height):
        super(Renderer, self).__init__(width=width, height=height, caption="Chess 2")
        working_dir = os.path.dirname(os.path.realpath(__file__))
        pyglet.resource.path = [os.path.join(working_dir, 'res')]
        pyglet.resource.reindex()
        self.scene = Menu()

    def on_draw(self):
        self.clear()
        # background
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, 
                            ('v2f',[0, 0, WIDTH, 0, WIDTH, HEIGHT, 0, HEIGHT]),
                            ('c3B', [128, 0, 128]*4))
        self.scene.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        self.scene = self.scene.on_click(x, y, button, modifiers)