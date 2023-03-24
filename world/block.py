from utils.transform import identity, translate
from world.ocean.ocean import Ocean
from world.terrain.terrain import Terrain
import OpenGL.GL as GL

class Chunk:
    def __init__(self, size, scale_factor):
        self.model_matrices = dict()
        translation_factor = (size-1)*scale_factor
        N = 4 
        for i in range (-N, N):
            for j in range(-N, N):
                self.model_matrices[(i,j)]= translate((i*translation_factor, 0.0, j*translation_factor))
        self.terrain_mesh = Terrain(size=size, scale_factor=scale_factor, model_matrices=self.model_matrices)
        self.ocean_mesh = Ocean(size, model_matrices=self.model_matrices)

    def update(self, t):
        self.ocean_mesh.update(t)
    
    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        self.ocean_mesh.draw(primitives=primitives, **uniforms)
        self.terrain_mesh.draw(primitives=primitives,  **uniforms)