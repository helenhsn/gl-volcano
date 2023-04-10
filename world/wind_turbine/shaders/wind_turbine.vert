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

// interpolated color for fragment shader, intialized at vertices

out VS_OUTPUT {
    vec3 position;
    vec3 normal;
} OUT;


void main() {
    // initialize interpolated colors at vertices
    OUT.normal = (model * vec4(normal, 0)).xyz;
    OUT.position = (model * vec4(position, 1)).xyz;
    // tell OpenGL how to transform the vertex to clip coordinates
    gl_Position = projection * view * model * vec4(position, 1);
}
