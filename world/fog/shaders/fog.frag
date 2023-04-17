#version 330 core
in VS_OUTPUT {
    vec2 uv;
} IN;

uniform sampler2D color_text;
uniform sampler2D depth_text;
uniform vec3 w_camera_position;
uniform mat4 view;
uniform mat4 proj;
uniform int is_fog;


const float near = 0.1; 
const float far  = 15000.0; 
  
float linearize_depth(float depth) {
    float z = depth * 2.0 - 1.0; // back to NDC 
    return (2.0 * near * far) / (far + near - z * (far - near));	
}

vec3 depth_to_worldpos(float depth) {
    float z = depth * 2.0 - 1.0; // back to NDC as depth is btw 0.0 and 1.0
    vec4 clip_space_pos = vec4(IN.uv*2.0 -1.0, z, 1.0);
    vec4 view_space_pos = inverse(proj) * clip_space_pos;

    view_space_pos /= view_space_pos.w; // perspective division

    vec4 world_pos = inverse(view) * view_space_pos;
    return world_pos.xyz;
}

float fog_from_height(vec3 pos, float linear_depth) {
    float factor = 0.02;
    float boundary = 760.0;
    if (linear_depth > 15000.0) {
        boundary = 3000.0;
        factor = 0.001;
    }
    return 1. - smoothstep(0,0.5, exp((pos.y-boundary)*factor));
}


vec3 apply_fog( in vec3 color, in float dist) {

    vec3 fog_plane_point = vec3(0., 500., 0.);
    float density = 0.002;
    float close_to_volcano = length(w_camera_position.xz)-1800.0;
    float gradient = 3.9;
    if (close_to_volcano < 0.0) // we don't want the fog to appear close to the volcano
        density = 0.002 - (1.0 - smoothstep(0.0, 5.0, exp((length(w_camera_position) - 1425)*0.002)))*0.0015;
        //gradient = 3.9 + (1.0 - smoothstep(0.0, 5.0, exp((length(w_camera_position) - 1425)*0.002)))*1.5;
    float linear_depth = linearize_depth(dist);
    float xz_fog = exp(-pow(linear_depth*density, gradient));
    vec3  fog_color  = vec3(0.4549, 0.5255, 0.6);

    // getting world pos from depth value to apply layer fog instead of uniform fog
    vec3 world_pos = depth_to_worldpos(dist);

    float fog_y = fog_from_height(world_pos, linear_depth);
    xz_fog = 1.-xz_fog;

    return mix(color, fog_color, fog_y*xz_fog);
}

out vec4 out_color;
void main() {
    float depth = texture(depth_text, IN.uv).r; 
    vec4 scene_color = texture(color_text, IN.uv);
    if (is_fog==1)
        scene_color.rgb = apply_fog(scene_color.rgb, depth);
    out_color = scene_color;
}