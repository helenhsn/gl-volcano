#version 430 core 

layout (binding=0, rgba32f) uniform readonly image2D displacement;
layout (binding=1, rgba32f) uniform writeonly image2D gradients;

layout (local_size_x = 16, local_size_y=16) in;

uniform int L;
uniform int N;

void main() {
    ivec2 loc = ivec2(gl_GlobalInvocationID.xy);

    ivec2 left = (loc - ivec2(1, 0)) & (N-1);
    ivec2 right = (loc + ivec2(1, 0)) & (N-1);
    ivec2 bottom = (loc - ivec2(0, 1)) & (N-1);
    ivec2 top = (loc + ivec2(0, 1)) & (N-1);

    vec3 displacement_left = imageLoad(displacement, left).rgb;
    vec3 displacement_right = imageLoad(displacement, right).rgb;
    vec3 displacement_bottom = imageLoad(displacement, bottom).rgb;
    vec3 displacement_top = imageLoad(displacement, top).rgb;

    float N_f32 = float(N);
    float L_f32 = float(L);

    // computing the slope vector ( Delta(h))
    vec2 grad = vec2(displacement_left.g - displacement_right.g, displacement_bottom.g - displacement_top.g);

    vec2 dx_D = (displacement_right.xz - displacement_left.xz) * (N_f32/L_f32);
    vec2 dy_D = (displacement_top.xz - displacement_bottom.xz) * (N_f32/L_f32);

    // jacobian 
    float jacobian = (1.0 + dx_D.x) * (1.0 + dy_D.y) - dx_D.y * dy_D.x;

    imageStore(gradients, loc, vec4(grad, 2*L_f32/N_f32, jacobian));
}