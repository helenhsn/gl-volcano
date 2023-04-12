#version 330 core

in VS_OUTPUT {
    vec3 position;
    vec2 uv;
    vec3 normal;
    vec3 albedo;
    float fog_plane_f;
} IN;

const vec3 light_pos = vec3(5000.0, 5000.0, -5000.0);
const vec3 light_col = vec3(1.);
const vec3 ambient_light = vec3(0.2196, 0.5922, 0.7059);
uniform vec3 w_camera_position;

out vec4 out_color;


vec3 applyFog( in vec3 color,      // original color of the pixel
               in vec3 view)  // camera to point vector
{
    vec3 fog_plane_point = vec3(0., 500., 0.);
    float dist = length(view);
    float density = 0.003;
    float gradient = 2.9;

    float xz_fog = exp(-pow(dist*density, gradient));
    vec3  fog_color  = vec3(0.4549, 0.5255, 0.6);


    float fog_amount = IN.fog_plane_f * (1.-xz_fog);

    return mix(color, fog_color, fog_amount);
}


float CalcLayeredFogFactor(){
    float gFogEnd = 0.1;
    float gLayeredFogTop = 1000;

    vec3 CameraProj = w_camera_position;
    CameraProj.y = 0.0;

    vec3 PixelProj = IN.position;
    PixelProj.y = 0.0; 

    float DeltaD = clamp(length(CameraProj - PixelProj), 0.0, 1.0);

    float DeltaY = 0.0;
    float DensityIntegral = 0.0;

    if (w_camera_position.y > gLayeredFogTop){
        if (IN.position.y <  gLayeredFogTop){
            DeltaY = (gLayeredFogTop - IN.position.y);
            DensityIntegral = DeltaY * DeltaY * 0.5;
        }
    } else {
        if (IN.position.y < gLayeredFogTop){
            DeltaY = abs(w_camera_position.y - IN.position.y)/gLayeredFogTop;
            float DeltaCamera = (gLayeredFogTop - w_camera_position.y) / gLayeredFogTop;
            float DensityCamera = DeltaCamera * DeltaCamera * 0.5;
            float DeltaPixel = (gLayeredFogTop - IN.position.y) / gLayeredFogTop;
            float DensityPixel = DeltaPixel * DeltaPixel * 0.5;
            DensityIntegral = abs(DensityCamera - DensityPixel);
        } else {
            DeltaY = (gLayeredFogTop - IN.position.y) / gLayeredFogTop;
            DensityIntegral = DeltaY * DeltaY * 0.5;
        }
    }
    float fogDensity = 0.0;

    if (DeltaY != 0){
        fogDensity = (sqrt(1.0 + ((DeltaD / DeltaY) * (DeltaD / DeltaY)))) * DensityIntegral;
    }

    return exp(-fogDensity);
}





void main() {
    vec3 p = IN.position;
    vec3 temp_v = w_camera_position - p;
    vec3 v = normalize(temp_v); // view dir
    vec3 n = IN.normal;
    vec3 l = normalize(light_pos - p); // light dir
    vec3 h = normalize(l + v); //halfway vector

    // ambient light
    vec3 ambient = 0.1 * ambient_light;

    // diffuse light
    float dif = max(dot(n, l), 0.0);
    vec3 diffuse = dif * light_col;

    // specular light
    float spec = pow(max(dot(n, h), 0.0), 32);
    vec3 specular = spec * light_col;


    out_color.rgb = specular*0.1 + (ambient*0.5 + diffuse) * IN.albedo;
    out_color.rgb = applyFog(out_color.rgb, temp_v);
    out_color = vec4(pow(out_color.rgb, vec3(1.0/2.2)), 1); // gamma correction
}
    
