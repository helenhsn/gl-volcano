#version 330 core

// receiving interpolated color and normal for fragment shader
in vec3 position;
in vec3 fragment_color;
in vec3 out_normal;

const vec3 light_pos = vec3(-5000.0, 5000.0, -5000.0);
const vec3 light_col = vec3(1.);
const vec3 ambient_light = vec3(0.2196, 0.5922, 0.7059);
const vec3 tree_color = vec3(0.60, 0.40, 0.17);

uniform vec3 w_camera_position;


// output fragment color for OpenGL
out vec4 out_color;

void main() {
    vec3 p = position;
    vec3 v = normalize(w_camera_position - p); // view dir
    vec3 n = out_normal;
    vec3 l = normalize(light_pos - p); // light dir
   // vec3 h = normalize(l + v); //halfway vector

    vec3 albedo = tree_color;

    // ambient light
    vec3 ambient = 0.1 * ambient_light;

    // diffuse light
    float dif = max(dot(n, l), 0.0);
    vec3 diffuse = dif * light_col;

    out_color.rgb = n;
    out_color.rgb = (ambient*0.5 + diffuse) * albedo;
    //out_color = vec4(pow(out_color.rgb, vec3(1.0/2.2)), 1); // gamma correction
    //out_color = vec4(out_normal,1);
}
