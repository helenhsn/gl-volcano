#version 330 core

// receiving interpolated position and normal for fragment shader
in VS_OUTPUT {
    vec3 position;
    vec3 normal;
    float fog_plane_f;
} IN;

const vec3 light_pos = vec3(5000.0, 5000.0, -5000.0);
const vec3 light_col = vec3(1.);
const vec3 ambient_light = vec3(0.2196, 0.5922, 0.7059);

uniform vec3 w_camera_position;

// output fragment color for OpenGL
out vec4 out_color;

vec3 applyFog( in vec3 color,      // original color of the pixel
               in vec3 view)  // camera to point vector
{
    vec3 fog_plane_point = vec3(0., 500., 0.);
    float dist = length(view);
    float density = 0.003;
    float gradient = 2.9;

    float f = smoothstep(0.0, 900.0, view.y);
    float xz_fog = exp(-pow(dist*density, gradient));
    vec3  fog_color  = vec3(0.5,0.6,0.7);


    float fog_amount = IN.fog_plane_f * (1.-xz_fog);

    return mix(color, fog_color, fog_amount);
}


void main() {
    vec3 p = IN.position;
    vec3 temp_v = w_camera_position - p;
    vec3 v = normalize(temp_v); // view dir
    vec3 n = normalize(IN.normal);
    vec3 l = normalize(light_pos - p); // light dir
    vec3 h = normalize(l + v); //halfway vector

    // color
    vec3 turbine_color = vec3(0.92, 0.98, 0.96);

    // ambient light
    vec3 ambient = 0.1 * ambient_light;

    // diffuse light
    float dif = max(dot(n, l), 0.0);
    vec3 diffuse = dif * light_col;

    // specular light
    float spec = pow(max(dot(n, h), 0.0), 32);
    vec3 specular = spec * light_col;

    out_color.rgb = specular*0.8 + (ambient*0.5 + diffuse*0.8) * turbine_color;
    out_color.rgb = applyFog(out_color.rgb, temp_v);
    out_color = vec4(pow(out_color.rgb, vec3(1.0/2.2)), 1); // gamma correction
}
