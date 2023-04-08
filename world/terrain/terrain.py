from utils.primitives import Grid
import OpenGL.GL as GL

from utils.shaders import Shader
from utils.texture import Texture
from utils.transform import identity, translate              # standard Python OpenGL wrapper
import numpy as np
class Terrain:
    def __init__(self, size, size_factor, model_matrices, N):
        self.size = size
        self.grid = Grid(Shader(vertex_source="world/terrain/shaders/terrain.vert", fragment_source="world/terrain/shaders/terrain.frag"), size=size, size_factor=size_factor)
        self.scale_factor = size_factor
        self.twoN = 2*N
        self.N = N//2
        self.maps = np.zeros(self.twoN * self.twoN, dtype=Texture)
        self.model_matrices = model_matrices
        cs = Shader(compute_source="world/terrain/shaders/cs/terrain.comp.glsl")
        for i in range (-self.N, self.N):
            for j in range(-self.N, self.N):
                index = i* self.twoN + j
                self.maps[index] = self.get_map(model_matrices[index], cs)

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        for i in range (-self.N, self.N):
            for j in range (-self.N, self.N):
                index = i* self.twoN + j
                GL.glActiveTexture(GL.GL_TEXTURE0)
                GL.glBindTexture(self.maps[index].type, self.maps[index].glid)
                self.grid.shader.bind()
                self.grid.shader.set_int("map", 0)
                self.grid.draw(primitives=primitives, model=self.model_matrices[index], **uniforms)


    def get_map(self, model, cs):
        map_text = Texture((self.size,self.size), GL.GL_CLAMP_TO_EDGE, GL.GL_CLAMP_TO_EDGE, GL.GL_LINEAR, GL.GL_LINEAR, GL.GL_RGBA32F, GL.GL_RGBA, is_vec=False)
        cs.bind()
        cs.set_image2d_write("map", map_text)
        cs.set_int("size", self.size)
        cs.set_float("scale_factor", self.scale_factor)
        cs.set_mat4("model", model)
        GL.glDispatchCompute(self.size//16, self.size//16, 1)
        return map_text
