#version 330 core
in vec3 position;
in vec3 normal;
in vec2 uv;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;


out VS_OUTPUT {
    vec2 uv;
} OUTPUT;

void main() {
    OUTPUT.uv = uv;
    gl_Position = projection * view * vec4(position, 1.);
}