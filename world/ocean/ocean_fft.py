from utils.shaders import Shader
from utils.texture import Texture
import OpenGL.GL as GL
from enum import Enum

class Step(Enum):
    HEIGHT_FIELD = 1
    CHOPPY_FIELD = 2

# set of textures used to run the algorithm of FFT on gpu
class TexturesFFT:
    def __init__(self, N):
        self.tilde_hkt = Texture((N, N), GL.GL_REPEAT, GL.GL_REPEAT, GL.GL_LINEAR, GL.GL_LINEAR, GL.GL_RG32F, GL.GL_RG, is_vec=False)
        self.dt_dxdz = Texture((N, N), GL.GL_REPEAT, GL.GL_REPEAT, GL.GL_LINEAR, GL.GL_LINEAR, GL.GL_RG32F, GL.GL_RG, is_vec=False)
        self.temp_text = Texture((N, N), GL.GL_REPEAT, GL.GL_REPEAT, GL.GL_LINEAR, GL.GL_LINEAR, GL.GL_RG32F, GL.GL_RG, is_vec=False)


class FFT:
    def __init__(self):
        repo = "world/ocean/shaders/cs/"
        format = ".comp.glsl"
        self.hk_cs = Shader(compute_source='{repo}fft_hkt{format}'.format(repo=repo, format=format))
        self.butterfly_cs = Shader(compute_source='{repo}fft_butterfly{format}'.format(repo=repo, format=format))
        self.inversion_cs = Shader(compute_source='{repo}fft_inversion{format}'.format(repo=repo, format=format))
        self.gradient_cs = Shader(compute_source='{repo}fft_gradients{format}'.format(repo=repo, format=format))
        self.temp_textures = TexturesFFT(256)

    def fft_d(self, step, ocean_grid):
        if step == Step.HEIGHT_FIELD:
            self.butterfly_cs.bind()
            self.butterfly_cs.set_uniforms(dict(log2_N=ocean_grid.log2_N, N=ocean_grid.N))
            self.butterfly_cs.set_image2d_read("readbuff", self.temp_textures.tilde_hkt)
            self.butterfly_cs.set_image2d_write("writebuff", self.temp_textures.temp_text)

            GL.glDispatchCompute(ocean_grid.N, 1, 1)
            GL.glMemoryBarrier(GL.GL_SHADER_IMAGE_ACCESS_BARRIER_BIT);

            self.butterfly_cs.set_image2d_read("readbuff", self.temp_textures.temp_text)
            self.butterfly_cs.set_image2d_write("writebuff", self.temp_textures.tilde_hkt)

            GL.glDispatchCompute(ocean_grid.N, 1, 1)
            GL.glMemoryBarrier(GL.GL_SHADER_IMAGE_ACCESS_BARRIER_BIT);

        elif step == Step.CHOPPY_FIELD:
            self.butterfly_cs.bind()
            self.butterfly_cs.set_uniforms(dict(log2_N=ocean_grid.log2_N, N=ocean_grid.N))
            self.butterfly_cs.set_image2d_read("readbuff", self.temp_textures.dt_dxdz)
            self.butterfly_cs.set_image2d_write("writebuff", self.temp_textures.temp_text)

            GL.glDispatchCompute(ocean_grid.N, 1, 1)
            GL.glMemoryBarrier(GL.GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

            self.butterfly_cs.set_image2d_read("readbuff", self.temp_textures.temp_text)
            self.butterfly_cs.set_image2d_write("writebuff", self.temp_textures.dt_dxdz)

            GL.glDispatchCompute(ocean_grid.N, 1, 1)

    def update(self, t, ocean_grid):
        
        self.hk_cs.bind()
        self.hk_cs.set_uniforms(dict(N=ocean_grid.N, L=ocean_grid.L, t=t))
        self.hk_cs.set_image2d_write ("tilde_hkt_dy", self.temp_textures.tilde_hkt)
        self.hk_cs.set_image2d_write("Dt_dx_dz", self.temp_textures.dt_dxdz)
        self.hk_cs.set_image2d_read("tilde_h0k", ocean_grid.h0_text)

        GL.glDispatchCompute(ocean_grid.N//16, ocean_grid.N//16, 1)
        GL.glMemoryBarrier(GL.GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

        self.fft_d(Step.HEIGHT_FIELD, ocean_grid=ocean_grid)
        self.fft_d(Step.CHOPPY_FIELD, ocean_grid=ocean_grid)

        self.inversion_cs.bind()
        self.inversion_cs.set_uniforms(dict(N=ocean_grid.N))
        self.inversion_cs.set_image2d_write("displacement", ocean_grid.displacement_text)
        self.inversion_cs.set_image2d_read("height_field", self.temp_textures.tilde_hkt)
        self.inversion_cs.set_image2d_read("choppy_field", self.temp_textures.dt_dxdz)

        GL.glDispatchCompute(ocean_grid.N//16, ocean_grid.N//16, 1)
        GL.glMemoryBarrier(GL.GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

        self.gradient_cs.bind()
        self.gradient_cs.set_uniforms(dict(N=ocean_grid.N, L=ocean_grid.L))
        self.gradient_cs.set_image2d_read("displacement", ocean_grid.displacement_text)
        self.gradient_cs.set_image2d_write("gradients", ocean_grid.gradients_text)

        GL.glDispatchCompute(ocean_grid.N//16, ocean_grid.N//16, 1)
        GL.glMemoryBarrier(GL.GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

