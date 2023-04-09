#version 330 core

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
//on ajoute cette ligne exo 2
in vec2 tex_coord;
in vec3 position;

out vec2 frag_tex_coords;

void main() {
    gl_Position = projection * view * model * vec4(position, 1);
    //on ajoute cette ligne exo 2
    frag_tex_coords = tex_coord;
}
