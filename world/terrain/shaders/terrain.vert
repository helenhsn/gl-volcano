#version 330 core

in vec3 position;
in vec2 uv;
in vec3 normal;

uniform sampler2D map;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform int size;
uniform vec3 w_camera_position;

const vec3 fog_plane_point = vec3(0., 500., 0.);


float random(in vec2 uv)
{
    return fract(sin(dot(uv.xy, 
                         vec2(12.9898, 78.233))) * 
                 43758.5453123);
}

// Based on Morgan McGuire @morgan3d -> value noise
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

vec3 albedo_from_height(float height)
{


    vec3 colors[4];

    colors[0] = vec3(0.4667, 0.4627, 0.4471);
    colors[1] = vec3(0.1529, 0.3686, 0.251);
    colors[2] = vec3(0.0396, 0.0396, 0.0396);
    colors[3] = vec3(0.02);
    if(height < 0.0)
        return vec3(0.7333, 0.0549, 0.451);
    else
    {
        float hscaled = clamp((height - 250.0)/100, 0., 1.); //btw 0. && 1.
        vec3 base_color = vec3(0., 0., 1.);
        if (hscaled <= 0.08)
            return mix(colors[0], colors[1], hscaled*0.1);
        else
            return mix(colors[1], colors[3],  (hscaled - 0.08)/(1.0-0.08));
    }
}

float fog_from_height(vec3 pos) {
    return 1. - smoothstep(0,1.5, exp((pos.y-400.0)*0.002));
}

out VS_OUTPUT {
    vec3 position;
    vec2 uv;
    vec3 normal;
    vec3 albedo;
    float fog_plane_f;
} OUTPUT;

void main() {
    OUTPUT.uv = uv;

    vec4 map_coefs = texture(map, uv);
    
    vec3 pos = vec3(position.x, map_coefs.x, position.z);
    OUTPUT.position = (model * vec4(pos, 1.)).xyz;
    gl_Position = projection * view * vec4(OUTPUT.position, 1);
    OUTPUT.normal = map_coefs.yzw;
    OUTPUT.albedo = albedo_from_height(OUTPUT.position.y);
    OUTPUT.fog_plane_f = fog_from_height(OUTPUT.position);
}