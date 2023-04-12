#version 330 core

in vec3 tex_coords;

uniform samplerCube cubemap;
uniform vec3 w_camera_position;

out vec4 out_color;
void main() {
    out_color = texture(cubemap, tex_coords);
}