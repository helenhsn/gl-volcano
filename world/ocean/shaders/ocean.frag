#version 330 core

in VS_OUTPUT {
    vec3 position;
    vec2 uv;
    vec3 normal;
} IN;

#define PI 3.14159265359

// simulation related uniforms
uniform sampler2D gradients;
uniform samplerCube skybox;
uniform vec3 w_camera_position;
uniform vec3 light_pos;


const vec3 deep_blue=vec3(0.0039, 0.0353, 0.1725);
const vec3 light_blue = vec3(0.0706, 0.1216, 0.1922);

uniform vec2 wind_dir;
uniform float t;
// output fragment color for OpenGL
out vec4 out_color;

// ----------------------------------------------------------------------------
float fresnel(vec3 n, vec3 l){
    float F0=.020018673;// water surface's response at normal incidence
    return F0+(1.-F0)*pow(clamp(1.-max(dot(l, n), 0.), 0., 1.), 5);
    
}

// ----------------------------------------------------------------------------


vec3 get_normal(vec3 slope){
    vec3 up = vec3(0., 1., 0.);
    vec3 n = (up - slope)/sqrt(1+slope*slope);
    return normalize(slope);
}



// ----------------------------------------------------------------------------
void main()
{
    vec4 grad = texture(gradients, IN.uv);
    vec3 water_color = mix(deep_blue, light_blue, smoothstep(40.0, 300.0, IN.position.y));

    vec3 n = get_normal(IN.normal);

    vec3 non_normalized_v = w_camera_position - IN.position;
    vec3 v = normalize(non_normalized_v); // view dir
    vec3 l = normalize(light_pos - IN.position); // light dir
    vec3 h=normalize(l+v);

    // lighting
    float F=fresnel(n, l);

    float spec = pow(max(dot(n, h), 0.0), 128);
    vec3 specular = spec * vec3(1.);

    float turbulence = max(1.3 - grad.w, 0.0);
	float color_mod = smoothstep(-5.0, 20.0, turbulence);

    // reflection
    vec3 reflc = reflect(-v, n);
    vec3 reflected_color = texture(skybox, reflc).rgb; //* vec3(0.302, 0.302, 0.302);

    // refraction -> not really necessary as we don't have a ground underwater
    // float descartes = 1.0/1.33;
    // vec3 refr = refract(-v, n, descartes);
    // vec3 refracted_color = texture(skybox, refr).rgb;

	water_color = mix(water_color,  reflected_color * color_mod, smoothstep(-200.0, 200.0, F));
    
    // reflection
    vec3 color = water_color + spec*0.1;

    out_color=vec4(color, 1.);

    out_color.rgb = pow(out_color.rgb, vec3(1.0/2.2)); // gamma correction
}