#version 330 core

in VS_OUTPUT {
    vec3 position;
    vec2 uv;
    vec3 normal;
    vec3 col;
} IN;

#define PI 3.14159265359
#define BLEND_START  8    // m
#define BLEND_END    10000  // m
// simulation related uniforms
uniform sampler2D gradients;
uniform samplerCube skybox;
uniform vec3 w_camera_position;

const vec3 light_pos = vec3(5000.0, 5000.0, -5000.0);
const vec3 ambient_light = vec3(0.7333, 0.8549, 0.8941);
const vec3 light_col=vec3(1.);
const vec3 deep_blue=vec3(0.0039, 0.0353, 0.1725);
const vec3 light_blue = vec3(0.098, 0.1647, 0.2667);

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
    return normalize(n);
}


// ----------------------------------------------------------------------------
void main()
{
    vec4 grad = texture(gradients, IN.uv);
    vec3 water_color = mix(deep_blue, light_blue, smoothstep(40.0, 300.0, IN.position.y));

    vec3 n = normalize(IN.normal);

    vec3 non_normalized_v = w_camera_position - IN.position;
    vec3 v = normalize(non_normalized_v); // view dir
    vec3 l = reflect(-v, n); // light dir
    vec3 h=normalize(l+v);




    // lighting
    float F=fresnel(n, l);

    
    vec3 ambient= ambient_light;
    vec3 diffuse = max(dot(l, n), 0.) * light_col;
    vec3 fresnel = F * ambient_light;

    // light from the sun (Ward anisotropic model)
    const float rho_s   = 0.01;
    const float ax    = 0.55;
    const float ay    = 0.9;

    // anisotropic directions
    vec3 x = cross(l, n);
    vec3 y = cross(x, n);

    float factor = (1./(4*PI) * rho_s / (ax * ay * sqrt(max(1e-5, dot(l, n) * dot(v, n)))));
    float hdotx = dot(h, x) / ax;
    float hdoty = dot(h, y) / ay;
    float hdotn = dot(h, n);
    float specular =  factor * exp(-2.0 * ((hdotx * hdotx) + (hdoty * hdoty)) / (1+hdotn * hdotn));
    vec3 spec = specular * light_col;

    float turbulence = max(0.1 - grad.w, 0.0);
	float color_mod = smoothstep(-8.0, 20.0, turbulence);

    // reflection
    vec3 reflc = reflect(-v, n);
    vec3 reflected_color = texture(skybox, reflc).rgb;

    // refraction -> not really necessary as we don't have a ground underwater
    // float descartes = 1.0/1.33;
    // vec3 refr = refract(-v, n, descartes);
    // vec3 refracted_color = texture(skybox, refr).rgb;

	water_color = mix(water_color,  reflected_color * color_mod, smoothstep(-500.0, 500.0, F*0.1));
    
    // reflection
    vec3 color = water_color + spec;

    out_color=vec4(color, 1.);
    out_color.rgb = pow(out_color.rgb, vec3(1.0/2.2)); // gamma correction
}