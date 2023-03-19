#version 330 core

in VS_OUTPUT {
    vec3 position;
    vec2 uv;
    vec3 normal;
} IN;

#define PI 3.14159265359


// uniforms
uniform int N;
uniform int L;

// simulation related uniforms
uniform sampler2D displacement;
uniform sampler2D gradients;
uniform sampler2D foam_text;
uniform float wind_speed;
uniform vec2 wind_direction;
uniform vec3 w_camera_position;

const vec3 light_pos = vec3(0.0, 1000.0, -100.0);
const vec3 ambient_light = vec3(0.7255, 0.9216, 0.9804);
const vec3 light_col=vec3(1.);
const vec3 deep_blue=vec3(0.0157, 0.2049, 0.4384);
const vec3 light_blue = vec3(0.0549, 0.5412, 0.8667);
// output fragment color for OpenGL
out vec4 out_color;


// ----------------------------------------------------------------------------
float fresnel(vec3 l, vec3 n){
    float F0=.020018673;// water surface's response at normal incidence
    return F0+(1.-F0)*pow(clamp(1.-max(dot(l, n), 0.), 0., 1.), 5);
    
}

// ----------------------------------------------------------------------------

float height(vec2 pos){
    return texture(displacement,pos).g;
}

vec3 get_normal(vec3 slope){
    vec3 up = vec3(0., 1., 0.);
    vec3 n = (up - slope)/sqrt(1+slope*slope);
    return normalize(n);
}

// ----------------------------------------------------------------------------

vec2 get_displacement(vec2 pos){
    return texture(displacement, pos.xy).xz;
}



// ----------------------------------------------------------------------------
void main()
{
    vec4 grad = texture(gradients, IN.uv);
    
    vec3 n=normalize(grad.xzy);// normalized normal vector

    //vec3 n = vec3(0., 1., 0.);
    vec3 v = normalize(w_camera_position - IN.position); // view dir
    vec3 l = normalize(light_pos - IN.position); // light dir
    vec3 h=normalize(l+v);
    
    float F=fresnel(n, v);

    
    vec3 ambient= ambient_light;
    vec3 diffuse = max(dot(l, n), 0.) * light_col;
    vec3 fresnel = F * light_col;

    // light from the sun (Ward anisotropic model)
    const float rho_s   = 0.3;
    const float ax    = 0.25;
    const float ay    = 0.1;

    // anisotropic directions
    vec3 x = cross(l, n);
    vec3 y = cross(x, n);

    float factor = (1./(4*PI) * rho_s / (ax * ay * sqrt(max(1e-5, dot(l, n) * dot(v, n)))));
    float hdotx = dot(h, x) / ax;
    float hdoty = dot(h, y) / ay;
    float hdotn = dot(h, n);
    float specular =  factor * exp(-2.0 * ((hdotx * hdotx) + (hdoty * hdoty)) / (1+hdotn * hdotn));;
    vec3 spec = specular * light_col;


    float range = 25.0;
    vec3 water_color = mix(deep_blue, light_blue, smoothstep(-range, range, IN.position.y));
    //float foam = texture(foam_text, IN.uv*5. + wind_direction*vec2(wind_speed/(N*2.))).r*10.0;
    //water_color = mix(water_color, vec3(1.0, 1.0, 1.0), smoothstep(0.8, 1.0, foam)*smoothstep(0.6, 0.3, grad.w));

    vec3 color = (ambient*0.3 + diffuse*0.5)*water_color + fresnel*0.1+ spec*0.8;


    // float noise = perlin(vec3(IN.UV*300., 0.))*.28+.72;
    // float tweak = smoothstep(1.05, 1.09, J*noise);
    
    out_color=vec4(color, 1.);


    
}