from utils.primitives import Grid
import OpenGL.GL as GL

from utils.shaders import Shader
from utils.texture import Texture
from utils.transform import identity, translate              # standard Python OpenGL wrapper

class Terrain:
    def __init__(self, size, scale_factor, model_matrices):
        self.size = size
        self.grid = Grid(Shader(vertex_source="world/terrain/shaders/terrain.vert", fragment_source="world/terrain/shaders/terrain.frag"), size=size)
        self.scale_factor = scale_factor
        self.maps = dict()
        self.model_matrices = model_matrices
        N = 4
        cs = Shader(compute_source="world/terrain/shaders/cs/terrain.comp.glsl")
        for i in range (-N, N):
            for j in range(-N, N):
                current_model = model_matrices[(i,j)]
                self.maps[(i, j)] = self.get_map(current_model, cs)

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        for tup, map in self.maps.items():
            GL.glActiveTexture(GL.GL_TEXTURE0)
            GL.glBindTexture(map.type, map.glid)
            self.grid.shader.bind()
            self.grid.shader.set_int("map", 0)
            self.grid.draw(primitives=primitives, model=self.model_matrices[tup], **uniforms)


    def get_map(self, model, cs):
        map_text = Texture((self.size,self.size), GL.GL_CLAMP_TO_EDGE, GL.GL_CLAMP_TO_EDGE, GL.GL_LINEAR, GL.GL_LINEAR, GL.GL_RGBA32F, GL.GL_RGBA, is_vec=False)
        cs.bind()
        cs.set_image2d_write("map", map_text)
        cs.set_int("size", self.size)
        cs.set_float("scale_factor", self.scale_factor)
        cs.set_mat4("model", model)
        GL.glDispatchCompute(self.size//16, self.size//16, 1)
        return map_text
