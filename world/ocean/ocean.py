from core import Shader
from world.ocean.ocean_fft import FFT
from world.ocean.ocean_grid import OceanGrid
from utils.primitives import Grid
import OpenGL.GL as GL

class Ocean:
    def __init__(self, size):
        self.size = size
        self.ocean_grid = OceanGrid(size, 256, 20.0)
        self.fft = FFT()
        self.grid = Grid(Shader("world/ocean/shaders/ocean.vert", "world/ocean/shaders/ocean.frag"), size)

    def draw(self, t,  primitives=GL.GL_TRIANGLES, **uniforms):
        self.fft.update(t, self.ocean_grid)

        self.grid.draw(primitives=primitives, displacement=self.ocean_grid.displacement_text, gradients=self.ocean_grid.gradients_text, wind_speed=self.ocean_grid.wind_speed, wind_direction=self.ocean_grid.wind_direction, **uniforms)