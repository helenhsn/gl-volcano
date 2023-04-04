#version 430 core

layout(std430, binding=4) buffer pos {   
    vec4 positions[];
};
layout(std430, binding=5) buffer vel {   
    vec4 velocities[];
};

layout(std430, binding=6) buffer init_pos {   
    vec4 positions_0[];
};

layout(std430, binding=7) buffer init_vel {   
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
    // x(t) = v_x0*t + x0
    // z(t) = v_z0*t + z0
    // y(t) = -1/2 g t^2 + v_y0*t + y0
    
    uint loc = gl_GlobalInvocationID.x;

    positions[loc].w -= 1.0; 
    if (positions[loc].w > 0.0) {
        positions[loc].xyz += velocities[loc].xyz * dt;
        velocities[loc].y -= 9.81 * dt * 4.0;
    } else {
        positions[loc] = positions_0[loc];
        velocities[loc].xyz = velocities_0[loc].xyz;
    }    
}