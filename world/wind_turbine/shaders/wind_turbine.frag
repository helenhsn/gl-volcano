#version 330 core

// receiving interpolated position and normal for fragment shader
in VS_OUTPUT {
    vec3 position;
    vec3 normal;
} IN;

const vec3 light_col = vec3(1.);
const vec3 ambient_light = vec3(0.2196, 0.5922, 0.7059);

uniform vec3 w_camera_position;
uniform vec3 light_pos;

// output fragment color for OpenGL
out vec4 out_color;


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
    out_color = vec4(pow(out_color.rgb, vec3(1.0/2.2)), 1); // gamma correction
}
