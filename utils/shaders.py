import os
import OpenGL.GL as GL

# ------------ low level OpenGL object wrappers ----------------------------
class Shader:
    """ Helper class to create and automatically destroy shader program """
    @staticmethod
    def _compile_shader(src, shader_type):
        src = open(src, 'r').read() if os.path.exists(src) else src
        src = src.decode('ascii') if isinstance(src, bytes) else src
        GL.glGetError()
        shader = GL.glCreateShader(shader_type)
        print(shader)
        err = GL.glGetError()
        if err != GL.GL_NO_ERROR:
            print("eeeeeeeee" ,err)
        GL.glShaderSource(shader, src)
        GL.glCompileShader(shader)
        status = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
        src = ('%3d: %s' % (i+1, l) for i, l in enumerate(src.splitlines()))
        if not status:
            log = GL.glGetShaderInfoLog(shader).decode('ascii')
            GL.glDeleteShader(shader)
            src = '\n'.join(src)
            print('Compile failed for %s\n%s\n%s' % (shader_type, log, src))
            os._exit(1)
        return shader

    def __init__(self, vertex_source=None, fragment_source=None, compute_source=None, debug=False):
        """ Shader can be initialized with raw strings or source file names """
        
        if (compute_source):
            comp = self._compile_shader(compute_source, GL.GL_COMPUTE_SHADER)
            if comp:
                self.glid = GL.glCreateProgram()  # pylint: disable=E1111
                GL.glAttachShader(self.glid, comp)
                GL.glLinkProgram(self.glid)
                GL.glDeleteShader(comp)
                status = GL.glGetProgramiv(self.glid, GL.GL_LINK_STATUS)
                if not status:
                    print(GL.glGetProgramInfoLog(self.glid).decode('ascii'))
                    os._exit(1)
        else:
            vert = self._compile_shader(vertex_source, GL.GL_VERTEX_SHADER)
            frag = self._compile_shader(fragment_source, GL.GL_FRAGMENT_SHADER)
            if vert and frag:
                self.glid = GL.glCreateProgram()  # pylint: disable=E1111
                GL.glAttachShader(self.glid, vert)
                GL.glAttachShader(self.glid, frag)
                GL.glLinkProgram(self.glid)
                GL.glDeleteShader(vert)
                GL.glDeleteShader(frag)
                status = GL.glGetProgramiv(self.glid, GL.GL_LINK_STATUS)
                if not status:
                    print(GL.glGetProgramInfoLog(self.glid).decode('ascii'))
                    os._exit(1)

        # get location, size & type for uniform variables using GL introspection
        self.uniforms = {}
        self.debug = debug
        get_name = {int(k): str(k).split()[0] for k in self.GL_SETTERS.keys()}
        for var in range(GL.glGetProgramiv(self.glid, GL.GL_ACTIVE_UNIFORMS)):
            name, size, type_ = GL.glGetActiveUniform(self.glid, var)
            name = name.decode().split('[')[0]   # remove array characterization
            args = [GL.glGetUniformLocation(self.glid, name), size]
            # add transpose=True as argument for matrix types
            if type_ in {GL.GL_FLOAT_MAT2, GL.GL_FLOAT_MAT3, GL.GL_FLOAT_MAT4}:
                args.append(True)
            if debug:
                call = self.GL_SETTERS[type_].__name__
                print(f'uniform {get_name[type_]} {name}: {call}{tuple(args)}')
            self.uniforms[name] = (self.GL_SETTERS[type_], args)

    def set_uniforms(self, uniforms):
        """ set only uniform variables that are known to shader """
        for name in uniforms.keys() & self.uniforms.keys():
            set_uniform, args = self.uniforms[name]
            set_uniform(*args, uniforms[name])

    def __del__(self):
        GL.glDeleteProgram(self.glid)  # object dies => destroy GL object

    GL_SETTERS = {
        GL.GL_UNSIGNED_INT:      GL.glUniform1uiv,
        GL.GL_UNSIGNED_INT_VEC2: GL.glUniform2uiv,
        GL.GL_UNSIGNED_INT_VEC3: GL.glUniform3uiv,
        GL.GL_UNSIGNED_INT_VEC4: GL.glUniform4uiv,
        GL.GL_FLOAT:      GL.glUniform1fv, GL.GL_FLOAT_VEC2:   GL.glUniform2fv,
        GL.GL_FLOAT_VEC3: GL.glUniform3fv, GL.GL_FLOAT_VEC4:   GL.glUniform4fv,
        GL.GL_INT:        GL.glUniform1iv, GL.GL_INT_VEC2:     GL.glUniform2iv,
        GL.GL_INT_VEC3:   GL.glUniform3iv, GL.GL_INT_VEC4:     GL.glUniform4iv,
        GL.GL_SAMPLER_1D: GL.glUniform1iv, GL.GL_SAMPLER_2D:   GL.glUniform1iv,
        GL.GL_SAMPLER_3D: GL.glUniform1iv, GL.GL_SAMPLER_CUBE: GL.glUniform1iv,
        GL.GL_FLOAT_MAT2: GL.glUniformMatrix2fv,
        GL.GL_FLOAT_MAT3: GL.glUniformMatrix3fv,
        GL.GL_FLOAT_MAT4: GL.glUniformMatrix4fv,
        GL.GL_IMAGE_2D: GL.glBindImageTexture,
    }

    def set_int(self, name, value):
        loc = GL.glGetUniformLocation(self.glid, name)
        if loc !=-1:
            GL.glUniform1i(loc, value)

    def set_image2d_read(self, name, image):
        loc = GL.glGetUniformLocation(self.glid, name)
        if loc !=-1:
            GL.glBindImageTexture(loc, image.glid, 0, GL.GL_FALSE, 0, GL.GL_READ_ONLY, image.preset.internal_format)
    
    def set_image2d_read_write(self, name, image):
        loc = GL.glGetUniformLocation(self.glid, name)
        if loc !=-1:
            GL.glBindImageTexture(loc, image.glid, 0, GL.GL_FALSE, 0, GL.GL_READ_WRITE, image.preset.internal_format)

    def set_image2d_write(self, name, image):
        loc = GL.glGetUniformLocation(self.glid, name)
        if loc !=-1:
            GL.glBindImageTexture(loc, image.glid, 0, GL.GL_FALSE, 0, GL.GL_WRITE_ONLY, image.preset.internal_format)

    def bind(self):
        GL.glUseProgram(self.glid)