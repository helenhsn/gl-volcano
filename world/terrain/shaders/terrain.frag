#version 330 core

in VS_OUTPUT {
    vec3 position;
    vec2 uv;
    vec3 normal;
} IN;

const vec3 light_col = vec3(1.);
const vec3 ambient_light = vec3(0.2196, 0.5922, 0.7059);
uniform vec3 w_camera_position;

out vec4 out_color;
uniform vec3 light_pos;

vec3 albedo_from_height(float height)
{


    vec3 colors[4];

    colors[0] = vec3(0.4784, 0.3176, 0.1569);
    colors[1] = vec3(0.4863, 0.2667, 0.0627);
    colors[2] = vec3(0.0941, 0.0902, 0.0902);
    colors[3] = vec3(0.02);
    
    float hscaled = clamp((height-255)/1400, 0., 1.); //btw 0. && 1.
    if (hscaled <= 0.04)
        return mix(colors[0], colors[1], smoothstep(0.0, 1.0, exp((hscaled/0.04)-0.9)*0.8));
    else if (hscaled > 0.04 && hscaled < 0.11) {
        float f =  smoothstep(0.25, 1.0, exp(((hscaled-0.04)/(0.11-0.04) - 0.9)*1.1));
        return mix(colors[1], colors[2], f);
    }        
    else
        return mix(colors[2], colors[3],  smoothstep(0.55, 1.0, exp(((hscaled-0.11)/(1.0-0.11) -2.)*1.1)));
    
}

void main() {
    vec3 p = IN.position;
    vec3 temp_v = w_camera_position - p;
    vec3 v = normalize(temp_v); // view dir
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
    vec3 specular = spec * light_col;


    out_color.rgb = specular*0.01 + (ambient*0.5 + diffuse) * albedo_from_height(p.y);
    out_color = vec4(pow(out_color.rgb, vec3(1.0/2.2)), 1); // gamma correction
}
    
