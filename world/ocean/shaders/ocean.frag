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
uniform vec3 w_camera_position;

const vec3 light_pos = vec3(-5000.0, 5000.0, -5000.0);
const vec3 ambient_light = vec3(0.2196, 0.5922, 0.7059);
const vec3 light_col=vec3(1.);
const vec3 deep_blue=vec3(0.0196, 0.0745, 0.1412);
const vec3 light_blue = vec3(0.0, 0.1686, 0.4078);

uniform vec2 wind_dir;
uniform float t;
// output fragment color for OpenGL
out vec4 out_color;

const vec3 perlinFrequency = vec3(0.001, 0.005, 0.002);
const vec3 perlinAmplitude = vec3(2.65, 2.90, 2.77);

// ----------------------------------------------------------------------------
float fresnel(vec3 l, vec3 n){
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
    float range = 5.0;
    vec3 water_color = mix(deep_blue, light_blue, smoothstep(-range, range, IN.position.y));

    vec3 n = normalize(IN.normal);
    vec3 temp_v = w_camera_position - IN.position;
    // tiling effect removal

    vec3 v = normalize(temp_v); // view dir
    vec3 l = normalize(light_pos - IN.position); // light dir
    vec3 h=normalize(l+v);



    // lighting
    float F=fresnel(n, v);

    
    vec3 ambient= ambient_light;
    vec3 diffuse = max(dot(l, n), 0.) * light_col;
    vec3 fresnel = F * ambient_light;

    // light from the sun (Ward anisotropic model)
    const float rho_s   = 0.2;
    const float ax    = 0.15;
    const float ay    = 0.1;

    // anisotropic directions
    vec3 x = cross(l, n);
    vec3 y = cross(x, n);

    float factor = (1./(4*PI) * rho_s / (ax * ay * sqrt(max(1e-5, dot(l, n) * dot(v, n)))));
    float hdotx = dot(h, x) / ax;
    float hdoty = dot(h, y) / ay;
    float hdotn = dot(h, n);
    float specular =  factor * exp(-2.0 * ((hdotx * hdotx) + (hdoty * hdoty)) / (1+hdotn * hdotn));
    vec3 spec = specular * light_col;

    //water_color = mix(water_color, vec3(1.0, 1.0, 1.0), smoothstep(0.8, 1.0, foam)*smoothstep(0.6, 0.3, grad.w));
        
    if (specular > 10.)
        spec *= 0.02;
    float turbulence = max(1.8 - grad.w, 0.0);
	float color_mod = smoothstep(0.2, 12.95, turbulence);

    float f = clamp((BLEND_END - length(temp_v))/(BLEND_END - BLEND_START), 0., 1.);
	water_color = mix(water_color, vec3(color_mod), smoothstep(-20., 10., f));
    vec3 color = (ambient*0.3 + diffuse*0.5)*water_color + fresnel*0.2+ spec*0.3;

    // float noise = perlin(vec3(IN.UV*300., 0.))*.28+.72;
    // float tweak = smoothstep(1.05, 1.09, J*noise);
    

    
    out_color=vec4(pow(color, vec3(1/2.2)), 1.);


    
}