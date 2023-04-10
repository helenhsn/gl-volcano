#version 330 core

uniform sampler2D diffuse_map;
uniform sampler2D second_texture;
in vec2 frag_tex_coords;
out vec4 out_color;

void main() {
    //on fait les deux textures
    out_color = vec4(texture(diffuse_map, vec2(frag_tex_coords)).rgb, 1.0);    
}
