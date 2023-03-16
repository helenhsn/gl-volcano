#version 330 core

in VS_OUTPUT {
    vec3 position;
    vec2 uv;
    vec3 normal;
} IN;

const vec3 light_pos = vec3(0.0, 100.0, 0.0);
const vec3 light_col = vec3(1.);
const vec3 ambient_light = vec3(0.7255, 0.9216, 0.9804);
const vec3 albedo = vec3(0.0706, 0.3608, 0.2157);

uniform vec3 w_camera_position;

out vec4 out_color;


#define OCTAVES 3
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

// height displacement
float fbm(in vec2 p) {
    float value = 0.;
    float gain = 1.0;
    float amp = 10.5;
    for (int i = 0; i < OCTAVES; i++) {
        value += amp * noise(p);
        amp *= gain + .1;
    }
    return value;
}
float gaussian_volcano(vec2 p) {
    vec2 temp = -(p+13)*(p+13)/0.2;
    return 500.*exp(temp.x + temp.y);
}

float gaussian_map(vec2 p) {
    vec2 temp1 = -p*p/11.0;
    vec2 temp2 = -p*p;
    vec2 temp3 = -(p-6)*(p-6)/3.0;
    vec2 temp4 = -(p+6)*(p+6)/30.0;

    return 3*exp(temp1.x + temp1.y) - 3*exp(temp2.x + temp2.y) + 2*exp(temp3.x + temp3.y) + exp((temp4.x + temp4.y)/2.0);
}

float height_terrain(in vec2 p) {
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
    float spec = pow(max(dot(n, h), 0.0), 32);
    vec3 specular = spec * albedo;

    out_color.rgb = specular + ambient + diffuse;

    // if (p.x > 256 && p.z > 256)
    //     out_color.rgb = noise(p.xz);
    //out_color.rgb = pow(out_color.rgb, vec3(1.0/2.2)); // gamma correction
    out_color = vec4(1.);
}