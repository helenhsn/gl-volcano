#!/usr/bin/env python3
"""
Python OpenGL practical application.
"""

import sys                          # for system arguments

# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import numpy as np                  # all matrix manipulations & OpenGL args
import glfw                         # lean window system wrapper for OpenGL
from core import Shader, Mesh, Viewer, Node, load

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

class Grid(Mesh):
    def __init__(self, shader, size): #size = grid's length & width = square grid
        self.size = size
        vertices = []
        uv = []
        normals = []

        # initializing mesh vertices, normals && uv coordinates for texturing
        for x in range(0, size):
            for y in range (0, size):
                x = float(x)
                y = float(y)
                vertices.append((x-size/2, 0.0, y-size/2))
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
    
    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        
        super().draw(primitives=primitives, size=self.size, **uniforms)
    



class Cylinder(Node):
    """ Very simple cylinder based on provided load function """
    def __init__(self, shader):
        super().__init__()
        self.add(*load('cylinder.obj', shader))  # just load cylinder from file

