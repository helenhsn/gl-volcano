#version 430 core

in vec3 position;
in vec2 uv;
in vec3 normal;

layout(std430, binding=8) buffer model_matrices {   
    mat4 model_matrix[];  
};

uniform mat4 view;
uniform mat4 projection;
uniform sampler2D displacement;
uniform sampler2D gradients;
uniform vec3 w_camera_position;
uniform vec2 wind_dir;
uniform float t;

// removing tilling effect # TODO LN
#define BLEND_START  8    // m
#define BLEND_END    10000  // m


#define OCTAVES 6


float random(in vec2 uv)
{
    return fract(sin(dot(uv.xy, 
                         vec2(12.9898, 78.233))) * 
                 43758.5453123);
}

// Based on Morgan McGuire @morgan3d
// https://www.shadertoy.com/view/4dS3Wd
float noise (in vec2 _st) {
    vec2 i = floor(_st);
    vec2 f = fract(_st);

    // Four corners in 2D of a tile
    float a = random(i);
    float b = random(i + vec2(1.0, 0.0));
    float c = random(i + vec2(0.0, 1.0));
    float d = random(i + vec2(1.0, 1.0));

    vec2 u = f * f * (3.0 - 2.0 * f);

    return mix(a, b, u.x) +
            (c - a)* u.y * (1.0 - u.x) +
            (d - b) * u.x * u.y;
}

float fbm (vec2 p, float amp, float gain, float freq, float lacunarity) {
    float value = 0.;
    //loop
    for (int i = 0; i < OCTAVES; i++) {
        value += amp * noise(vec2(p.x * freq, p.y * freq));
        amp *= gain;
        freq *= lacunarity;
    }
    return value;
}

vec3 blend_height(in vec3 p, float clamp_factor) {

    return vec3(p.x, (1. - clamp_factor) * p.y + 100, p.z);
}

vec3 blend_normal(in vec3 n, float clamp_factor) {
    return mix(n, vec3(0., 1., 0.), clamp_factor);
}


/********************** REMOVING TILING EFFECT *************/ 

vec2 hash(vec2 v) {
    return vec2
    (
        fract(sin(dot(v, vec2(763., 827.))+26.) * 9283.),
        fract(sin(dot(v, vec2(135., 236.))+145.) * 422.)
    );
}

float perlin(vec2 pos) {
    vec2 cube_coords = vec2(floor(pos.x), floor(pos.y));
    vec2 coords = pos - cube_coords;
    return mix(
        mix (
            dot(hash(cube_coords), coords),
            dot(hash(vec2(cube_coords.x + 1., cube_coords.y)), vec2(coords.x - 1., coords.y)),
            smoothstep(0., 1., coords.x)
        ),
        mix (
            dot(hash(vec2(cube_coords.x, cube_coords.y + 1.)), vec2(coords.x, coords.y - 1.)),
            dot(hash(vec2(cube_coords.x + 1., cube_coords.y + 1.)), vec2(coords.x - 1., coords.y - 1.)),
            smoothstep(0., 1., coords.x)
        ),
        smoothstep(0., 1., coords.y)
    );
}

float get_perlin_blend(vec2 p, vec3 perlinFrequency, vec3 perlinAmplitude) {
    float p0 = perlin(p * perlinFrequency.x + wind_dir*t*0.1);
    float p1 = perlin(p * perlinFrequency.y + wind_dir*t*0.1);
    float p2 = perlin(p * perlinFrequency.z + wind_dir*t*0.1);
    return dot(vec3(p0, p1, p2), perlinAmplitude);
}

vec3 get_perlin_normal(vec2 p, vec3 perlinFrequency, vec3 perlinAmplitude) {
    vec2 eps = vec2(0.01, 0.0);

    // finite differences
    vec3 n = vec3(
        get_perlin_blend(p+eps.xy, perlinFrequency, perlinAmplitude) - get_perlin_blend(p - eps.xy, perlinFrequency, perlinAmplitude), 
        2.0 * eps.x,
        get_perlin_blend(p+eps.yx, perlinFrequency, perlinAmplitude) - get_perlin_blend(p - eps.yy, perlinFrequency, perlinAmplitude)
        );
    return n;
}

// removing tiling effect due to the repetition of the same ocean texture
// to use if framerate allows it...
void tiling(inout vec3 d, inout vec3 n, vec3 p) {
    vec3 v = w_camera_position - p;
    float v_length = length(v);
    float factor = clamp((BLEND_END - v_length)/(BLEND_END - BLEND_START), 0., 1.);
    float perl = 0.0;
    vec3 perlin_n = vec3(0.);
    if (factor < 1.) {
        perl = get_perlin_blend(p.xz, vec3(0.001, 0.004, 0.002), vec3(105.65, 110.90, 100.77));
        perlin_n = get_perlin_normal(p.xz, vec3(0.001, 0.004, 0.02), vec3(105.65, 110.90, 100.77));
    }
    d = mix(vec3(perl), d, factor*factor);
    n.xz = mix(perlin_n.xz, n.xz, factor*factor);

}

out VS_OUTPUT {
    vec3 position;
    vec2 uv;
    vec3 normal;
    vec3 col;

} OUTPUT;

void main() {
    vec2 Uv = fract(uv+ 1./256.);

    mat4 model = transpose(model_matrix[gl_InstanceID]);

    vec3 d = texture(displacement, Uv).rgb + vec3(0., 70.0, 0.0);
    vec3 grad = texture(gradients, Uv).xzy;

    OUTPUT.uv = uv;
    vec3 n = grad;

    // removing tiling effect
    //tiling(d, n, (model*vec4(position, 1.)).xyz);
    
    vec3 new_pos = position + d;

    vec3 world_pos = (model * vec4(new_pos, 1.)).xyz;

    // flattening ocean under the island
    float noise_cliff = fbm(world_pos.xz, 1000.0, .55, 0.002, 2.0)*0.5 + 0.5; // gives a rusty appearance to our island
    float clamp_factor = smoothstep(-2000-700, -2000, length(world_pos.xz)+noise_cliff) -1 + smoothstep(2000+700, 2000, length(world_pos.xz)+noise_cliff);
    clamp_factor *= clamp_factor;

    OUTPUT.position = blend_height(world_pos, clamp_factor);
    OUTPUT.normal = blend_normal(n, clamp_factor);
    OUTPUT.col = OUTPUT.position;
    gl_Position = projection * view * vec4(OUTPUT.position, 1);
}