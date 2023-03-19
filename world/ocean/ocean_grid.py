
from utils.texture import Texture
from utils.transform import normalized, vec, length_sq
from math import log2, pi, sqrt, exp
import numpy as np
import OpenGL.GL as GL


SIZE = (256+1)*(256+1)
TWO_PI = 2*pi

class OceanGrid:
    def __init__(self, L, N, A):
        self.L = L
        self.N = N
        self.log2_N = log2(N)
        self.A = A
        self.wind_direction = vec(1.0, 1.0)
        self.wind_speed = 40.0
        self.h0_text = self.init_h0k_text()
        self.displacement_text = Texture.new_from_none((N, N), GL.GL_CLAMP_TO_EDGE, GL.GL_CLAMP_TO_EDGE, GL.GL_LINEAR, GL.GL_LINEAR, GL.GL_RGBA32F, GL.GL_RGBA)
        self.gradients_text = Texture.new_from_none((N, N), GL.GL_CLAMP_TO_EDGE, GL.GL_CLAMP_TO_EDGE, GL.GL_LINEAR, GL.GL_LINEAR, GL.GL_RGBA32F, GL.GL_RGBA)
    
    def phillips_spectrum(self, k, win_dir_n):
        
        V = self.wind_speed
        L = (V*V)/9.81

        k_n = normalized(k)
        k_dot_w = np.dot(k, win_dir_n)
        mag_sq = length_sq(k)
        l = L/2000.0
        P_h = self.A * exp(-1.0/(mag_sq*l*l)) * exp(-mag_sq*l*l) * (k_dot_w*k_dot_w*k_dot_w*k_dot_w*k_dot_w*k_dot_w) / (2.0*mag_sq*mag_sq)
        
        return P_h

    

    def init_h0k_text(self):
        win_dir_n = normalized(self.wind_direction)
        k = vec(0.0, 0.0)
        half = self.N/2

        h0 = np.empty((SIZE, 2))

        N_plus_1 = self.N + 1

        for m in range(0,N_plus_1):
            k[1] = TWO_PI * (half - m) / self.L
            for n in range(0, N_plus_1):
                k[0] = TWO_PI * (half - n) / self.L
                index = m*(self.N+1)+n
                sqrt_P_h = 0.0
                if k[0] != 0.0 and k[1] != 0.0:
                    sqrt_P_h = sqrt(self.phillips_spectrum(k=k, win_dir_n=win_dir_n))
                h0_real = np.random.normal()*sqrt_P_h
                h0_im = np.random.normal()*sqrt_P_h

                h0[index] = (h0_real, h0_im)
        
        return Texture.new_from_vec(vec(N_plus_1, N_plus_1), GL.GL_REPEAT, GL.GL_REPEAT, GL.GL_NEAREST, GL.GL_NEAREST, GL.GL_RG32F, GL.GL_RG, h0)

                



