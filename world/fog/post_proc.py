import OpenGL.GL as GL
from utils.primitives import Quad
from utils.shaders import Shader
from utils.texture import Texture

class FBO:
    def __init__(self):
        self.glid = GL.glGenFramebuffers(1)
    
    def bind(self):
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.glid)

    def unbind(self):
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
    


class PostProcessing:
    """
    We could have made a more general class to handle all post-processing effects but here we only use this
    to display fog to the screen so...
    """
    def __init__(self, win_size):
        self.shader = Shader(vertex_source="world/fog/shaders/fog.vert", fragment_source="world/fog/shaders/fog.frag")
        self.quad = Quad(self.shader)
        self.fbo = FBO()

        self.fbo.bind()
        # creating 2 textures to store color & depth buffers from the scene
        self.color_text = Texture((win_size[0], win_size[1]), GL.GL_CLAMP_TO_EDGE, GL.GL_CLAMP_TO_EDGE, GL.GL_LINEAR, GL.GL_LINEAR, GL.GL_RGBA8, GL.GL_RGBA, is_fbo=True)
        self.depth_text = Texture((win_size[0], win_size[1]), GL.GL_CLAMP_TO_EDGE, GL.GL_CLAMP_TO_EDGE, GL.GL_LINEAR, GL.GL_LINEAR, GL.GL_DEPTH_COMPONENT24, GL.GL_DEPTH_COMPONENT, is_fbo=True)
        
        # binding the created textures to the fbo
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, self.color_text.glid, 0)
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT, GL.GL_TEXTURE_2D, self.depth_text.glid, 0)

        status = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
        if status != GL.GL_FRAMEBUFFER_COMPLETE:
            print(f"Framebuffer is not complete: {status}")
        self.fbo.unbind()
    
    def draw(self):

        GL.glDisable(GL.GL_DEPTH_TEST)

        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(self.color_text.type, self.color_text.glid)
        GL.glActiveTexture(GL.GL_TEXTURE1)
        GL.glBindTexture(self.depth_text.type, self.depth_text.glid)
        
        self.shader.bind()
        self.shader.set_int("color_text", 0)
        self.shader.set_int("depth_text", 1)
        self.quad.draw()

        GL.glEnable(GL.GL_DEPTH_TEST)

