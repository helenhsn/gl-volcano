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
    from utils.transform import quaternion, quaternion_from_axis_angle
    from utils.animation import KeyFrameControlNode

    """ Creates the bottom of the turbine with 3 sections """
    #initialisation of variables we will need
    sizes = [70, 60, 50, 30]
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
            transform = Node(transform=rotate((0, 0, 1), 90))
        transform.add(shape)
        
        if i != 0:
            transform.world_transform = list_shapes[i-1].world_transform @ transform.transform
        else:
            transform.world_transform = transform.transform
        
        list_shapes.append(transform)
    # we link the parts to the others
    list_shapes[0].add(list_shapes[1])
    list_shapes[1].add(list_shapes[2])

    # we need to calculate the vector for the blades rotation
    a = vec(0, sizes[3], 0, 0)
    b = vec(0, -sizes[3], 0, 0)
    vect_ab = b - a

    # matrix_ab = np.zeros((4,4), 'f')
    # matrix_ab[:3,0] = b-a
    # matrix_animation = list_shapes[3].world_transform @ matrix_ab
    blades(radiuses[3], list_shapes[3], sizes[0], shader, cos, sin)
    
    # animated part of the turbine
    translate_keys = {0: vec(0, 0, 0)}
    rotate_keys = { 0: quaternion_from_axis_angle(vect_ab @ list_shapes[3].world_transform, 90),
                    6: quaternion_from_axis_angle(vect_ab @ list_shapes[3].world_transform, 180),
                    12: quaternion_from_axis_angle(vect_ab @ list_shapes[3].world_transform, 270),
                    }
    scale_keys = {0: 1}
    keynode = KeyFrameControlNode(translate_keys, rotate_keys, scale_keys, modulo=12)
    keynode.add(list_shapes[3])

   
    new_node = Node(transform=translate(sizes[i], 2*sizes[i-1], 0))
    new_node.add(keynode)
    list_shapes[3] = new_node
    list_shapes[2].add(new_node)


    return list_shapes[0]

def blades(radius, adding_support, size, shader, cos, sin):
    from core import Node
    """ Creates the blades of the turbine"""
    cylinder = Cylinder(shader, 10, 2, 1/7, 1, cos, sin)
    radius_x = size/20
    radius_z = size/5
    angles = [0, 120, -120]
    vector = (0, 1, 0)
    for i in range(len(angles)):
        # first we scale the cylinder then we put it at the point (0, 0, 0)
        # next is moving the blade a little in order to make it more real and put it away from the center of the adding support
        # and we can move on to the rotations in order to get the angle of the blade and put it perpendicular to the adding support
        blade_part = Node(transform=rotate(vector, 90) @ rotate(vector, angles[i]) @ rotate((1, 0, 1), 90)@ translate(0, 8/10*radius, 0) @ translate(0, size, 0) @ scale(radius_x, size, radius_z))
        blade_part.add(cylinder)
        adding_support.add(blade_part)
            
    return adding_support
