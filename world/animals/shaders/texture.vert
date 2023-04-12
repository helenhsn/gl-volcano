#version 330 core

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
in vec2 tex_coord;
in vec3 position;

out vec2 frag_tex_coords;

out VS_OUTPUT {
    vec3 position;
    float fog_plane_f;
} OUT;


float fog_from_height(vec3 pos) {

    float hscaled = clamp((pos.y - 250.0)/100, 0., 1.); //btw 0. && 1.
    return 1. - smoothstep(0,1.5, exp((pos.y-400.0)*0.002));
}


void main() {
    OUT.position = (model * vec4(position, 1)).xyz;
    OUT.fog_plane_f = fog_from_height(OUT.position);
    gl_Position = projection * view * model * vec4(position, 1);
    frag_tex_coords = tex_coord;
}
