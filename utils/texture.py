import OpenGL.GL as GL              # standard Python OpenGL wrapper
from PIL import Image               # load texture maps
import OpenGL.version as glversion

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

    def __del__(self):  # delete GL texture from GPU when object dies
        GL.glDeleteTextures(self.glid)

    def __init__(self, dimensions, wrap_s, wrap_t, mag_filter, min_filter, internal_format, format, data=None, is_vec=False, path_img=None):
        self.glid = GL.glGenTextures(1)
        self.type = GL.GL_TEXTURE_2D
        self.dimensions = (int(dimensions[0]), int(dimensions[1])) # dimensions = width, height
        self.preset = TexturePreset(wrap_s=wrap_s, wrap_t=wrap_t, mag_filter=mag_filter, min_filter=min_filter, internal_format=internal_format, format=format)
        if path_img:
            # imports image as a numpy array in exactly right format
            tex = Image.open(path_img).convert('RGBA')
            GL.glBindTexture(self.type, self.glid)
            GL.glTexParameteri(self.type, GL.GL_TEXTURE_WRAP_S, wrap_s)
            GL.glTexParameteri(self.type, GL.GL_TEXTURE_WRAP_T, wrap_t)
            GL.glTexParameteri(self.type, GL.GL_TEXTURE_MIN_FILTER, min_filter)
            GL.glTexParameteri(self.type, GL.GL_TEXTURE_MAG_FILTER, mag_filter)
            GL.glTexImage2D(self.type, 0, GL.GL_RGBA, tex.width, tex.height,
                            0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, tex.tobytes())
            print(f'Loaded texture {path_img} ({tex.width}x{tex.height}'
                   f' wrap={str(wrap_t).split()[0]}'
                   f' min={str(min_filter).split()[0]}'
                   f' mag={str(mag_filter).split()[0]})')
        else:
            # binding the texture
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.glid)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, self.preset.wrap_t)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, self.preset.wrap_s)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, self.preset.min_filter)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, self.preset.mag_filter)
            if is_vec:
                GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, self.preset.internal_format, self.dimensions[0], self.dimensions[1], 0, self.preset.format, GL.GL_FLOAT, data)
            else:
                GL.glTexStorage2D(GL.GL_TEXTURE_2D, 1, self.preset.internal_format, dimensions[0], dimensions[1])
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
