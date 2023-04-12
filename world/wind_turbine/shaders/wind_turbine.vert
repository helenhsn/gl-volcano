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
    float fog_plane_f;
} OUT;


float fog_from_height(vec3 pos) {

    float hscaled = clamp((pos.y - 250.0)/100, 0., 1.); //btw 0. && 1.
    return 1. - smoothstep(0,1.5, exp((pos.y-400.0)*0.002));
}


void main() {
    // tell OpenGL how to transform the normal and the position given the model matrix
    OUT.normal = (model * vec4(normal, 0)).xyz;
    OUT.position = (model * vec4(position, 1)).xyz;
    OUT.fog_plane_f = fog_from_height(OUT.position);
    // tell OpenGL how to transform the vertex to clip coordinates
    gl_Position = projection * view * model * vec4(position, 1);
}
