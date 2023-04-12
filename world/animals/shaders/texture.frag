#version 330 core
in vec2 frag_tex_coords;

uniform sampler2D diffuse_map;
out vec4 out_color;

void main() {
    // on met la texture sur l'animal
    out_color = vec4(texture(diffuse_map, vec2(frag_tex_coords)).rgb, 1.0);    
}
