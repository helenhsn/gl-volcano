#version 330 core

in vec3 position;
in vec2 uv;
in vec3 normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;


#define MIN_HEIGHT 30.0
#define AMP_HEIGHT 50.0
#define MIN_SPREAD 500.0

#define OCTAVES 3 

out VS_OUTPUT {
    vec3 position;
    vec2 uv;
    vec3 normal;
} OUTPUT;


/************************ NOISE ***************/

mat2 Rotate(float th) {
    return mat2(cos(th), sin(th), -sin(th), cos(th)); 
}


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

float fbm (in vec2 st, float amp, float gain) {
    float value = 0.;
    //loop
    for (int i = 0; i < OCTAVES; i++) {
        value += amp * noise(st);
        st *= Rotate(-1.5);
        amp += gain + .01;
    }
    return value;
}


/***************************************************/

float gaussian_volcano(vec2 p) {
    float translate = MIN_HEIGHT*3.0;
    vec2 temp = -(p+translate)*(p+translate) / (MIN_SPREAD * 10);
    vec2 temp2 = -(p+translate)*(p+translate)/30.0;
    float noise = fbm(p, 0.2 + sin(p.y*2.)*0.6 * sin(p.x*2.)*0.9 - cos(1.1)*0.9, .8);
    return AMP_HEIGHT*(4.0*exp(temp.x + temp.y) - 30.0*exp(temp2.x + temp2.y));
}

float gaussian_map(vec2 p) {
    float translate = MIN_HEIGHT*2.0;
    vec2 temp = -(p-translate)*(p+translate)/(MIN_SPREAD*12.0);
    return AMP_HEIGHT *2.*exp(temp.x + temp.y);
}

float height_terrain(in vec2 p) {
    float noise = fbm(p, 0.2 + sin(p.y*2.)*0.6 * sin(p.x*2.)*0.9 - cos(1.1)*0.9, .8);
    return gaussian_volcano(p);
}

vec3 get_normal(vec3 p) {
    vec2 eps = vec2(0.01, 0.0);
    vec3 n = vec3(
        height_terrain(p.xz+eps.xy) - height_terrain(p.xz - eps.xy), 
        2.0 * eps.x,
        height_terrain(p.xz+eps.yx) - height_terrain(p.xz - eps.yy)
        );
    return normalize(n);
}

void main() {
    OUTPUT.uv = vec2(height_terrain(position.xz));
    OUTPUT.position = position;
    OUTPUT.normal = OUTPUT.normal;
    gl_Position = projection * view * model * vec4(OUTPUT.position, 1);
}