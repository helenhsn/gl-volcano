from utils.primitives import Grid
import OpenGL.GL as GL

from utils.shaders import Shader              # standard Python OpenGL wrapper

class Terrain:
    def __init__(self, size):
        self.size = size
        self.grid = Grid(Shader(vertex_source="world/terrain/shaders/terrain.vert", fragment_source="world/terrain/shaders/terrain.frag"), size=size)

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        self.grid.draw(primitives=primitives, **uniforms)
