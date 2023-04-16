#version 330 core

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
in vec2 tex_coord;
in vec3 position;

out vec2 frag_tex_coords;

out VS_OUTPUT {
    vec3 position;
} OUT;


void main() {
    OUT.position = (model * vec4(position, 1)).xyz;
    gl_Position = projection * view * model * vec4(position, 1);
    frag_tex_coords = tex_coord;
}
