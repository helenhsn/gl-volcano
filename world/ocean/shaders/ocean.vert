#version 330 core

in vec3 position;
in vec2 uv;
in vec3 normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform sampler2D displacement;
uniform sampler2D gradients;
uniform vec3 w_camera_position;

// removing tilling effect # TODO LN
#define BLEND_START  8    // m
#define BLEND_END    100  // m
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


out VS_OUTPUT {
    vec3 position;
    vec2 uv;
    vec3 normal;
} OUTPUT;

void main() {
    vec2 Uv = fract(uv+ 1./256.);

    vec3 d = texture(displacement, Uv).rgb;
    vec3 grad = texture(gradients, Uv).xzy;

    OUTPUT.uv = uv;
    vec3 new_pos = position + d;
    vec3 world_pos = (model * vec4(new_pos, 1.)).xyz;

    float noise_cliff = fbm(world_pos.xz, 1000.0, .55, 0.002, 2.0)*0.5 + 0.5; // gives a rusty appearance to our island
    float clamp_factor = smoothstep(-2300-700, -2300, length(world_pos.xz)+noise_cliff) -1 + smoothstep(2300+700, 2300, length(world_pos.xz)+noise_cliff);

    clamp_factor *= clamp_factor;
    OUTPUT.position = blend_height(world_pos, clamp_factor);
    OUTPUT.normal = blend_normal(grad, clamp_factor);
    gl_Position = projection * view * vec4(OUTPUT.position, 1);
}