#version 330 core

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform mat4 view;
uniform vec3 rgt;
uniform vec3 up;
uniform mat4 proj;

in VS_OUTPUT {
    float lifetime;
    float size;
    vec3 pos;
    float initial_lifetime;
} IN[];

out GS_OUTPUT {
    float lifetime;
    vec2 uv;
    vec3 pos;
} OUTPUT;

void main() {
    // we need to create a quad for each particle.
    vec3 pos = gl_in[0].gl_Position.xyz;
    float life_percentage = IN[0].lifetime/IN[0].initial_lifetime;
    mat4 view_proj = proj*view;

    // TOP RIGHT CORNER
    vec3 top_right = pos + (rgt + up) * IN[0].size;
    gl_Position = view_proj * vec4(top_right, 1.0);
    OUTPUT.lifetime = life_percentage;
    OUTPUT.uv = vec2(1., 1.);
    OUTPUT.pos = IN[0].pos;
    EmitVertex(); // new vertex

    // BOTTOM RIGHT CORNER
    vec3 bottom_right = pos + (rgt - up) * IN[0].size;
    gl_Position = view_proj * vec4(bottom_right, 1.0);
    OUTPUT.lifetime = life_percentage;
    OUTPUT.uv = vec2(1., 0.);
    OUTPUT.pos = IN[0].pos;

    EmitVertex(); // new vertex

     // TOP LEFT CORNER
    vec3 top_left = pos + (-rgt + up) * IN[0].size;
    gl_Position = view_proj * vec4(top_left, 1.0);
    OUTPUT.lifetime = life_percentage;
    OUTPUT.uv = vec2(0., 1.);
    OUTPUT.pos = IN[0].pos;

    EmitVertex(); // new vertex

    // BOTTOM LEFT CORNER
    vec3 bottom_left = pos - (rgt + up) * IN[0].size;
    gl_Position = view_proj * vec4(bottom_left, 1.0);
    OUTPUT.lifetime = life_percentage;
    OUTPUT.uv = vec2(0.);
    OUTPUT.pos = IN[0].pos;

    EmitVertex(); // new vertex

    EndPrimitive(); // new quad for 1 particle
}