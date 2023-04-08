from utils.shaders import Shader
from utils.texture import Texture
from world.ocean.ocean_fft import FFT
from world.ocean.ocean_grid import OceanGrid
from utils.primitives import Grid
import OpenGL.GL as GL
import numpy as np

class Ocean:
    def __init__(self, size, model_matrices, size_factor, number_grids):
        self.size = size
        self.ocean_grid = OceanGrid(size, 256)
        self.fft = FFT()
        self.grid = Grid(Shader(vertex_source="world/ocean/shaders/ocean.vert", fragment_source="world/ocean/shaders/ocean.frag"), size=size, size_factor=size_factor)
        self.t = 0.0

        ssbo_loc = GL.glGetProgramResourceIndex(self.grid.shader.glid, GL.GL_SHADER_STORAGE_BLOCK, "model_matrices")
        GL.glShaderStorageBlockBinding(self.grid.shader.glid, ssbo_loc, 8)
        
        
        self.ssbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_SHADER_STORAGE_BUFFER, self.ssbo)
        self.model_matrices = model_matrices
        print(self.model_matrices)
        GL.glBufferData(GL.GL_SHADER_STORAGE_BUFFER, self.model_matrices.nbytes, self.model_matrices, GL.GL_STATIC_DRAW)
        GL.glBindBufferBase(GL.GL_SHADER_STORAGE_BUFFER, 8, self.ssbo)

        self.grid.vertex_array.arguments = (self.grid.vertex_array.index_buffer.size, GL.GL_UNSIGNED_INT, None, number_grids)

    def update(self, t):
        self.t = t
        self.fft.update(t, self.ocean_grid)

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):

        # binding updated textures 
        self.grid.shader.bind()
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(self.ocean_grid.displacement_text.type, self.ocean_grid.displacement_text.glid)

        GL.glActiveTexture(GL.GL_TEXTURE1)
        GL.glBindTexture(self.ocean_grid.gradients_text.type, self.ocean_grid.gradients_text.glid)
        self.grid.shader.set_int("displacement", 0)
        self.grid.shader.set_int("gradients", 1)
        self.grid.draw(primitives=primitives, wind_speed=self.ocean_grid.wind_speed, t = self.t, wind_dir=self.ocean_grid.wind_direction, draw_command=GL.glDrawElementsInstanced,**uniforms)