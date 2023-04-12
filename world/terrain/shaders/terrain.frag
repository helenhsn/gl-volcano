#version 330 core

in VS_OUTPUT {
    vec3 position;
    vec2 uv;
    vec3 normal;
    vec3 albedo;
} IN;

const vec3 light_pos = vec3(5000.0, 5000.0, -5000.0);
const vec3 light_col = vec3(1.);
const vec3 ambient_light = vec3(0.2196, 0.5922, 0.7059);

uniform vec3 w_camera_position;

out vec4 out_color;



vec4 applyFog( in vec4  color,      // original color of the pixel
               in float dist, // camera to point distance
               in vec3  rayOri,   // camera position
               in vec3  rayDir )  // camera to point vector
{
    float b = 0.02;
    float a = 10e5;
    float fog_maxdist = 3000;
    float fog_mindist = 1000;
    vec4  fog_colour = vec4(0.4, 0.4, 0.4, 1.0);
    float height = 1000;
    float dist_height = height - rayDir.y;

    // Calculate fog
    // float dist = length(rayOri.xyz);
    float fog_factor = (fog_maxdist - dist) / (fog_maxdist - fog_mindist) ;
    fog_factor = clamp(fog_factor, 0.0, 1.0);

    vec4 color_new = mix(fog_colour, color, fog_factor);
    fog_factor = clamp(fog_factor, 0.0, 0.5);
    //color_new.y = color.y;
    return color_new;
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
    out_color = applyFog(out_color, length(temp_v), w_camera_position, temp_v);
    vec4  fog_colour = vec4(0.4, 0.4, 0.4, 1.0);
    //out_color = mix(fog_colour, out_color, CalcLayeredFogFactor());
    
    out_color = vec4(pow(out_color.rgb, vec3(1.0/2.2)), 1); // gamma correction
}
    
