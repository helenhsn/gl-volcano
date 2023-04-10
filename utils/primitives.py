#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""

import sys                          # for system arguments

# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import numpy as np                  # all matrix manipulations & OpenGL args
import glfw
import ctypes

# function that caculates all sines and cosines of the unit circle depending on a number of slices required
def init_cos_sin(slices):
    theta_incr = 2*np.pi/slices
    cosines = []
    sines = []
    for i in range(slices):
        theta = i*theta_incr
        cosines.append(np.cos(theta))
        sines.append(np.sin(theta))
    return cosines, sines



class VertexArray:
    """ helper class to create and self destroy OpenGL vertex array objects."""
    def __init__(self, shader, attributes, index=None, usage=GL.GL_STATIC_DRAW):
        """ Vertex array from attributes and optional index array. Vertex
            Attributes should be list of arrays with one row per vertex. """

        self.shader = shader
        # create vertex array object, bind it
        self.glid = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.glid)
        self.buffers = {}  # we will store buffers in a named dict
        nb_primitives, size = 0, 0

        # load buffer per vertex attribute (in list with index = shader layout)
        for name, data in attributes.items():
            loc = GL.glGetAttribLocation(shader.glid, name)
            if loc >= 0:
                # bind a new vbo, upload its data to GPU, declare size and type
                self.buffers[name] = GL.glGenBuffers(1)
                data = np.array(data, np.float32, copy=False)  # ensure format
                try:
                    nb_primitives, size = (data.shape[0], data.shape[1])
                except IndexError:
                    nb_primitives=data.shape[0]
                    size = 1 
                GL.glEnableVertexAttribArray(loc)
                GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffers[name])
                GL.glBufferData(GL.GL_ARRAY_BUFFER, data, usage)
                GL.glVertexAttribPointer(loc, size, GL.GL_FLOAT, False, 0, None)

        # optionally create and upload an index buffer for this object
        self.draw_command = GL.glDrawArrays
        self.arguments = (0, nb_primitives)
        if index is not None:
            self.buffers['index'] = GL.glGenBuffers(1)
            self.index_buffer = np.array(index, np.int32, copy=False)  # good format
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.buffers['index'])
            GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.index_buffer, usage)
            self.draw_command = GL.glDrawElements
            self.arguments = (self.index_buffer.size, GL.GL_UNSIGNED_INT, None)

    def execute(self, primitive, attributes=None, draw_command=None):
        """ draw a vertex array, either as direct array or indexed array """
        # optionally update the data attribute VBOs, useful for e.g. particles
        attributes = attributes or {}
        for name, data in attributes.items():
            if name in self.buffers:
                GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffers[name])
                GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, data)

        GL.glBindVertexArray(self.glid)

        if not draw_command:
            self.draw_command(primitive, *self.arguments)
        else:
            draw_command(primitive, *self.arguments)

    def __del__(self):  # object dies => kill GL array and buffers from GPU
        GL.glDeleteVertexArrays(1, [self.glid])
        GL.glDeleteBuffers(len(self.buffers), list(self.buffers.values()))


# ------------  Mesh is the core drawable -------------------------------------
class Mesh:
    """ Basic mesh class, attributes and uniforms passed as arguments """
    def __init__(self, shader, attributes, index=None,
                 usage=GL.GL_STATIC_DRAW, **uniforms):
        self.shader = shader
        self.uniforms = uniforms
        self.vertex_array = VertexArray(shader, attributes, index, usage)

    def draw(self, primitives=GL.GL_TRIANGLES, attributes=None, draw_command=None, **uniforms):
        GL.glUseProgram(self.shader.glid)
        self.shader.set_uniforms({**self.uniforms, **uniforms})
        self.vertex_array.execute(primitives, attributes, draw_command=draw_command)


class Axis(Mesh):
    """ Axis object useful for debugging coordinate frames """
    def __init__(self, shader):
        pos = ((0, 0, 0), (1, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 0), (0, 0, 1))
        col = ((1, 0, 0), (1, 0, 0), (0, 1, 0), (0, 1, 0), (0, 0, 1), (0, 0, 1))
        super().__init__(shader, attributes=dict(position=pos, color=col))

    def draw(self, primitives=GL.GL_LINES, **uniforms):
        super().draw(primitives=primitives, **uniforms)


class Triangle(Mesh):
    """Hello triangle object"""
    def __init__(self, shader):
        position = np.array(((0, .5, 0), (-.5, -.5, 0), (.5, -.5, 0)), 'f')
        color = np.array(((1, 0, 0), (0, 1, 0), (0, 0, 1)), 'f')
        self.color = (1, 1, 0)
        attributes = dict(position=position, color=color)
        super().__init__(shader, attributes=attributes)

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        super().draw(primitives=primitives, global_color=self.color, **uniforms)

    def key_handler(self, key):
        if key == glfw.KEY_C:
            self.color = (0, 0, 0)


