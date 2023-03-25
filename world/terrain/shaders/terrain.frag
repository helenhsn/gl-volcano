#version 330 core

in VS_OUTPUT {
    vec3 position;
    vec2 uv;
    vec3 normal;
} IN;

const vec3 light_pos = vec3(-10000.0, 10000.0, -10000.0);
const vec3 light_col = vec3(1.);
const vec3 ambient_light = vec3(0.7255, 0.9216, 0.9804);

uniform vec3 w_camera_position;

vec3 albedo_from_height(float height)
{


    vec3 colors[4];

    colors[0] = vec3(0.0, 0.0, 0.0);
    colors[1] = vec3(0.0784, 0.4314, 0.0314);
    colors[2] = vec3(0.0784, 0.0941, 0.0784);
    colors[3] = vec3(0.0, 0.0, 0.0);
    if(height < 0.0)
        return vec3(0.7333, 0.0549, 0.451);
    else
    {
        float hscaled = clamp((height - 200)/(1000 - 200), 0., 1.); //btw 0. && 1.
        vec3 base_color = vec3(0., 0., 1.);
        if (hscaled < 0.1)
            return mix(colors[0], colors[1], hscaled/0.1);
        if ( 0.1 < hscaled  && hscaled < 0.15)
            return mix(colors[1], colors[2], (hscaled - 0.1)/(0.15 - 0.1));
        else
            return mix(colors[2], colors[3], (hscaled-0.15)/(1. - 0.15)+0.1);
        return base_color;
    }
}


out vec4 out_color;


void main() {
    vec3 p = IN.position;
    vec3 v = normalize(w_camera_position - p); // view dir
    vec3 n = IN.normal;
    vec3 l = normalize(light_pos - p); // light dir
    vec3 h = normalize(l + v); //halfway vector

    vec3 albedo = albedo_from_height(p.y);

    // ambient light
    vec3 ambient = 0.1 * ambient_light;

    // diffuse light
    float dif = max(dot(n, l), 0.0);
    vec3 diffuse = dif * light_col;

    // specular light
    float spec = pow(max(dot(n, h), 0.0), 8);
    vec3 specular = spec * light_col;

    out_color.rgb = specular + ambient + diffuse * albedo;
    //out_color.rgb = pow(out_color.rgb, vec3(1.0/2.2)); // gamma correction
}
    
