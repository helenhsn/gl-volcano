#!/usr/bin/env python3
"""
Python OpenGL tree maker.
"""
# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import random as rd

from utils.transform import translate, rotate, scale, sincos, quaternion_from_axis_angle
from utils.primitives import Cylinder
from utils.shaders import Shader

SEUIL = 12
FACTOR = 0.9

def make_tree(cos, sin):
    from core import Node, vec
    from utils.animation import KeyFrameControlNode
    """ Creates the bottom of the tree with 3 sections """
    # definition of all the variables we will use
    sizes = [30, 22.5, 16.875]
    radiuses = [8, 6, 4.5]
    no_axis = (0, 0, 0)
    list_rotation_branch = [0, 45, 90, 135]
    # for branches :
    size_branch = 30
    radius_branch = 3
    angle_branch = 70

    # initialization of the cylinder used for all the tree
    shader = Shader(vertex_source="world/tree/shaders/tree.vert", fragment_source="world/tree/shaders/tree.frag")
    cylinder = Cylinder(shader, 10, 2, 3/4, 1, cos, sin)

    basic_shapes = []
    rotated_shapes = []

    # animated part of the tree
    translate_keys = {0: vec(0, 0, 0)}
    rotate_keys = {0: quaternion_from_axis_angle((1, 0, -1), 0),
                   3: quaternion_from_axis_angle((1, 0, -1), 2),
                   6: quaternion_from_axis_angle((1, 0, -1), 0),
                   9: quaternion_from_axis_angle((1, 0, -1), 1),
                   12: quaternion_from_axis_angle((1, 0, -1), 0)
                   }
    scale_keys = {0: 1}

    for i in range(3):
        shape = Node(transform=translate(0, sizes[i], 0) @ scale(radiuses[i], sizes[i], radiuses[i]))
        shape.add(cylinder)
        if i == 0:
            rotate_shape = Node(transform=rotate(no_axis, 0))
        elif i == 1:
            rotate_shape = Node(transform=rotate(no_axis, 0) @ translate(0, 2*sizes[i-1], 0))
        else:
            rotate_shape = Node(transform=rotate(no_axis, 0) @ translate(0, 2*sizes[i-1], 0))
            # we rotate and add more branches
            for rotation in list_rotation_branch:
                branch_shape = Node(transform=rotate((0, 1, 0), rotation))
                branch_rec(1, cylinder, translate(0, 1/2*(sizes[0] + sizes[1] + sizes[2]), 0),
                        branch_shape, rotate(no_axis, 0), 0, size_branch, radius_branch, 0.8, angle_branch)
                rotate_shape.add(branch_shape)
        #we don't link everything yet in order to make all the links
        rotated_shapes.append(rotate_shape)
        basic_shapes.append(shape)

    # we link the parts and add the animations
    keynode2 = KeyFrameControlNode(translate_keys, rotate_keys, scale_keys, modulo=12)
    keynode3 = KeyFrameControlNode(translate_keys, rotate_keys, scale_keys, modulo=12)
    
    rotated_shapes[0].add(basic_shapes[0])
    keynode2.add(basic_shapes[1])
    keynode3.add(rotated_shapes[2])
    rotated_shapes[2].add(basic_shapes[2])

    rotated_shapes[0].add(basic_shapes[0], rotated_shapes[1])
    rotated_shapes[1].add(keynode2, keynode3)


    return rotated_shapes[0]


def branch_rec(occurence, shape, translation_parent, adding_support, rotation_parent, angle_parent, size, radius, factor, angle):
    from core import Node, vec
    from utils.animation import KeyFrameControlNode
    """ Creates the branches of the tree (2)"""
    if size * factor < SEUIL: # recursion stop
        return 0
    rotation_tab = [(1, 0, 0), (1, 0, 0), (0, 0, 1), (0, 0, 1)]
    signs_tab = [1, -1, -1, 1]

    # animation to add a little movement to the end branches
    translate_keys = {0: vec(0, 0, 0)}
    rotate_keys = {0: quaternion_from_axis_angle((1, 0, -1), 0),
                   3: quaternion_from_axis_angle((1, 0, -1), 20),
                   6: quaternion_from_axis_angle((1, 0, -1), 0),
                   9: quaternion_from_axis_angle((1, 0, -1), 10),
                   12: quaternion_from_axis_angle((1, 0, -1), 0)
                   }
    scale_keys = {0: 1}
    keynode = KeyFrameControlNode(translate_keys, rotate_keys, scale_keys, modulo=12)


    for i in range(4):
        # calculate the angle and size of the branch by adding a little of random in order to have a better tree
        angle_branch = angle * rd.uniform(0.7, 1.2)
        size_branch = size * rd.uniform(0.95, 1.05)
        # we scale and translate the branch to the origin and we add the shape
        base_branch = Node(transform=translate(0, size_branch, 0) @ scale(radius, size_branch, radius))
        base_branch.add(shape)
        # we rotate the branch with the parent rotation and its own rotation
        rotation_branch = Node(transform=rotate(rotation_tab[i], signs_tab[i]*angle_branch) @ rotation_parent)
        # finally we can translate it to the top of the parent
        translation_branch = Node(transform=translation_parent)
        if i == 0 or i == 1:
            # we add new branches
            translation_1 = translate(0, 2*size_branch*sincos(signs_tab[i]*angle_branch+angle_parent)[1], 2*size_branch*sincos(signs_tab[i]*angle_branch+angle_parent)[0])
            rotation_1 = rotate(rotation_tab[i], signs_tab[i] * angle_branch) @ rotation_parent
            res = branch_rec(occurence+1, shape, translation_1, translation_branch, rotation_1, signs_tab[i]*angle_branch+angle_parent, size_branch*factor, radius*factor, factor, angle_branch)
            if res == 0: # if we are at the end of the tree, we add animation and we link the different parts
                keynode.add(base_branch)
                rotation_branch.add(keynode)
            else:
                rotation_branch.add(base_branch)
        else:
            base_branch.add(shape)
            rotation_branch.add(base_branch)
        translation_branch.add(rotation_branch)

        adding_support.add(translation_branch)

        if occurence == 1 and i == 1: # we add 2 other branches to add volume
            break
    # we return the branch
    return adding_support


def move_tree(tree_list, coordinates_list):
    from core import Node
    liste = []
    for i in range(len(tree_list)):
        new_base = Node(transform=translate(coordinates_list[i]))
        new_base.add(tree_list[i])
        liste.append(new_base)
    return liste
