#version 330 core

uniform sampler2D diffuse_map;
uniform sampler2D second_texture;
in vec2 frag_tex_coords;
out vec4 out_color;

void main() {
    //on fait les deux textures
    vec4 couleur1 = texture(diffuse_map, frag_tex_coords);
    vec4 couleur2 = texture(second_texture, frag_tex_coords);
    // 1- alpha * couleur1 + alpha * couleur2 (alpha = couleur2.a)
    out_color = mix(couleur1, couleur2, couleur2.a);    
}
