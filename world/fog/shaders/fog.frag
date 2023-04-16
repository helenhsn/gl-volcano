#version 330 core
in VS_OUTPUT {
    vec2 uv;
} IN;

uniform sampler2D color_text;
uniform sampler2D depth_text;

const float near = 0.1; 
const float far  = 15000.0; 
  
float linearize_depth(float depth) {
    float z = depth * 2.0 - 1.0; // back to NDC 
    return (2.0 * near * far) / (far + near - z * (far - near));	
}

out vec4 out_color;
void main() {
    float depth = linearize_depth(texture(depth_text, IN.uv).r); 
    out_color = texture(color_text, IN.uv);
}