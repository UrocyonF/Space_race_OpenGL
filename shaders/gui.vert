#version 330 core

layout (location = 0) in vec3 position;

out vec2 vtex;

uniform vec2 size;
uniform vec2 start;

void main (void)
{
  //coordonnees de textures
  vtex=position.xy;
  vtex.y = 1.0f-vtex.y;

  //position dans l'espace ecran
  vec2 p = position.xy * size + start;

  gl_Position = vec4(p, 0., 1.);
}