
from random import random, uniform
from struct import pack
import OpenGL.GL as GL
import numpy as np
from utils.shaders import Shader
from utils.texture import Texture
from math import pi, sin, cos

class SmokeParticleSystem:
    def __init__(self):

        self.nb_particles = 16384
        
        sample_chisquared = np.random.noncentral_chisquare(df=1, nonc=0.00001, size=self.nb_particles)
        self.velocities = np.zeros((self.nb_particles, 4), dtype=np.float32)
        self.positions = [(0.0, 900.0, 0.0, sample_chisquared[i]) for i in range(self.nb_particles)]
        self.positions = np.asarray(self.positions, dtype=np.float32)

        
        R = 40.0

        for i in range(self.nb_particles):
            phi = uniform(-pi/12.0, pi/4.0)
            theta = uniform(pi/4.0, pi)

            speed_slope_x = R * sin(phi) * cos(theta) * uniform(0.2, 6.0)
            speed_slope_y = R * cos(phi) * uniform(1.0, 5.0)
            speed_slope_z = R * sin(phi) * sin(theta) * uniform(0.2, 6.0)
            self.velocities[i] = (speed_slope_x, speed_slope_y, speed_slope_z, 0.0) # zero padding for the ssbo

        self.init_pos = self.positions.copy()
        self.init_vel = self.velocities.copy()


        # init buffers & shader program
        self.shader = Shader(vertex_source="world/particles/smoke/smoke.vert", geom_source="world/particles/smoke/smoke.geom", fragment_source="world/particles/smoke/smoke.frag")
        self.cs = Shader(compute_source="world/particles/smoke/update.comp.glsl")

        # binding the ssbos to the compute shader program && generating buffers
        self.init_ssbos(shader_pgrm=self.cs.glid, attributes=dict(pos=self.positions, vel=self.velocities, init_pos=self.init_pos, init_vel=self.init_vel))

        # binding the ssbo containing the positions to the vertex shader
        ssbo_loc = GL.glGetProgramResourceIndex(self.shader.glid, GL.GL_SHADER_STORAGE_BLOCK, "pos")
        GL.glShaderStorageBlockBinding(self.shader.glid, ssbo_loc, 0)

        ssbo_loc = GL.glGetProgramResourceIndex(self.shader.glid, GL.GL_SHADER_STORAGE_BLOCK, "init_pos")
        GL.glShaderStorageBlockBinding(self.shader.glid, ssbo_loc, 2)

        self.sprites = Texture(path_img="textures/particles_atlas.png")

    def init_ssbos(self, shader_pgrm, attributes):
        self.buffers = {}  # we will store buffers in a named dict

        buffer_count = 0
        for name, data in attributes.items(): 

            #setting ssbo's binding point
            ssbo_loc = GL.glGetProgramResourceIndex(shader_pgrm, GL.GL_SHADER_STORAGE_BLOCK, name)
            GL.glShaderStorageBlockBinding(shader_pgrm, ssbo_loc, buffer_count)
            
            
            self.buffers[name] = GL.glGenBuffers(1)
            GL.glBindBuffer(GL.GL_SHADER_STORAGE_BUFFER, self.buffers[name])

            print(f"size bytes = {data.nbytes} && stride = {data.itemsize}")
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
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(self.sprites.type, self.sprites.glid)


        self.shader.bind()
        self.shader.set_int("sprites", 0)
        self.shader.set_uniforms(dict(view=camera.view, proj=camera.proj, up=camera.up, rgt=camera.rgt))

        # draw
        GL.glEnable(GL.GL_BLEND)
        self.execute()

