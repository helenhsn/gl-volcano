from utils.primitives import Cube
from utils.shaders import Shader
import OpenGL.GL as GL

from utils.texture import Texture

class Skybox:
    def __init__(self, size):
        self.size = size
        self.shader = Shader(vertex_source="world/skybox/shaders/skybox.vert", fragment_source="world/skybox/shaders/skybox.frag")
        self.cube = Cube(shader=self.shader,r=size)
        self.cubemap_text = Texture(cubemap_faces=["right", "left", "top", "bottom", "back", "front"])

        
    def draw(self, view, proj):
        self.shader.bind()

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(self.cubemap_text.type, self.cubemap_text.glid)
        self.shader.set_int("cubemap", 0)

        self.shader.set_mat4("view", view)
        self.shader.set_mat4("proj", proj)

        self.cube.draw()
