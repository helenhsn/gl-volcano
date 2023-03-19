from world.ocean.ocean import Ocean
from world.terrain.terrain import Terrain
import OpenGL.GL as GL

class Chunk:
    def __init__(self, size):
        #self.ocean_mesh = Ocean(size)
        self.terrain_mesh = Terrain(size)
    
    def draw(self, t, primitives=GL.GL_TRIANGLES, **uniforms):
        #self.ocean_mesh.draw(t, primitives=primitives, **uniforms, t=t)
        self.terrain_mesh.draw(primitives=primitives, **uniforms)