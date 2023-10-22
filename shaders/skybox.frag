#version 330 core

// Variable de sortie (sera utilisé comme couleur)
out vec4 color;

in vec4 vcolor;
in vec2 vtex;

uniform sampler2D tex;

void main (void)
{
  //recuperation de la texture
  vec4 color_texture = texture(tex, vtex);
  vec4 color_final   = vcolor*color_texture;

  //couleur finale
  color = color_final;
}