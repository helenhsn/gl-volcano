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
            index_buffer = np.array(index, np.int32, copy=False)  # good format
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.buffers['index'])
            GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, index_buffer, usage)
            self.draw_command = GL.glDrawElements
            self.arguments = (index_buffer.size, GL.GL_UNSIGNED_INT, None)

    def execute(self, primitive, attributes=None):
        """ draw a vertex array, either as direct array or indexed array """
        # optionally update the data attribute VBOs, useful for e.g. particles
        attributes = attributes or {}
        for name, data in attributes.items():
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.buffers[name])
            GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, data)

        GL.glBindVertexArray(self.glid)
        self.draw_command(primitive, *self.arguments)

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

    def draw(self, primitives=GL.GL_TRIANGLES, attributes=None, **uniforms):
        GL.glUseProgram(self.shader.glid)
        self.shader.set_uniforms({**self.uniforms, **uniforms})
        self.vertex_array.execute(primitives, attributes)


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
    def __init__(self, shader, number_facets):
        self.shader = shader
        #angles
        theta_init = 0.0
        theta_max = 2*np.pi
        theta_incr = theta_max/number_facets
        #hauteurs
        h_base1 = -1
        h_base2 = 1
        position = []
        normal = []
        index = []
        counter = 0

        #création de l'enveloppe du cylindre
        theta = theta_init
        while(theta < theta_max):
            #on découpe le cylindre en rectangles qu'on découpe eux-mêmes en triangles
            #on fait 4 points
            A = (np.cos(theta), h_base1, np.sin(theta))
            C = (np.cos(theta), h_base2, np.sin(theta))
            B = (np.cos(theta + theta_incr), h_base1, np.sin(theta + theta_incr))
            D = (np.cos(theta + theta_incr), h_base2, np.sin(theta + theta_incr))
            #on ajoute les 3 points chaque triangle pour dessiner nos rectanlges
            position.append(A)
            normal.append((np.cos(theta), 0, np.sin(theta)))
            position.append(B)
            normal.append((np.cos(theta + theta_incr), 0, np.sin(theta + theta_incr)))
            position.append(C)
            normal.append((np.cos(theta), 0, np.sin(theta)))
            position.append(C)
            normal.append((np.cos(theta), 0, np.sin(theta)))
            position.append(B)
            normal.append((np.cos(theta + theta_incr), 0, np.sin(theta + theta_incr)))
            position.append(D)
            normal.append((np.cos(theta + theta_incr), 0, np.sin(theta + theta_incr)))

            
            #on incrémente à chaque itération theta
            theta = theta + theta_incr

            #on a ajouté 6 points donc on doit ajouter les index correspondants
            for _ in range(0, 6):
                index.append(counter)
                counter += 1
            
        #création des deux faces du cylindre, une pour chaque hauteur
        for hauteur in (h_base1, h_base2):
            theta = theta_init
            A = (0, hauteur, 0) #le point au centre du cercle - ça sera toujours le même donc on peut le créer dans le for directement

            while(theta < theta_max):
                #on découpe en triangles le cercle
                B = (np.cos(theta), hauteur, np.sin(theta))
                C = (np.cos(theta+theta_incr), hauteur, np.sin(theta+theta_incr))

                position.append(A)
                position.append(B)
                position.append(C)

                theta = theta + theta_incr
                #on a ajouté 6 points donc on doit ajouter les index correspondants
                for _ in range(0,3):
                    index.append(counter)
                    counter += 1
                    if(hauteur == h_base1):
                        normal.append((0, -1, 0))
                    else:
                        normal.append((0, 1, 0))

        self.position = np.array((position), 'f')
        self.normal = np.array(normal, 'f')
        self.color = self.normal


        self.index = np.array(index, np.uint32)

        attributes = dict(position=position, color=self.normal)
        super().__init__(shader, attributes=attributes, index=self.index)



    def draw(self, primitives=GL.GL_TRIANGLES, attributes=None, **uniforms):
        """
            Dessine la forme
        """
        #On peut refaire un dictionnaire pour modifier la couleur (on peut écraser que
        # l'un des deux attribut car les buffers sont différents !)
        attributes = dict(color=self.color) #on a besoin que de color qu'on envoie dans draw
        super().draw(primitives=primitives, attributes=attributes, **uniforms)



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
                vertices.append((x*4, 0.0, y*4))
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
        