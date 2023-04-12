#version 330 core
in vec2 frag_tex_coords;

in VS_OUTPUT {
    vec3 position;
    float fog_plane_f;
} IN;

uniform sampler2D diffuse_map;
out vec4 out_color;

uniform vec3 w_camera_position;

vec3 applyFog( in vec3 color,      // original color of the pixel
               in vec3 view)  // camera to point vector
{
    vec3 fog_plane_point = vec3(0., 500., 0.);
    float dist = length(view);
    float density = 0.003;
    float gradient = 2.9;

    float f = smoothstep(0.0, 900.0, view.y);
    float xz_fog = exp(-pow(dist*density, gradient));
    vec3  fog_color  = vec3(0.5,0.6,0.7);


    float fog_amount = IN.fog_plane_f * (1.-xz_fog);

    return mix(color, fog_color, fog_amount);
}


void main() {
    vec3 p = IN.position;
    vec3 temp_v = w_camera_position - p;
    
    // animal texture
    out_color = vec4(texture(diffuse_map, vec2(frag_tex_coords)).rgb, 1.0);    

    out_color.rgb = applyFog(out_color.rgb, temp_v);
    out_color = vec4(pow(out_color.rgb, vec3(1.0/2.2)), 1); // gamma correction
}
