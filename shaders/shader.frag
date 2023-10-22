#version 330 core

// Variable de sortie (sera utilisé comme couleur)
out vec4 color;

in vec3 coordonnee_3d;
in vec3 coordonnee_3d_locale;
in vec3 vnormale;
in vec4 vcolor;
in vec2 vtex;

uniform sampler2D tex;

vec3 light=vec3(0.5,0.5,5.0);

void main (void)
{
  //vecteurs pour le calcul d'illumination
  vec3 n = normalize(vnormale);
  vec3 d = normalize(light-coordonnee_3d_locale);
  vec3 r = reflect(d,n);
  vec3 o = normalize(-coordonnee_3d_locale);

  //calcul d'illumination
  float diffuse  = 0.7*clamp(dot(n,d),0.0,1.0);
  float specular = 0.2*pow(clamp(dot(r,o),0.0,1.0),128.0);
  float ambiant  = 0.2;

  vec4 white = vec4(1.0,1.0,1.0,0.0);

  //recuperation de la texture
  vec4 color_texture = texture(tex, vtex);
  vec4 color_final   = vcolor*color_texture;

  //couleur finale
  color = (ambiant+diffuse)*color_final+specular*white;
}