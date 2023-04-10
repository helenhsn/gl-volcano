#!/usr/bin/env python3
"""
Python OpenGL tree maker.
"""

import sys                          # for system arguments

# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import numpy as np                  # all matrix manipulations & OpenGL args
import random as rd
import glfw                         # lean window system wrapper for OpenGL

from utils.transform import translate, rotate, scale, sincos
from utils.primitives import Cylinder
from utils.shaders import Shader


SEUIL = 10
FACTOR = 0.9


def make_turbine(cos, sin):
    from core import Node, vec
    from utils.transform import quaternion, quaternion_from_euler
    from utils.animation import KeyFrameControlNode

    """ Creates the bottom of the turbine with 3 sections """
    #initialisation of variables we will need
    sizes = [50, 40, 30, 15]
    radiuses = [18, 12, 8, 8]
    no_axis = (0, 0, 0)
    
    # initialize the cylinder used
    shader = Shader(vertex_source="world/wind_turbine/shaders/wind_turbine.vert", fragment_source="world/wind_turbine/shaders/wind_turbine.frag")
    cylinder = Cylinder(shader, 10, 2, 2/3, 1, cos, sin)

    #creation of the three parts
    list_shapes = []
    for i in range(len(sizes)):
        shape = Node(transform=translate(0, sizes[i], 0) @ scale(radiuses[i], sizes[i], radiuses[i]) @ rotate(no_axis, 0))
        shape.add(cylinder)
        if i == 0:
            transform = Node(transform=rotate(no_axis, 0))
        elif i == 1:
            transform = Node(transform=rotate(no_axis, 0) @ translate(0, 2 * sizes[i-1], 0))
        elif i == 2:
            transform = Node(transform=rotate(no_axis, 0) @ translate(0, 2*sizes[i-1], 0))
        else:
            transform = Node(transform=translate(sizes[i], 2*sizes[i-1], 0) @ rotate((0, 0, 1), 90))
        transform.add(shape)
        list_shapes.append(transform)
    # we link the parts to the others
    list_shapes[0].add(list_shapes[1])
    list_shapes[1].add(list_shapes[2])

    # animated part of the turbin
    translate_keys = {0: vec(0, 0, 0), 2: vec(0, 0, 0), 4: vec(0, 0, 0)}
    rotate_keys = { 3: quaternion(), 4: quaternion() }
    scale_keys = {0: 1, 2: 1, 4: 1}
    keynode = KeyFrameControlNode(translate_keys, rotate_keys, scale_keys, modulo=4 )
    keynode.add(list_shapes[3])

    list_shapes[2].add(keynode)

    blades(radiuses[3], list_shapes[3], sizes[0], shader, cos, sin)

    return list_shapes[0]

def blades(radius, adding_support, size, shader, cos, sin):
    from core import Node
    """ Creates the blades of the turbine"""
    cylinder = Cylinder(shader, 10, 2, 1/7, 1, cos, sin)
    radius_x = size/20
    radius_y = size/5
    angles = [0, 120, -120]
    vectors = [(1, 0, 1), (0, 1, 0), (0, 1, 0)]

    for i in range(len(angles)):
        blade_part = Node(transform=rotate(vectors[1], 90) @ rotate(vectors[i], angles[i]) @ rotate((1, 0, 1), 90) @ translate(9/10*radius*np.sin(angles[i]), 9/10*radius*np.cos(angles[i]), 0) @ translate(0, size, 0) @ scale(radius_x, size, radius_y))
        blade_part.add(cylinder)
        adding_support.add(blade_part)
            
    return adding_support
