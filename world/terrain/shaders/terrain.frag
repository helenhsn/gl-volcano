#version 330 core

in VS_OUTPUT {
    vec3 position;
    vec2 uv;
    vec3 normal;
} IN;

const vec3 light_pos = vec3(-10000.0, 10000.0, -10000.0);
const vec3 light_col = vec3(1.);
const vec3 ambient_light = vec3(0.7255, 0.9216, 0.9804);
const vec3 albedo = vec3(0.1059, 0.0627, 0.0078);

uniform vec3 w_camera_position;
uniform mat4 model;
uniform int size;

float total_size = 2*float(size);
float min_spread = 10*total_size;

out vec4 out_color;

#define OCTAVES 6
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
float smin( float a, float b, float k )
{
    float h = clamp( 0.5+0.5*(b-a)/k, 0.0, 1.0 );
    return mix( b, a, h ) - k*h*(1.0-h);
}

float max (float a, float b) {
    return a >= b ? a : b;
}

float min (float a, float b) {
    return a <= b ? a : b;
}


float volcano(vec2 p, float noise) {
    float translate = 0.0;
    vec2 trans = p+translate;
    vec2 mult = (trans)*(trans);
    vec2 temp = -mult/(min_spread*25);
    vec2 temp2 = -mult/30.0;
    float value_1 = AMP_HEIGHT*(10.0*exp(temp.x + temp.y) - 30.0*exp(temp2.x + temp2.y));

    float f1 = ((length(mult))*0.3-10)+160;
    float f2 = (abs((length(trans))*0.35)-10)*(length(mult))*0.01+205;
    float value_2 = min(f1,f2)  + 280;

    return smin(value_1, value_2, 2) + 150 + noise*1.5;
}


float height_terrain(in vec2 p) {

    float clamp_factor = smoothstep(-1000-300, -1000, length(p)) -1 + smoothstep(1000+300, 1000, length(p));

    float noise = fbm(p, 100.0, .45, 0.009, 2.0); // gives a rusty appearance to our island

    float volcano_height = volcano(p, noise);
    volcano_height = volcano_height*(smoothstep(900.0, 0, length(p))*0.9 + 0.2);
    return clamp_factor*(volcano_height+50) - 75;
}

vec3 get_normal(vec3 p) {
    vec2 eps = vec2(0.01, 0.0);
    // finite differences
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
    vec3 n = get_normal(p);
    vec3 l = normalize(light_pos - p); // light dir
    vec3 h = normalize(l + v); //halfway vector

    // ambient light
    vec3 ambient = 0.1 * ambient_light;

    // diffuse light
    float dif = max(dot(n, l), 0.0);
    vec3 diffuse = dif * light_col;

    // specular light
    float spec = pow(max(dot(n, h), 0.0), 4);
    vec3 specular = spec * light_col;

    out_color.rgb = specular*0.5 + ambient + diffuse * albedo;
    //out_color.rgb = pow(out_color.rgb, vec3(1.0/2.2)); // gamma correction
}
    
