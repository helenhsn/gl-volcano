#version 330 core

in vec3 position;
in vec2 uv;
in vec3 normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform sampler2D displacement;


out VS_OUTPUT {
    vec3 position;
    vec2 uv;
    vec3 normal;
} OUTPUT;

void main() {
    vec2 uv = fract(uv+ 1./256.);
    vec3 d = texture(displacement, uv).rgb;
    OUTPUT.uv = uv;
    vec3 new_pos = position + d;
    OUTPUT.position = (model * vec4(new_pos,1)).xyz;
    OUTPUT.normal = normal;
    gl_Position = projection * view * model * vec4(new_pos, 1);
}