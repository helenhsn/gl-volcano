#version 430 core

layout(std430, binding=0) buffer pos {   
    vec4 positions[];
};
layout(std430, binding=1) buffer vel {   
    vec4 velocities[];
};

layout(std430, binding=2) buffer init_pos {   
    vec4 positions_0[];
};

layout(std430, binding=3) buffer init_vel {   
    vec4 velocities_0[];
};

layout (local_size_x = 16) in;

uniform float dt;

float random(in vec2 uv)
{
    return fract(sin(dot(uv.xy, 
                         vec2(12.9898, 78.233))) * 
                 43758.5453123);
}

void main() {
    
    uint loc = gl_GlobalInvocationID.x;

    if (positions[loc].w > 0.001) {
        positions[loc].xyz += velocities[loc].xyz * dt;

        if (positions[loc].w < 0.05 && positions[loc].y > 1100.0) {
            positions[loc].w *= 0.95;
         } else {
            positions[loc].w *= 0.9;
        }
            
    } else {
        positions[loc] = positions_0[loc];
        velocities[loc].xyz = velocities_0[loc].xyz;
    }    
}