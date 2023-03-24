#version 430

#define TWO_PI	6.2831853071795864
#define RES 256
#define LOG2_RES 8

layout (rg32f, binding = 0) uniform readonly image2D readbuff;
layout (rg32f, binding = 1) uniform writeonly image2D writebuff;

vec2 mul(vec2 z, vec2 w) { // multiplication btwn 2 complex 2D vectors
	return vec2(z.x * w.x - z.y * w.y, z.y * w.x + z.x * w.y);
}

shared vec2 pingpong[2][RES];

layout (local_size_x = RES) in;
void main()
{
	const float N = float(RES);

	int z = int(gl_WorkGroupID.x);
	int x = int(gl_LocalInvocationID.x);

	int nj = (bitfieldReverse(x) >> (32 - LOG2_RES)) & (RES - 1);
	pingpong[0][nj] = imageLoad(readbuff, ivec2(z, x)).rg;;

	barrier();

	// butterfly passes
	int src = 0;

	for (int s = 1; s <= LOG2_RES; ++s) {
		int m = 1 << s;				// butterfly group height
		int mh = m >> 1;			// butterfly group half height

		// k = n * N / 2^stage)
		int k = (x * (RES / m));
		int i = (x & ~(m - 1));		// butterfly group starting offset
		int j = (x & (mh - 1));		// butterfly index in group

		// twiddle factor W_N^k

		// TODO : compute W_N_k in advance in cpu and store it in a txt
		float theta = (TWO_PI * float(k)) / N;
		vec2 W_N_k = vec2(cos(theta), sin(-theta));

		vec2 input1 = pingpong[src][i + j + mh];
		vec2 input2 = pingpong[src][i + j];

		src = 1 - src;
		pingpong[src][x] = input2 + mul(W_N_k, input1);

		barrier();
	}

	// STEP 3: write output
	vec2 result = pingpong[src][x];
	imageStore(writebuff, ivec2(x, z), vec4(result, 0.0, 1.0));
}