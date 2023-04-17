#version 330 core

in vec3 tex_coords;

uniform samplerCube cubemap;
uniform vec3 w_camera_position;

const float lower_bound = 0.0;
const float upper_bound = 10.0;
out vec4 out_color;
void main() {
    vec3  fog_color  = vec3(0.4706, 0.5961, 0.6549);
    float factor = (tex_coords.y - lower_bound)/(upper_bound - lower_bound);
    factor = clamp(factor, 0.0, 1.0);
    out_color = vec4(mix(fog_color,texture(cubemap, tex_coords).rgb, factor), 1.0);
}