#version 430 core

layout(std430, binding=0) buffer pos {   
    vec4 positions[];  
};

layout(std430, binding=2) buffer init_pos {   
    vec4 positions_0[];
};


out VS_OUTPUT {
    float lifetime;
    float size;
    vec3 pos;
    float initial_lifetime;
} OUTPUT;

void main() {

    // passing down to the geometry shader
    OUTPUT.lifetime = positions[gl_VertexID].w;
    OUTPUT.size = 30.0;
    OUTPUT.pos = positions[gl_VertexID].xyz;
    OUTPUT.initial_lifetime = positions_0[gl_VertexID].w;
    gl_Position = vec4(positions[gl_VertexID].xyz, 1);
}