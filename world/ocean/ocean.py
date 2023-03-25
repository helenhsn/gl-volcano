from utils.shaders import Shader
from utils.texture import Texture
from world.ocean.ocean_fft import FFT
from world.ocean.ocean_grid import OceanGrid
from utils.primitives import Grid
import OpenGL.GL as GL

class Ocean:
    def __init__(self, size, model_matrices):
        self.size = size
        self.ocean_grid = OceanGrid(size, 256, 30.0)
        self.fft = FFT()
        self.grid = Grid(Shader(vertex_source="world/ocean/shaders/ocean.vert", fragment_source="world/ocean/shaders/ocean.frag"), size)
        self.model_matrices = model_matrices

    def update(self, t):
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
        for tup in self.model_matrices.keys():
            self.grid.draw(primitives=primitives, wind_speed=self.ocean_grid.wind_speed, wind_direction=self.ocean_grid.wind_direction, model=self.model_matrices[tup],**uniforms)