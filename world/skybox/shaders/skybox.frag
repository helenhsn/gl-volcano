#version 330 core

in vec3 tex_coords;

uniform samplerCube cubemap;


out vec4 out_color;
void main() {
    out_color = texture(cubemap, tex_coords);

    //out_color = vec4(1.);
}