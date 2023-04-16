#version 330 core
in vec2 frag_tex_coords;

in VS_OUTPUT {
    vec3 position;
} IN;

uniform sampler2D diffuse_map;
out vec4 out_color;

uniform vec3 w_camera_position;



void main() {
    vec3 p = IN.position;
    vec3 temp_v = w_camera_position - p;
    
    // animal texture
    out_color = vec4(texture(diffuse_map, vec2(frag_tex_coords)).rgb, 1.0);    
    out_color = vec4(pow(out_color.rgb, vec3(1.0/2.2)), 1); // gamma correction
}
