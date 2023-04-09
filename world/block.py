from utils.transform import identity, translate
from world.ocean.ocean import Ocean
from world.terrain.terrain import Terrain
import numpy as np
import OpenGL.GL as GL

class Chunk:
    def __init__(self, size, size_factor, N):
        twoN = 2*N
        number_grids = twoN * twoN
        self.model_matrices_terrain = np.zeros((number_grids, 4, 4), dtype=np.float32)
        self.model_matrices_ocean = np.zeros((number_grids, 4, 4), dtype=np.float32)
        translation_factor_terrain = (size-1)*size_factor
        translation_factor_ocean = (size-1)*(size_factor+4)
        for i in range (-N, N):
            for j in range(-N, N):
                self.model_matrices_terrain[i * twoN + j] = translate((i*translation_factor_terrain, 0.0, j*translation_factor_terrain))
                self.model_matrices_ocean[i * twoN + j] = translate((i*translation_factor_ocean, 0.0, j*translation_factor_ocean))


        self.terrain_mesh = Terrain(size=size, size_factor=size_factor, model_matrices=self.model_matrices_terrain, N=N)
        self.ocean_mesh = Ocean(size, size_factor=size_factor+4,model_matrices=self.model_matrices_ocean, number_grids=number_grids)

    def update(self, t):
        self.ocean_mesh.update(t)
    
    def draw(self, primitives=GL.GL_TRIANGLES, skybox=None, **uniforms):
        self.ocean_mesh.draw(primitives=primitives, skybox=skybox,**uniforms)
        self.terrain_mesh.draw(primitives=primitives, skybox=skybox, **uniforms)
