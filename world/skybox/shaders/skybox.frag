#version 330 core

in vec3 tex_coords;

uniform samplerCube cubemap;
uniform vec3 w_camera_position;

const float lower_bound = 0.0;
const float upper_bound = 30.0;
out vec4 out_color;
void main() {
    out_color = texture(cubemap, tex_coords) * vec4(vec3(0.302, 0.302, 0.302), 1.);
}