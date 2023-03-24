#version 430 core
#define M_PI 3.1415926535897932384626433832795

layout(local_size_x=16,local_size_y=16) in;

layout(binding=0,rg32f) writeonly uniform image2D tilde_hkt_dy; // height

layout(binding=1,rg32f) writeonly uniform image2D Dt_dx_dz; // choppiness

layout(binding=2,rg32f) readonly uniform image2D tilde_h0k; // initial factors

uniform int N;// resolution
uniform int L;// ocean size mesh
uniform float t;


vec2 mul_comp(vec2 z, vec2 w) {
	return vec2(z.x * w.x - z.y * w.y, z.y * w.x + z.x * w.y);
}

void main(void)
{
	ivec2 loc1	= ivec2(gl_GlobalInvocationID.xy);
	ivec2 loc2	= ivec2(N - loc1.x, N - loc1.y);

	vec2 h_tk;
	vec2 h0_k	= imageLoad(tilde_h0k, loc1).rg;
	vec2 h0_mk	= imageLoad(tilde_h0k, loc2).rg;

	vec2 k = (float(N/2) - loc1) * 2 * M_PI /L;


	float w_k = sqrt(9.81 * length(k));
	float cos_wt = cos(w_k * t);
	float sin_wt = sin(w_k * t);

	h_tk.x = cos_wt * (h0_k.x + h0_mk.x) - sin_wt * (h0_k.y + h0_mk.y);
	h_tk.y = cos_wt * (h0_k.y - h0_mk.y) + sin_wt * (h0_k.x - h0_mk.x);

	float kn2 = dot(k, k);
	vec2 nk = vec2(0.0, 0.0);

	if (kn2 > 1e-12)
		nk = normalize(k);
	// horitonzal displacement
	vec2 Dt_x = vec2(h_tk.y * nk.x, -h_tk.x * nk.x);
	vec2 iDt_z = vec2(h_tk.x * nk.y, h_tk.y * nk.y);

	// write ouptut
	imageStore(tilde_hkt_dy, loc1, vec4(h_tk, 0.0, 0.0));
	imageStore(Dt_dx_dz, loc1, vec4(Dt_x+ iDt_z, 0.0, 0.0));

}
