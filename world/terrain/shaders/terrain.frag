#version 330 core

in VS_OUTPUT {
    vec3 position;
    vec2 uv;
    vec3 normal;
} IN;

const vec3 light_pos = vec3(0.0, 1000.0, -100.0);
const vec3 light_col = vec3(1.);
const vec3 ambient_light = vec3(0.7255, 0.9216, 0.9804);
const vec3 albedo = vec3(0.0706, 0.3608, 0.2157);

uniform vec3 w_camera_position;
uniform mat4 model;
uniform int size;

float total_size = 2*float(size);
float min_spread = 10*total_size;

out vec4 out_color;

#define OCTAVES 3

#define MIN_HEIGHT 30.0
#define AMP_HEIGHT 50.0

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


/***************************************************/

float gaussian_volcano(vec2 p) {
    float translate = MIN_HEIGHT*3.0;
    vec2 temp = -(p+translate)*(p+translate) / min_spread;
    vec2 temp2 = -(p+translate)*(p+translate)/30.0;
    //loat noise = fbm(p, 0.2 + sin(p.y*2.)*0.6 * sin(p.x*2.)*0.9 - cos(1.1)*0.9, .8);
    return AMP_HEIGHT*(4.0*exp(temp.x + temp.y) - 30.0*exp(temp2.x + temp2.y));
}

float gaussian_map(vec2 p) {
    float loc1 = (size-3.0)/2.0;     
    float loc2 = (size-2.8)/2.0;     
    float loc3 = (size-1.2)/2.0;     
    vec2 temp = -(p+loc1)*(p+loc1) / min_spread;
    vec2 temp2 = -(p-loc2)*(p-loc2) / (min_spread*2.);
    vec2 temp3 = -(p-loc3)*(p-loc3) / (min_spread*3.2);
    vec2 temp4 = -(p-loc1)*(p-loc1) / (min_spread*0.7);
    vec2 temp5 = -(p-loc3)*(p-loc3) / min_spread;
    return AMP_HEIGHT*(1.5*exp(temp.x + temp.y) + 1.8*exp(temp2.x + temp2.y) + exp(temp3.x + temp3.y));
}


float height_terrain(in vec2 p) {
    float noise = fbm(p, 1.0, 0.7, 0.01, 2.0);
    return 10.0*noise;
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
    vec3 p = IN.position;
    vec3 v = normalize(w_camera_position - p); // view dir
    vec3 n = IN.normal;
    vec3 l = normalize(light_pos - p); // light dir
    vec3 h = normalize(l + v); //halfway vector

    // ambient light
    vec3 ambient = 0.1 * ambient_light;

    // diffuse light
    float dif = max(dot(n, l), 0.0);
    vec3 diffuse = dif * light_col;

    // specular light
    float spec = pow(max(dot(n, h), 0.0), 256);
    vec3 specular = spec * light_col;

    out_color.rgb = specular*0.5 + ambient + diffuse * albedo;
    out_color.rgb = pow(out_color.rgb, vec3(1.0/2.2)); // gamma correction
}
    
