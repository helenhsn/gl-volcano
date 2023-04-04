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

    vec2 uv_scaled = IN.uv/8.0; // 64 sprites so we need to divide our uv coordinates by 8
    float f = floor(8.0*IN.lifetime)/8.0;
    vec2 offset = vec2(f, 0.875 - f); // when lifetime = 0.0 we're at the bottom right of sprites text
    out_color = texture2D(sprites, uv_scaled + offset);
    out_color.rgb = mix(out_color.rgb * vec3(1.0, 0.0, 0.0), vec3(1.0, 0.6, 0.0), clamp(IN.lifetime, 0.0, 0.8));
    out_color.rgb = mix(vec3(0.0, 0.0, 0.0), out_color.rgb, IN.lifetime);
    out_color.a *=0.18;

}