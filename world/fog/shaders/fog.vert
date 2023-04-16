#version 330 core
in vec2 position;

out VS_OUTPUT {
    vec2 uv;
} OUTPUT;
void main() {
    OUTPUT.uv = position*0.5+0.5;
    gl_Position = vec4(position.x, position.y, 0.0, 1.0);
}