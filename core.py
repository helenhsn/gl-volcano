# Python built-in modules
import os                           # os function, i.e. checking file status
from itertools import cycle         # allows easy circular choice list
import atexit                       # launch a function at exit

# External, non built-in modules
import OpenGL.GL as GL              # standard Python OpenGL wrapper
import glfw                         # lean window system wrapper for OpenGL
import numpy as np                  # all matrix manipulations & OpenGL args
import assimpcy
from utils.primitives import Mesh, init_cos_sin
from utils.shaders import Shader # 3D resource loader
from random import randint


# our transform functions
from utils.transform import Trackball, identity, rotate, scale, vec, translate
from utils.camera import Camera
from world.block import Chunk
from world.skybox.skybox import Skybox
from world.tree.tree import make_tree, move_tree
from world.wind_turbine.wind_turbine import make_turbine
from utils.primitives import Cylinder

import os
import OpenGL.GL as GL

from world.particles.smoke.smoke_ps import SmokeParticleSystem
from world.particles.splashes.splash_ps import SplashParticleSystem

# ------------  Node is the core drawable for hierarchical scene graphs -------
class Node:
    """ Scene graph transform and parameter broadcast node """
    def __init__(self, children=(), transform=identity()):
        self.transform = transform
        self.world_transform = identity()
        self.children = list(iter(children))

    def add(self, *drawables):
        """ Add drawables to this node, simply updating children list """
        self.children.extend(drawables)

    def draw(self, model=identity(), **other_uniforms):
        """ Recursive draw, passing down updated model matrix. """
        self.world_transform = model @ self.transform
        for child in self.children:
            child.draw(model=self.world_transform, **other_uniforms)

    def key_handler(self, key):
        """ Dispatch keyboard events to children with key handler """
        for child in (c for c in self.children if hasattr(c, 'key_handler')):
            child.key_handler(key)

class Animal(Node):
    """ Animal based on provided load function """
    def __init__(self, shader, path_obj):
        super().__init__()
        self.add(*load(path_obj, shader))  # just load capy from file

class Fence(Node):
    """ Fence based on provided load function """
    def __init__(self, shader):
        super().__init__()
        self.add(*load('world/pen/13078_Wooden_Post_and_Rail_Fence_v1_l3.obj', shader))  # just load capy from file

class Pen(Node):
    def __init__(self):
        super().__init__()
        node = Node(transform=translate(-1500, 1500, 600) @ scale(300, 3000, 3000))
        node.add(Fence(shader=Shader(vertex_source="world/pen/shaders/pen.vert", fragment_source="world/pen/shaders/pen.frag")))
        self.add(node)


# -------------- 3D resource loader -------------------------------------------
MAX_BONES = 128
MAX_KOALA = 50

# optionally load texture module
try:
    from utils.texture import Texture, Textured
except ImportError:
    Texture, Textured = None, None

# optionally load animation module
try:
    from utils.animation import KeyFrameControlNode, Skinned
except ImportError:
    KeyFrameControlNode, Skinned = None, None


