#version 330 core
in vec3 position;

uniform mat4 view;
uniform mat4 proj;

out vec3 tex_coords; // vec3 because we're sampling a 3D texture (cubemap texture)

void main() {
    // model matrix isn't used here as we don't rotate/translate/scale the skybox
    // view is clamped to 3x3 matrix as we disable translation
    vec4 pos = proj * mat4(mat3(view)) * vec4(position, 1.0);
    tex_coords = position;
    gl_Position = pos.xyww;
}