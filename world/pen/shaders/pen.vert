#version 330 core
in vec2 tex_coord;
in vec3 position;


uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;


out VS_OUTPUT {
    vec2 uv;
} OUTPUT;

void main() {
    OUTPUT.uv = tex_coord;
    gl_Position = projection * view * vec4(position, 1.);
}