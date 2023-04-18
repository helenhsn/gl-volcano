import ctypes
from random import random, uniform
from struct import pack
import OpenGL.GL as GL
import numpy as np
from utils.shaders import Shader
from utils.texture import Texture
from math import pi, sin, cos

class SplashParticleSystem:
    """
    Class handling the splash particles system.
    """
    def __init__(self):

        # initializing particles positions & speed
        self.nb_particles = 1024

        self.velocities = np.zeros((self.nb_particles, 4), dtype=np.float32)
        self.positions = [(uniform(-10.0, 10.0), 1370.0, uniform(-10.0, 10.0), uniform(25.0, 50.0)) for _ in range(self.nb_particles)]

        
        R = 20.0

        for i in range(self.nb_particles):
            phi = uniform(-pi/12.0, pi/4.0)
            theta = uniform(pi/4.0, pi)

            speed_slope_x = R * sin(phi) * cos(theta) * uniform(2.0, 10.0)
            speed_slope_y = R * cos(phi) * uniform(1.0, 8.0)
            speed_slope_z = R * sin(phi) * sin(theta) * uniform(2.0, 10.0)
            self.velocities[i] = (speed_slope_x, speed_slope_y, speed_slope_z, 0.0) # zero padding for the ssbo

        self.init_pos = self.positions.copy()
        self.init_vel = self.velocities.copy()


        # init buffers & shader program
        self.shader = Shader(vertex_source="world/particles/splashes/splash.vert", geom_source="world/particles/splashes/splash.geom", fragment_source="world/particles/splashes/splash.frag")
        self.cs = Shader(compute_source="world/particles/splashes/update.comp.glsl")

        # binding the ssbos to the compute shader program && generating buffers
        self.init_ssbos(shader_pgrm=self.cs.glid, attributes=dict(pos=np.array(self.positions, dtype=np.float32), vel=self.velocities, init_pos=np.array(self.init_pos, dtype=np.float32), init_vel=self.init_vel))

        # binding the ssbo containing the positions to the vertex shader
        ssbo_loc = GL.glGetProgramResourceIndex(self.shader.glid, GL.GL_SHADER_STORAGE_BLOCK, "pos")
        GL.glShaderStorageBlockBinding(self.shader.glid, ssbo_loc, 4)

        ssbo_loc = GL.glGetProgramResourceIndex(self.shader.glid, GL.GL_SHADER_STORAGE_BLOCK, "init_pos")
        GL.glShaderStorageBlockBinding(self.shader.glid, ssbo_loc, 6)


    def init_ssbos(self, shader_pgrm, attributes):
        self.buffers = {}  # we will store buffers in a named dict

        buffer_count = 4
        for name, data in attributes.items(): 

            #setting ssbo's binding point
            ssbo_loc = GL.glGetProgramResourceIndex(shader_pgrm, GL.GL_SHADER_STORAGE_BLOCK, name)
            GL.glShaderStorageBlockBinding(shader_pgrm, ssbo_loc, buffer_count)
            
            
            self.buffers[name] = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_SHADER_STORAGE_BUFFER, self.buffers[name])

            GL.glBufferData(GL.GL_SHADER_STORAGE_BUFFER, data.nbytes, data, GL.GL_DYNAMIC_DRAW)
            GL.glBindBufferBase(GL.GL_SHADER_STORAGE_BUFFER, buffer_count, self.buffers[name])
            
            buffer_count+=1
        
        GL.glMemoryBarrier(GL.GL_SHADER_STORAGE_BARRIER_BIT)



    def execute(self):
        # optionally update the data attribute VBOs, useful for e.g. particles
        GL.glDrawArrays(GL.GL_POINTS, 0, self.nb_particles)

    def draw(self, dt, camera):

        # updating particles
        self.cs.bind()
        self.cs.set_float("dt", dt)
        GL.glDispatchCompute(self.nb_particles//16, 1, 1)
        GL.glMemoryBarrier(GL.GL_SHADER_STORAGE_BARRIER_BIT)

        # rendering particles

        # binding atlas
        self.shader.bind()
        self.shader.set_uniforms(dict(view=camera.view, proj=camera.proj, up=camera.up, rgt=camera.rgt))

        # draw
        self.execute()

