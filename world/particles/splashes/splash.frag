#version 330 core

in GS_OUTPUT {
    float lifetime;
    vec2 uv;
    vec3 pos;
} IN;

uniform float t;
uniform vec3 emitter_color;

uniform sampler2D sprites;


out vec4 out_color;

void main() {

    out_color = mix(vec4(1., 0., 0., 1.), vec4(1.0, 0.9843, 0.0, 1.0), IN.lifetime);

}