#version 430 core

layout (local_size_x = 16, local_size_y = 16) in;

layout (binding = 0, rgba32f) writeonly uniform image2D displacement;
layout (binding = 1, rg32f) readonly uniform image2D height_field;
layout (binding = 2, rg32f) readonly uniform image2D choppy_field;


uniform int N;

void main(void)
{
	const float choppiness = -75.0;
	const float height_factor = 70.0;

	ivec2 loc = ivec2(gl_GlobalInvocationID.xy);

	// ifft 
	float sign_correction = ((((loc.x + loc.y) & 1) == 1) ? -1.0 : 1.0) / float(N*N);

	float h = sign_correction * imageLoad(height_field, loc).x;
	vec2 D = sign_correction * imageLoad(choppy_field, loc).xy;

	imageStore(displacement, loc, vec4(D.x * choppiness, h * height_factor, D.y * choppiness, 1.0));

}