class Cylinder(Mesh):
    """ Class for drawing a cylinder object """
    def __init__(self, shader, slices, height, radius_facet_up, radius_facet_down, cosines, sines):
        self.shader = shader
        radiuses = [radius_facet_up, radius_facet_down]

        position = []
        normal = []
        index = []
        
        #lateral faces 
        for i in range(slices):
            counter = 2*i
            index.append(((counter+2)%(2*slices), counter, counter+1))
            index.append(((counter+3)%(2*slices), (counter+2)%(2*slices), counter+1))

            for j in range(2):
                h = height/2 - height * j
                position.append((cosines[i] * radiuses[j], h, sines[i] * radiuses[j]))
                normal.append((cosines[i], 0, sines[i]))
        
        #add again all points
        for i in range(slices):
            counter = 2*i
            for j in range(2):
                h = height/2 - height * j
                position.append((cosines[i] * radiuses[j], h, sines[i] * radiuses[j]))
        
        for i in range(slices-1):
            counter = 2*i
            for j in range(2):
                h = height/2 - height * j
                a = 1/2
                position.append((cosines[i] * radiuses[j], h, sines[i] * radiuses[j]))
            index.append(((counter+2+2*slices)%(4*slices), 4*slices, counter+2*slices))
            index.append(((counter+3+2*slices)%(4*slices), counter+1+2*slices, 4*slices+1))
            normal.append((0, 1/2, 0))
            normal.append((0, -1/2, 0))
        # we add the last two vertices manually
        index.append(((2*slices), 4*slices, 4*slices-2))
        index.append(((2*slices+1), 4*slices-1, 4*slices+1))
        normal.append((0, 1/2, 0))
        normal.append((0, -1/2, 0))
        position.append((cosines[slices-1] * radiuses[0], height/2, sines[slices-1] * radiuses[0]))
        position.append((cosines[slices-1] * radiuses[1], -height/2, sines[slices-1] * radiuses[1]))

        #add bottom and top points
        for j in range(2):
            h = height/2 - height * j
            a = 1/2 - 1*j
            position.append((0, h+h/3, 0))

            normal.append((0, a, 0))

        self.position = np.array((position), 'f')
        self.normal = np.array(normal, 'f')
        self.color = self.position

        self.index = np.array(index, np.uint32)

        attributes = dict(position=position, normal=self.normal)
        super().__init__(shader, attributes=attributes, index=self.index)


    def draw(self, primitives=GL.GL_TRIANGLES, attributes=None, **uniforms):
        """
            Draw the cylinder
        """
        super().draw(primitives=primitives, **uniforms)

class Cube(Mesh):
    def __init__(self, shader, r):
         # front face regarding the camera but back face regarding world
        positions = [
            (-r, r, -r), 
            (-r, -r, -r),
            (r, -r, -r),
            (r, r, -r),
            (-r, r, r),
            (-r, -r, r),
            (r, -r, r),
            (r, r, r)
        ]
        indices=[0, 1, 2, 0, 2, 3, 4, 6, 5, 4, 7, 6, 7, 2, 6, 7, 3, 2, 0, 5, 1, 0, 4, 5, 4, 0, 3, 4, 3, 7, 5, 2, 1, 5, 6, 2]

        super().__init__(shader, attributes=dict(position=positions), index=indices)
    
    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms): 
        super().draw(primitives=primitives, **uniforms)



class Grid(Mesh):
    def __init__(self, shader, size, size_factor): #size = grid's length & width = square grid
        self.size = size
        vertices = []
        uv = []
        normals = []

        # initializing mesh vertices, normals && uv coordinates for texturing
        for x in range(0, size):
            for y in range (0, size):
                x = float(x)
                y = float(y)
                vertices.append((x*size_factor, 0.0, y*size_factor)) # stretching the mesh -> less computation for the same surface's size
                normals.append((0.0, 1.0, 0.0))
                uv.append((x/(size-1), y/(size-1)))


        # initializing mesh indices for EBO 
        indices = []

        for x in range(0, size-1):
            for y in range (0,size-1): # for each unit square in the mesh grid
                
                # first triangle : bottom left -> bottom right -> top left (counterclockwise)
                indices.append(x * size + y)
                indices.append((x+1)*size + y)
                indices.append(x*size + y + 1)

                # second triangle : top left -> bottom right -> top right (counterclockwise)
                indices.append(x * size + y + 1)
                indices.append((x+1)*size + y)
                indices.append((x+1)*size + y + 1)
        super().__init__(shader, attributes=dict(position=vertices, uv=uv, normal=normals), index=indices)
    
    def draw(self, primitives=GL.GL_TRIANGLES, draw_command=None, **uniforms):
        
        super().draw(primitives=primitives, size=self.size, draw_command=draw_command, **uniforms)

