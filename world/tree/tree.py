#!/usr/bin/env python3
"""
Python OpenGL practical application.
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

SEUIL = 0.5
FACTOR = 0.9


def make_tree():
    from core import Node

    """ Creates the bottom of the tree with 3 sections """
    facteur = 2
    d = 0.30 *facteur
    epaisseur = 0.6
    a = 0.40*d*epaisseur*facteur
    b = 1*d*facteur
    c = 0.25*d*epaisseur*facteur
    e = 0.40*d*epaisseur*facteur

    angle = 70
    size = 0.7*facteur
    largeur_branche = 0.05*facteur
    no_axis = (0, 0, 0)
    no_angle = 0
    
    shader = Shader(vertex_source="world/tree/shaders/tree.vert", fragment_source="world/tree/shaders/tree.frag")
    cylinder = Cylinder(shader, 10, 1, 0.5)

    #on crée 3 cylindres pour la base de l'arbre et on les met tous sur l'axe 0:
    base_shape = Node(transform=translate(0, b, 0) @ scale(a, b, a) @ rotate(no_axis, no_angle))
    middle_shape = Node(transform=translate(0, 1.5*b, 0) @ scale(e, 1.5*b, e))
    upper_shape = Node(transform=translate(0, 2*b, 0) @ scale(c, 2*b, c))

    upper_shape.add(cylinder)
    middle_shape.add(cylinder)
    base_shape.add(cylinder)

    base_transform = Node(transform=rotate(no_axis, no_angle))
    middle_transform = Node(transform=rotate(no_axis, no_angle) @ translate(0, 1*b, 0))
    upper_transform = Node(transform=rotate(no_axis, no_angle) @ translate(0, b, 0))

    upper_transform.add(upper_shape)
    middle_transform.add(middle_shape, upper_transform)
    base_transform.add(base_shape, middle_transform)

    #on fait les rotations :
    # rotation_base = Node(transform=rotate(no_axis, no_angle))
    # rotation_middle = Node(transform=rotate(no_axis, no_angle))
    # rotation_upper = Node(transform=rotate(no_axis, no_angle))

    # rotation_base.add(base_shape)
    # rotation_middle.add(middle_shape)
    # rotation_upper.add(upper_shape)

    # #on fait les translations nécessaires :
    # translation_base = Node()
    # translation_middle = Node(transform=translate(0, b, 0)) #on met le cylindre du milieu au milieu du cylindre d'en bas
    # translation_upper = Node(transform=translate(0, 1*b, 0)) #on met le cylindre d'en haut au milieu du cylindre du milieu


    # translation_base.add(rotation_base, translation_middle)
    # translation_middle.add(rotation_middle, translation_upper)
    # translation_upper.add(rotation_upper)

    #on crée les branches :
    # tree_rec2(1, cylinder, translate(0, 4*b, 0), translation_upper, rotate(no_axis, no_angle), no_angle, size, 0.05*epaisseur, 0.8, angle)
    # second_tree = Node(transform=rotate((0, 1, 0), 90))
    # third_tree = Node(transform=rotate((0, 1, 0), 45))
    # fourth_tree = Node(transform=rotate((0, 1, 0), 135))
    # fifth_tree = Node(transform=rotate((0, 1, 0), 25))
    # sixth_tree = Node(transform=rotate((0, 1, 0), 75))
    # seventh_tree = Node(transform=rotate((0, 1, 0), 115))
    # eigth_tree = Node(transform=rotate((0, 1, 0), 155))

    # translation_upper.add(second_tree, third_tree, fourth_tree, fifth_tree, sixth_tree, seventh_tree, eigth_tree)
    # tree_rec2(1, cylinder, translate(0, 4*b, 0), second_tree, rotate(no_axis, no_angle), 0, size, largeur_branche*epaisseur, 0.8, angle)
    # tree_rec2(1, cylinder, translate(0, 4*b, 0), third_tree, rotate(no_axis, no_angle), 0, size, largeur_branche*epaisseur, 0.8, angle)
    # tree_rec2(1, cylinder, translate(0, 4*b, 0), fourth_tree, rotate(no_axis, no_angle), 0, size, largeur_branche*epaisseur, 0.8, angle)
    # tree_rec2(1, cylinder, translate(0, 4*b, 0), fifth_tree, rotate(no_axis, no_angle), 0, size, largeur_branche*epaisseur, 0.8, angle)
    # tree_rec2(1, cylinder, translate(0, 4*b, 0), sixth_tree, rotate(no_axis, no_angle), 0, size, largeur_branche*epaisseur, 0.8, angle)
    # tree_rec2(1, cylinder, translate(0, 4*b, 0), seventh_tree, rotate(no_axis, no_angle), 0, size, largeur_branche*epaisseur, 0.8, angle)
    # tree_rec2(1, cylinder, translate(0, 4*b, 0), eigth_tree, rotate(no_axis, no_angle), 0, size, largeur_branche*epaisseur, 0.8, angle)
    
    
    return base_transform

def tree_rec2(occurence, shape, translation_parent, adding_support, rotation_parent, angle_parent, size, radius, factor, angle):
    from core import Node

    """ Creates the branches of the tree (2)"""
    if size * factor < SEUIL:
        return 0
    
    size1 = size * rd.uniform(0.98, 1.0)
    size2 = size * rd.uniform(0.98, 1.0)
    size3 = size * rd.uniform(1.0, 1.02)
    size4 = size * rd.uniform(1.0, 1.02)
    size5 = size * rd.uniform(1.0, 1.02)
    size6 = size * rd.uniform(1.0, 1.02)
    size7 = size * rd.uniform(1.0, 1.02)
    size8 = size * rd.uniform(1.0, 1.02)

    angle1 = angle * rd.uniform(0.7, 1.0)
    angle2 = angle * rd.uniform(0.7, 1.0)
    angle3 = angle * rd.uniform(0.7, 1.0)
    angle4 = angle * rd.uniform(0.7, 1.0)
    angle5 = angle * rd.uniform(0.7, 1.0)
    angle6 = angle * rd.uniform(0.7, 1.0)
    angle7 = angle * rd.uniform(0.7, 1.0)
    angle8 = angle * rd.uniform(0.7, 1.0)

    #on met les nouvelles formes au niveau du 0
    branche_base_1 = Node(transform=translate(0, size1, 0) @ scale(radius, size1, radius))
    branche_base_2 = Node(transform=translate(0, size2, 0) @ scale(radius, size2, radius))
    branche_base_3 = Node(transform=translate(0, size3, 0) @ scale(radius, size3, radius))
    branche_base_4 = Node(transform=translate(0, size4, 0) @ scale(radius, size4, radius))
    branche_base_5 = Node(transform=translate(0, size5, 0) @ scale(radius, size5, radius))
    branche_base_6 = Node(transform=translate(0, size6, 0) @ scale(radius, size6, radius))
    branche_base_7 = Node(transform=translate(0, size7, 0) @ scale(radius, size7, radius))
    branche_base_8 = Node(transform=translate(0, size8, 0) @ scale(radius, size8, radius))
    
    #on ajoute les cylindres à nos formes
    branche_base_1.add(shape)
    branche_base_2.add(shape)
    branche_base_3.add(shape)
    branche_base_4.add(shape)
    branche_base_5.add(shape)
    branche_base_6.add(shape)
    branche_base_7.add(shape)
    branche_base_8.add(shape)


    if occurence == 1:
        fact = 1
    else:
        fact = 2
    #on effectue les rotations voulues auxquelles on doit y ajouter celle du parent
    rotation_branche_1 = Node(transform=rotate((1, 0, 0), angle1) @ rotation_parent)
    rotation_branche_2 = Node(transform=rotate((1, 0, 0), -angle2) @ rotation_parent)
    rotation_branche_3 = Node(transform=rotate((0, 0, 1), -fact*angle3) @ rotation_parent)
    rotation_branche_4 = Node(transform=rotate((0, 0, 1), fact*angle4) @ rotation_parent)
    rotation_branche_5 = Node(transform=rotate((1, 0, -1), fact*angle5) @ rotation_parent)
    rotation_branche_6 = Node(transform=rotate((-1, 0, 1), fact*angle6) @ rotation_parent)
    rotation_branche_7 = Node(transform=rotate((1, 0, 1), fact*angle7) @ rotation_parent)
    rotation_branche_8 = Node(transform=rotate((-1, 0, -1), fact*angle8) @ rotation_parent)
    
    #on ajoute la forme précédente
    rotation_branche_1.add(branche_base_1)
    rotation_branche_2.add(branche_base_2)
    rotation_branche_3.add(branche_base_3)
    rotation_branche_4.add(branche_base_4)
    rotation_branche_5.add(branche_base_5)
    rotation_branche_6.add(branche_base_6)
    rotation_branche_7.add(branche_base_7)
    rotation_branche_8.add(branche_base_8)

    #on translate au bon endroit nos branches en prenant en compte celle du parent
    translation_branche_1 = Node(transform=translation_parent)
    translation_branche_2 = Node(transform=translation_parent)
    translation_branche_3 = Node(transform=translation_parent)
    translation_branche_4 = Node(transform=translation_parent)
    translation_branche_5 = Node(transform=translation_parent)
    translation_branche_6 = Node(transform=translation_parent)
    translation_branche_7 = Node(transform=translation_parent)
    translation_branche_8 = Node(transform=translation_parent)


    translation_branche_1.add(rotation_branche_1)
    translation_branche_2.add(rotation_branche_2)
    translation_branche_3.add(rotation_branche_3)
    translation_branche_4.add(rotation_branche_4)
    translation_branche_5.add(rotation_branche_5)
    translation_branche_6.add(rotation_branche_6)
    translation_branche_7.add(rotation_branche_7)
    translation_branche_8.add(rotation_branche_8)

    adding_support.add(translation_branche_1, translation_branche_2, translation_branche_3, translation_branche_4, translation_branche_5, translation_branche_6, translation_branche_7, translation_branche_8)

    translation_1 = translate(0, 2*size1*sincos(angle1+angle_parent)[1], 2*size1*sincos(angle1+angle_parent)[0])
    rotation_1 = rotate((1, 0, 0), angle1) @ rotation_parent
    
    translation_2 = translate(0, 2*size2*sincos(-angle2+angle_parent)[1], 2*size2*sincos(-angle2+angle_parent)[0])
    rotation_2 = rotate((1, 0, 0), -angle2) @ rotation_parent
    
    tree_rec2(occurence+1, shape, translation_1, translation_branche_1, rotation_1, angle1+angle_parent, size1*factor, radius*factor, factor, angle1)
    tree_rec2(occurence+1, shape, translation_2, translation_branche_2, rotation_2, -angle2+angle_parent, size2*factor, radius*factor, factor, angle2)
    
    return adding_support

def move_tree(tree_list, coordinates_list):
    from core import Node
    liste = []
    for i in range(len(tree_list)):
        new_base = Node(transform=translate(coordinates_list[i]))
        new_base.add(tree_list[i])
        liste.append(new_base)
    return liste
