# version 330 core
in VS_OUTPUT {
    vec2 uv;
} IN;

uniform sampler2D diffuse_map;

out vec4 color;
void main() {
    color = vec4(texture(diffuse_map, IN.uv).rgb, 1.);
}
