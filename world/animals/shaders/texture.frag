#version 330 core
in vec2 frag_tex_coords;

uniform sampler2D diffuse_map;
out vec4 out_color;

void main() {
    //on fait les deux textures
    out_color = vec4(texture(diffuse_map, vec2(frag_tex_coords)).rgb, 1.0);    
}
