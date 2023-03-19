#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""

from utils.primitives import Axis
from world.block import Chunk
import sys                          # for system arguments

# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper

from core import Shader, Viewer, Node

from utils.transform import *
from utils.animation import *


# -------------- rotation ----------------------------------------------------
class RotationControlNode(Node):
    def __init__(self, key_up, key_down, axis, angle=0):
        super().__init__(transform=rotate(axis, angle))
        self.angle, self.axis = angle, axis
        self.key_up, self.key_down = key_up, key_down

    def key_handler(self, key):
        self.angle += 5 * int(key == self.key_up)
        self.angle -= 5 * int(key == self.key_down)
        self.transform = rotate(self.axis, self.angle)
        super().key_handler(key)


# -------------- main program and scene setup --------------------------------
def main():
    """ create a window, add scene objects, then run rendering loop """
    CHUNK_SIZE = 1024 #nb of vertices per chunk side
    viewer = Viewer(size=CHUNK_SIZE)

    viewer.add(Chunk(CHUNK_SIZE)) # one mesh grid !
    viewer.add(Axis(Shader("world/ocean/shaders/ocean.vert", "world/ocean/shaders/ocean.frag")))
    # start rendering loop
    viewer.run()


if __name__ == '__main__':
    main()                     # main function keeps variables locally scoped
