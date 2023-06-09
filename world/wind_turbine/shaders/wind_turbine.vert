#version 330 core

// global color
uniform vec3 global_color;

// input attribute variable, given per vertex
in vec3 position;
in vec3 color;
in vec3 normal;

// global matrix variables
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;


out VS_OUTPUT {
    vec3 position;
    vec3 normal;
} OUT;



void main() {
    // tell OpenGL how to transform the normal and the position given the model matrix
    OUT.normal = (model * vec4(normal, 0)).xyz;
    OUT.position = (model * vec4(position, 1)).xyz;
    // tell OpenGL how to transform the vertex to clip coordinates
    gl_Position = projection * view * model * vec4(position, 1);
}
