from core import Shader
from utils.primitives import Grid
import OpenGL.GL as GL              # standard Python OpenGL wrapper

class Terrain:
    def __init__(self, size):
        self.size = size
        self.grid = Grid(Shader("world/terrain/shaders/terrain.vert", "world/terrain/shaders/terrain.frag"), size)

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        self.grid.draw(primitives=primitives, **uniforms)
