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

    if (positions[loc].w > 0.01) {
        positions[loc].xyz += velocities[loc].xyz * dt;

        if (positions[loc].w < 0.1 && positions[loc].y > 800.0) {
            positions[loc].w *= 0.96;
            velocities[loc].y *= 0.99; // decrease the speed by 1% each frame (we want smoke to be there much longer)
         } else {
            positions[loc].w *= 0.9;
        }
        if (positions[loc].w > 0.9)
            velocities[loc].x *= velocities[loc].x < 0.0 ? 1.02 : 1.005 ; // decrease the speed by 1% each frame (we want smoke to be there much longer)
            velocities[loc].z *= velocities[loc].z < 0.0 ? 1.02 : 1.005 ; // decrease the speed by 1% each frame (we want smoke to be there much longer)
            
    } else {
        positions[loc] = positions_0[loc];
        velocities[loc].xyz = velocities_0[loc].xyz;
    }    
}