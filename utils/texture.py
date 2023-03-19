import OpenGL.GL as GL              # standard Python OpenGL wrapper
from PIL import Image               # load texture maps


class TexturePreset:
    def __init__(self, wrap_s, wrap_t, mag_filter, min_filter, internal_format, format):
        self.wrap_s = wrap_s
        self.wrap_t = wrap_t
        self.mag_filter = mag_filter
        self.min_filter = min_filter
        self.internal_format = internal_format
        self.format = format


# -------------- OpenGL Texture Wrapper ---------------------------------------
class Texture:
    """ Helper class to create and automatically destroy textures """
    def __init__(self, tex_file, wrap_mode=GL.GL_REPEAT,
                 mag_filter=GL.GL_LINEAR, min_filter=GL.GL_LINEAR_MIPMAP_LINEAR,
                 tex_type=GL.GL_TEXTURE_2D):
        self.glid = GL.glGenTextures(1)
        self.type = tex_type
        try:
            # imports image as a numpy array in exactly right format
            tex = Image.open(tex_file).convert('RGBA')
            GL.glBindTexture(tex_type, self.glid)
            GL.glTexImage2D(tex_type, 0, GL.GL_RGBA, tex.width, tex.height,
                            0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, tex.tobytes())
            GL.glTexParameteri(tex_type, GL.GL_TEXTURE_WRAP_S, wrap_mode)
            GL.glTexParameteri(tex_type, GL.GL_TEXTURE_WRAP_T, wrap_mode)
            GL.glTexParameteri(tex_type, GL.GL_TEXTURE_MIN_FILTER, min_filter)
            GL.glTexParameteri(tex_type, GL.GL_TEXTURE_MAG_FILTER, mag_filter)
            GL.glGenerateMipmap(tex_type)
            print(f'Loaded texture {tex_file} ({tex.width}x{tex.height}'
                  f' wrap={str(wrap_mode).split()[0]}'
                  f' min={str(min_filter).split()[0]}'
                  f' mag={str(mag_filter).split()[0]})')
        except FileNotFoundError:
            print("ERROR: unable to load texture file %s" % tex_file)

    def __del__(self):  # delete GL texture from GPU when object dies
        GL.glDeleteTextures(self.glid)

    @classmethod
    def new_from_vec(self, dimensions, wrap_s, wrap_t, mag_filter, min_filter, internal_format, format, data):
        self.id = GL.glGenTextures(1)
        self.dimensions = (int(dimensions[0]), int(dimensions[1])) # dimensions = width, height
        self.preset = TexturePreset(wrap_s=wrap_s, wrap_t=wrap_t, mag_filter=mag_filter, min_filter=min_filter, internal_format=internal_format, format=format)

        # binding the texture
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, self.preset.wrap_t)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, self.preset.wrap_s)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, self.preset.min_filter)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, self.preset.mag_filter)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, self.preset.internal_format, self.dimensions[0], self.dimensions[1], 0, self.preset.format, GL.GL_FLOAT, data)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    @classmethod
    def new_from_none(self, dimensions, wrap_s, wrap_t, mag_filter, min_filter, internal_format, format):
        self.id = GL.glGenTextures(1)
        self.dimensions = (int(dimensions[0]), int(dimensions[1])) # dimensions = width, height
        self.preset = TexturePreset(wrap_s=wrap_s, wrap_t=wrap_t, mag_filter=mag_filter, min_filter=min_filter, internal_format=internal_format, format=format)

        # binding the texture
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, self.preset.wrap_t)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, self.preset.wrap_s)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, self.preset.min_filter)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, self.preset.mag_filter)
        GL.glTexStorage2D(GL.GL_TEXTURE_2D, 1, self.preset.internal_format, self.dimensions[0], self.dimensions[1])
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

# -------------- Textured mesh decorator --------------------------------------
class Textured:
    """ Drawable mesh decorator that activates and binds OpenGL textures """
    def __init__(self, drawable, **textures):
        self.drawable = drawable
        self.textures = textures

    def draw(self, primitives=GL.GL_TRIANGLES, **uniforms):
        for index, (name, texture) in enumerate(self.textures.items()):
            GL.glActiveTexture(GL.GL_TEXTURE0 + index)
            GL.glBindTexture(texture.type, texture.glid)
            uniforms[name] = index
        self.drawable.draw(primitives=primitives, **uniforms)
