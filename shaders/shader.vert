#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normale;
layout (location = 2) in vec3 color;
layout (location = 3) in vec2 tex;

uniform mat4 rotation_model;
uniform vec4 rotation_center_model;
uniform vec4 translation_model;

uniform mat4 rotation_view;
uniform vec4 rotation_center_view;
uniform vec4 translation_view;

uniform mat4 projection;

out vec3 coordonnee_3d;
out vec3 coordonnee_3d_locale;
out vec3 vnormale;
out vec4 vcolor;
out vec2 vtex;

//Un Vertex Shader minimaliste
void main (void)
{
  //Les coordonnees 3D du sommet
  coordonnee_3d = position;

  //application de la deformation du model
  vec4 p_model = rotation_model*(vec4(position, 1.0)-rotation_center_model)+rotation_center_model+translation_model;

  //application de la deformation de la vue
  vec4 p_modelview = rotation_view*(p_model-rotation_center_view)+rotation_center_view+translation_view;

  coordonnee_3d_locale = p_modelview.xyz;

  //Projection du sommet
  vec4 p_proj = projection*p_modelview;

  //Gestion des normales
  vec4 n = rotation_view*rotation_model*vec4(normale,1.0);
  vnormale=n.xyz;

  //Couleur du sommet
  vcolor=vec4(color,1.0);

  //position dans l'espace ecran
  gl_Position = p_proj;

  //coordonnees de textures
  vtex=tex;
}