def load(file, shader, tex_file=None, **params):
    """ load resources from file using assimp, return node hierarchy """
    try:
        pp = assimpcy.aiPostProcessSteps
        flags = pp.aiProcess_JoinIdenticalVertices | pp.aiProcess_FlipUVs
        flags |= pp.aiProcess_OptimizeMeshes | pp.aiProcess_Triangulate
        flags |= pp.aiProcess_GenSmoothNormals
        flags |= pp.aiProcess_ImproveCacheLocality
        flags |= pp.aiProcess_RemoveRedundantMaterials
        scene = assimpcy.aiImportFile(file, flags)
    except assimpcy.all.AssimpError as exception:
        print('ERROR loading', file + ': ', exception.args[0].decode())
        return []

    # ----- Pre-load textures; embedded textures not supported at the moment
    path = os.path.dirname(file) if os.path.dirname(file) != '' else './'
    for mat in scene.mMaterials:
        if tex_file:
            tfile = tex_file
        elif 'TEXTURE_BASE' in mat.properties:  # texture token
            name = mat.properties['TEXTURE_BASE'].split('/')[-1].split('\\')[-1]
            # search texture in file's whole subdir since path often screwed up
            paths = os.walk(path, followlinks=True)
            tfile = next((os.path.join(d, f) for d, _, n in paths for f in n
                     if name.startswith(f) or f.startswith(name)), None)
            assert tfile, 'Cannot find texture %s in %s subtree' % (name, path)
        else:
            tfile = None
        if Texture is not None and tfile:
            mat.properties['diffuse_map'] = Texture(path_img=tfile)

    # ----- load animations
    def conv(assimp_keys, ticks_per_second):
        """ Conversion from assimp key struct to our dict representation """
        return {key.mTime / ticks_per_second: key.mValue for key in assimp_keys}

    # load first animation in scene file (could be a loop over all animations)
    transform_keyframes = {}
    if scene.HasAnimations:
        anim = scene.mAnimations[0]
        for channel in anim.mChannels:
            # for each animation bone, store TRS dict with {times: transforms}
            transform_keyframes[channel.mNodeName] = (
                conv(channel.mPositionKeys, anim.mTicksPerSecond),
                conv(channel.mRotationKeys, anim.mTicksPerSecond),
                conv(channel.mScalingKeys, anim.mTicksPerSecond)
            )

    # ---- prepare scene graph nodes
    nodes = {}                                       # nodes name -> node lookup
    nodes_per_mesh_id = [[] for _ in scene.mMeshes]  # nodes holding a mesh_id

    def make_nodes(assimp_node):
        """ Recursively builds nodes for our graph, matching assimp nodes """
        keyframes = transform_keyframes.get(assimp_node.mName, None)
        if keyframes and KeyFrameControlNode:
            node = KeyFrameControlNode(*keyframes, assimp_node.mTransformation)
        else:
            node = Node(transform=assimp_node.mTransformation)
        nodes[assimp_node.mName] = node
        for mesh_index in assimp_node.mMeshes:
            nodes_per_mesh_id[mesh_index] += [node]
        node.add(*(make_nodes(child) for child in assimp_node.mChildren))
        return node

    root_node = make_nodes(scene.mRootNode)

    # ---- create optionally decorated (Skinned, Textured) Mesh objects
    for mesh_id, mesh in enumerate(scene.mMeshes):
        # retrieve materials associated to this mesh
        mat = scene.mMaterials[mesh.mMaterialIndex].properties

        # initialize mesh with args from file, merge and override with params
        index = mesh.mFaces
        uniforms = dict(
            k_d=mat.get('COLOR_DIFFUSE', (1, 1, 1)),
            k_s=mat.get('COLOR_SPECULAR', (1, 1, 1)),
            k_a=mat.get('COLOR_AMBIENT', (0, 0, 0)),
            s=mat.get('SHININESS', 16.),
        )
        attributes = dict(
            position=mesh.mVertices,
            normal=mesh.mNormals,
        )

        # ---- optionally add texture coordinates attribute if present
        if mesh.HasTextureCoords[0]:
            attributes.update(tex_coord=mesh.mTextureCoords[0])

        # --- optionally add vertex colors as attributes if present
        if mesh.HasVertexColors[0]:
            attributes.update(color=mesh.mColors[0])

        # ---- compute and add optional skinning vertex attributes
        if mesh.HasBones:
            # skinned mesh: weights given per bone => convert per vertex for GPU
            # first, populate an array with MAX_BONES entries per vertex
            vbone = np.array([[(0, 0)] * MAX_BONES] * mesh.mNumVertices,
                             dtype=[('weight', 'f4'), ('id', 'u4')])
            for bone_id, bone in enumerate(mesh.mBones[:MAX_BONES]):
                for entry in bone.mWeights:  # need weight,id pairs for sorting
                    vbone[entry.mVertexId][bone_id] = (entry.mWeight, bone_id)

            vbone.sort(order='weight')   # sort rows, high weights last
            vbone = vbone[:, -4:]        # limit bone size, keep highest 4

            attributes.update(bone_ids=vbone['id'],
                              bone_weights=vbone['weight'])

        new_mesh = Mesh(shader, attributes, index, **{**uniforms, **params})

        if Textured is not None and 'diffuse_map' in mat:
            new_mesh = Textured(new_mesh, diffuse_map=mat['diffuse_map'])
        if Skinned and mesh.HasBones:
            # make bone lookup array & offset matrix, indexed by bone index (id)
            bone_nodes = [nodes[bone.mName] for bone in mesh.mBones]
            bone_offsets = [bone.mOffsetMatrix for bone in mesh.mBones]
            new_mesh = Skinned(new_mesh, bone_nodes, bone_offsets)
        for node_to_populate in nodes_per_mesh_id[mesh_id]:
            node_to_populate.add(new_mesh)

    nb_triangles = sum((mesh.mNumFaces for mesh in scene.mMeshes))
    print('Loaded', file, '\t(%d meshes, %d faces, %d nodes, %d animations)' %
          (scene.mNumMeshes, nb_triangles, len(nodes), scene.mNumAnimations))
    return [root_node]


