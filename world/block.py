from world.ocean.ocean import Ocean
from world.terrain.terrain import Terrain
import OpenGL.GL as GL

class Chunk:
    def __init__(self, size):
        self.ocean_mesh = Ocean(size)
        self.terrain_mesh = Terrain(size)

    def update(self, t):
        self.ocean_mesh.update(t)
    
    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        self.ocean_mesh.draw(primitives=primitives, **uniforms)
        self.terrain_mesh.draw(primitives=primitives, **uniforms)