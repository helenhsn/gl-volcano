from core import Shader
from primitives import Grid
import OpenGL.GL as GL              # standard Python OpenGL wrapper

class Terrain:
    def __init__(self, size):
        self.size = size
        self.grid = Grid(Shader("terrain/terrain.vert", "terrain/terrain.frag"), size)
    
    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        self.grid.draw(primitives=primitives, **uniforms)