# ------------  Viewer class & window management ------------------------------
class Viewer(Node):
    """ GLFW viewer window, with classic initialization & graphics loop """

    def __init__(self, width=1500, height=1000, size=128):
        from utils.shaders import Shader
        from utils.transform import translate, rotate, scale
        super().__init__()

        # initialize and automatically terminate glfw on exit
        glfw.init()
        atexit.register(glfw.terminate)

        # camera related attributes
        self.previous_mouse_pos = vec(0.0, 0.0)
        self.first_mouse_move = True

        # version hints: create GL window with >= OpenGL 3.3 and core profile
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.RESIZABLE, True)
        self.win = glfw.create_window(width, height, 'Project', None, None)

        # make win's OpenGL context current; no OpenGL calls can happen before
        glfw.make_context_current(self.win)

        # initialize trackball
        self.camera = Camera()
        self.mouse = (0, 0)
        self.mouse_move = False

        self.delta_time = 0.0
        self.last_frame = 0.0

        # register event handlers
        glfw.set_key_callback(self.win, self.on_key)
        glfw.set_cursor_pos_callback(self.win, self.on_mouse_move)
        glfw.set_mouse_button_callback(self.win, self.on_mouse_click)
        glfw.set_window_size_callback(self.win, self.on_size)

        # useful message to check OpenGL renderer characteristics
        print('OpenGL', GL.glGetString(GL.GL_VERSION).decode() + ', GLSL',
              GL.glGetString(GL.GL_SHADING_LANGUAGE_VERSION).decode() +
              ', Renderer', GL.glGetString(GL.GL_RENDERER).decode())

        # initialize GL by setting viewport and default render characteristics
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_FRONT)
        GL.glEnable(GL.GL_DEPTH_TEST)  # depth test now enabled (TP2)

        # cyclic iterator to easily toggle polygon rendering modes
        self.fill_modes = cycle([GL.GL_LINE, GL.GL_POINT, GL.GL_FILL])

        # skybox init
        self.skybox = Skybox(50.0)

        # terrain/ocean mesh related attributes
        self.chunk_size = size
        self.chunk = Chunk(size, 4, N=4)

        # particle system init
        self.splash_ps = SplashParticleSystem()
        self.smoke_ps = SmokeParticleSystem()

        # tree init
        # initialise the angles we will use for the cylinders
        cosines, sines = init_cos_sin(10)
        self.tree = [make_tree(cosines, sines)]
        self.tree = move_tree(self.tree, [(1200.0, 300.0, 0.0)])[0]

        # wind turbine init
        turbine = make_turbine(cosines, sines)
        translations_wind_turbine = [(-1300, 300, 400), (-1000, 300, 300), (-1300, 300, 600), (-900, 300, 800), (-700, 300, 800)]
        self.turbine = []
        # we move manually each turbine in order to make the scene look good
        for translation in translations_wind_turbine:
            move_turbine = Node(transform=translate(translation) @ rotate((0, 1, 0), -220)) # they face the wind
            move_turbine.add(turbine)
            self.turbine.append(move_turbine)

        # initialize the koalas
        from utils.transform import quaternion_from_axis_angle
        
        # animate all koalas, they just do a yoyo effect
        translate_keys = {0: vec(0, 0, 0), 2: vec(0, 0, 0), 3: vec(0, 0, 0)}
        rotate_keys = {0: quaternion_from_axis_angle((1, 0, 1), 0),
                       2: quaternion_from_axis_angle((1, 0, 1), 15),
                       4: quaternion_from_axis_angle((1, 0, 1), 0),
                       6: quaternion_from_axis_angle((1, 0, 1), -15),
                       8: quaternion_from_axis_angle((1, 0, 1), 0)}
        scale_keys = {0: 1, 1: 0.95, 2: 1, 4: 1.05, 6: 1} # they also breathe a lot
        keynode = KeyFrameControlNode(translate_keys, rotate_keys, scale_keys, modulo=8)
        shader_for_animals = Shader(vertex_source="world/animals/shaders/texture.vert", fragment_source="world/animals/shaders/texture.frag")

        # we load a Koala and we save it when it is correctly turned
        koala = Animal(shader_for_animals, 'world/animals/koala.obj')
        keynode.add(koala)
        rotated_koala = Node(transform=rotate((0, 1, 0), 180) @ rotate((0, 1, 0), -90) @ rotate((1, 0, 0), -90))
        rotated_koala.add(keynode)
        self.koala = rotated_koala

        # we add each koala to the scene
        positions_koalas = [((-1200, 320, 500), 40),
                            ((-1100, 320, 500), 80),
                            ((-1000, 320, 400), 120),
                            ((-1100, 320, 700), 203),
                            ((-1200, 320, 720), 280),
                            ((-1050, 320, 500), 340)]
        for pos, angle in positions_koalas:
            node_koala = Node(transform=translate(pos) @ rotate((0, 1, 0), angle))
            node_koala.add(rotated_koala)
            self.add(node_koala)

        self.number_koala = 0
        self.pos_koala = {"x": [-700, 100], "y": [320], "z": [1100, 1200]}


        print("""\n\n\n############### UTILISATION DU CLAVIER ###############
    - Z : avancer dans la direction pointée par la caméra
    - S : reculer (idem)
    - Q : aller à gauche (sur le code on voit qu'il faut appuyer A mais le clavier par défaut est un clavier QWERTY)
    - D : aller à droite
    - Espace : monter
    - Backspace : descendre

    - Flèche du haut : tourne la caméra vers le haut (selon l'axe z)
    - Flèche du bas : tourne la caméra vers le bas (selon l'axe z)
    - Flèche de gauche : tourne la caméra vers la gauche (i.e. dans le sens antihoraire selon l'axe y)
    - Flèche de droite : tourne la caméra vers la droite (i.e.sens horaire) 

    - K : faire apparaître un koala
    - P : 
        - 1ère fois : affiche la scène uniquement avec des triangles, 
        - 2ème fois : affiche uniquement les sommets des objets de la scène, 
        - 3ème fois : retour à l'affichage classique
    - Echap : quitte la scène
######################################################""")


    def run(self):
        """ Main render loop for this OpenGL window """
        while not glfw.window_should_close(self.win):

            # update viewer's attributes
            win_size = glfw.get_window_size(self.win)

            current_frame = glfw.get_time()
            self.delta_time = current_frame - self.last_frame
            self.last_frame = current_frame
            self.chunk.update(current_frame)
            view_matrix = self.camera.view_matrix()
            projection_matrix = self.camera.projection_matrix(win_size)
            
            # opaque objects
            for turbine in self.turbine:
                turbine.draw(view=view_matrix,
                        projection=projection_matrix,
                        w_camera_position=self.camera.camera_pos)
            
            self.tree.draw(view=view_matrix,
                        projection=projection_matrix,
                        w_camera_position=self.camera.camera_pos)
            

            self.chunk.draw(view=view_matrix,
                        projection=projection_matrix,
                        w_camera_position=self.camera.camera_pos,
                        skybox=self.skybox.cubemap_text)

            # objects we loaded in our scene
            # animals and other objects have a different cull face than all the other objects 
            # so we change that parameter before changing it again after drawing all animals
            GL.glCullFace(GL.GL_BACK)
            self.draw(view=view_matrix,
                      projection=projection_matrix,
                      w_camera_position=self.camera.camera_pos)
            GL.glCullFace(GL.GL_FRONT)

            # skybox (optimization)
            # we want the skybox to be drawn behind every other object in the scene -> not in depth buffer
            GL.glDepthFunc(GL.GL_LEQUAL)
            GL.glDisable(GL.GL_CULL_FACE)
            self.skybox.draw(view=view_matrix, proj=projection_matrix)
            GL.glEnable(GL.GL_CULL_FACE)
            GL.glDepthFunc(GL.GL_LESS)

            # # transparent objects
            GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
            GL.glBlendEquation(GL.GL_FUNC_ADD)
            GL.glDepthMask(GL.GL_FALSE)
            self.smoke_ps.draw(dt=self.delta_time, camera=self.camera)    
            self.splash_ps.draw(dt=self.delta_time, camera=self.camera)
            GL.glDepthMask(GL.GL_TRUE)
            GL.glDisable(GL.GL_BLEND)

            # flush render commands, and swap draw buffers
            glfw.swap_buffers(self.win)

            # Poll for and process events
            glfw.poll_events()

            GL.glClearColor(0.3, 0.4, 0.6, 0.1)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)


    def on_key(self, _win, key, _scancode, action, _mods):
        """ 'Q' or 'Escape' quits """
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(self.win, True)

            if key == glfw.KEY_P: #wireframe mode
                GL.glPolygonMode(GL.GL_FRONT_AND_BACK, next(self.fill_modes))
            
            if key == glfw.KEY_K:  # a koala appears randomly by pressing a button
                if self.number_koala < MAX_KOALA:
                    # random position
                    x = randint(self.pos_koala["x"][0], self.pos_koala["x"][1])
                    y = self.pos_koala["y"][0]
                    z = randint(self.pos_koala["z"][0], self.pos_koala["z"][1])
                    # random rotation 
                    transform_koala = Node(transform=translate(x, y, z) @ rotate((0, 1, 0), randint(0, 360)))
                    transform_koala.add(self.koala)
                    self.add(transform_koala)
                    self.number_koala += 1
                else: 
                    print("Please, don't let koalas destroy humanity...")

            self.camera.handle_keys(key, action, self.delta_time)

            # call Node.key_handler which calls key_handlers for all drawables
            self.key_handler(key)

            
    def add(self, *drawables):
        """ Add drawables to this node, simply updating children list """
        self.children.extend(drawables)



    def on_mouse_move(self, win, xpos, ypos):
        if self.mouse_move:
            self.mouse = (xpos,  ypos)
            if self.first_mouse_move:
                self.previous_mouse_pos = self.mouse
                self.first_mouse_move = False
            else:
                offset_x = self.mouse[0] - self.previous_mouse_pos[0]
                offset_y = self.mouse[1] - self.previous_mouse_pos[1]
                self.camera.handle_mouse_movement(offset_x, offset_y)
                self.previous_mouse_pos = self.mouse

    def on_mouse_click(self, win, button, action, mods):
        if action == glfw.PRESS and button == glfw.MOUSE_BUTTON_LEFT:
            self.mouse_move = not self.mouse_move
            self.first_mouse_move = True

    def on_size(self, _win, _width, _height):
        """ window size update => update viewport to new framebuffer size """
        GL.glViewport(0, 0, *glfw.get_framebuffer_size(self.win))
