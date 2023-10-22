from cpe3d import Object3D, Camera, Transformation3D, Text
from glutils import create_program_from_file, load_texture
from random import seed, random, choice, uniform
from viewerGL import ViewerGL
from mesh import Mesh
import OpenGL.GL as GL
import numpy as np
import pyrr


def main():
    # creating the viewer
    viewer = ViewerGL(nb_asteroid, nb_ring)

    # camera placement
    viewer.set_camera(Camera())

    # creating shader programs
    program3d_id = create_program_from_file('./shaders/shader.vert', './shaders/shader.frag')
    programSkybox_id = create_program_from_file('./shaders/shader.vert', './shaders/skybox.frag')
    programGUI_id = create_program_from_file('./shaders/gui.vert', './shaders/gui.frag')


    # function allowing you to create a 3D object from an .obj file and a texture
    def create_object(obj_path, texture_path):
        m = Mesh.load_obj(obj_path)
        m.normalize()
        m.apply_matrix(pyrr.matrix44.create_from_scale([1, 1, 1, 1]))
        tr = Transformation3D()
        texture = load_texture(texture_path)
        o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), program3d_id, texture, tr)
        viewer.add_object(o, 'objs')

    # function allowing you to create several 3D objects from an .obj file, a texture, a scale and a number of objects
    def creat_multi_object(obj_path, texture_path, scale, nb_obj):
        m = Mesh.load_obj(obj_path)
        m.normalize()
        m.apply_matrix(pyrr.matrix44.create_from_scale(scale))
        vao = m.load_to_gpu()
        texture = load_texture(texture_path)
        for _ in range(nb_obj):
            ti = Transformation3D()
            for i in range(3): ti.translation[i] = choice([-1, 1])*uniform(0.5, 20)
            ti.quaternion = pyrr.quaternion.create(random(), random(), random(), random())
            o = Object3D(vao, m.get_nb_triangles(), program3d_id, texture, ti)
            viewer.add_object(o, 'objs')

    # function allowing you to create several images from a list of textures, start and end coordinates
    def creat_multi_image(texture_path_list, p0_list, p1_list, p2_list, p3_list):
        m = Mesh()
        n, c = [0, 1, 0], [1, 1, 1]
        t0, t1, t2, t3 = [0, 0], [1, 0], [1, 1], [0, 1]
        m.faces = np.array([[0, 1, 2], [0, 2, 3]], np.uint32)
        for i in range(len(texture_path_list)):
            m.vertices = np.array([[p0_list[i] + n + c + t0], [p1_list[i] + n + c + t1], [p2_list[i] + n + c + t2], [p3_list[i] + n + c + t3]], np.float32)
            texture = load_texture(texture_path_list[i])
            o = Object3D(m.load_to_gpu(), m.get_nb_triangles(), programSkybox_id, texture, Transformation3D())
            viewer.add_object(o, 'objs')

    # function allowing you to create several texts from a list of texts, start and end coordinates
    def create_multi_text(text_tuple, x_start_list, y_start_list, x_end_list, y_end_list, screen_name):
        vao = Text.initalize_geometry()
        texture = load_texture('./assets/fontB.jpg')
        for i in range(len(text_tuple)):
            o = Text(text_tuple[i], np.array([x_start_list[i], y_start_list[i]], np.float32), np.array([x_end_list[i], y_end_list[i]], np.float32), vao, 2, programGUI_id, texture)
            viewer.add_object(o, screen_name)


    # creating the player's ship (item 0)
    create_object('./assets/spaceship/spaceship.obj', './assets/spaceship/spaceship_texture.jpg')

    # creation of the skybox (object 1 to 6)
    texture_path_list = ['./assets/skybox/corona_dn.png', './assets/skybox/corona_up.png', './assets/skybox/corona_lf.png', './assets/skybox/corona_rt.png', './assets/skybox/corona_bk.png', './assets/skybox/corona_ft.png']
    p0_list = [[-50, -50, -50], [-50, 50, 50], [50, -50, -50], [-50, -50, 50], [-50, -50, -50], [50, -50, 50]]
    p1_list = [[50, -50, -50], [50, 50, 50], [-50, -50, -50], [50, -50, 50], [-50, -50, 50], [50, -50, -50]]
    p2_list = [[50, -50, 50], [50, 50, -50], [-50, 50, -50], [50, 50, 50], [-50, 50, 50], [50, 50, -50]]
    p3_list = [[-50, -50, 50], [-50, 50, -50], [50, 50, -50], [-50, 50, 50], [-50, 50, -50], [50, 50, 50]]
    creat_multi_image(texture_path_list, p0_list, p1_list, p2_list, p3_list)

    # creation and placement of asteroids (objects 7 to 7+nb_asteroid-1)
    creat_multi_object('./assets/asteroids/asteroid.obj', './assets/asteroids/asteroid_texture.jpg', [1, 1, 1, 1], nb_asteroid)

    # creation of a drawing of the rings which will be used for the race (objects 7+nb_asteroid to 7+nb_asteroid+nb_ring-1)
    creat_multi_object('./assets/rings/ring.obj', './assets/rings/ring_texture.jpg', [2, 2, 2, 1], nb_ring)

    # creation and placement of text (objects 7+nb_asteroid+nb_ring to 7+nb_asteroid+nb_ring+2)
    text_tuple = ('vie restante: 3', 'anneaux: 0/10', '00:00')
    x_start_list, y_start_list = [-1, -1, -0.1], [0.9, 0.78, 0.9]
    x_end_list, y_end_list = [-0.4, -0.4, 0.1], [1, 0.88, 1]
    create_multi_text(text_tuple, x_start_list, y_start_list, x_end_list, y_end_list, 'objs')

    # creation and placement of the text to display the speed (object 7+nb_asteroid+nb_ring+3 to 7+nb_asteroid+nb_ring+9)
    text_tuple = ('-', '-', '-', '-', '-', '-')
    x_start_list, y_start_list = [0.6 for _ in range(6)], [-0.8, -0.72, -0.64, -0.56, -0.48, -0.4]
    x_end_list, y_end_list = [1.1 for _ in range(6)], [-0.4, -0.32, -0.24, -0.16, -0.08, 0]
    create_multi_text(text_tuple, x_start_list, y_start_list, x_end_list, y_end_list, 'objs')

    # creating the game launch menu
    text_tuple = ('Jouer', 'Quitter')
    x_start_list, y_start_list = [-0.2, -0.3], [0.05, -0.15]
    x_end_list, y_end_list = [0.2, 0.3], [0.15, -0.05]
    create_multi_text(text_tuple, x_start_list, y_start_list, x_end_list, y_end_list, 'objs_start_menu')

    # creating the end game menu
    text_tuple = ('Vous avez perdu !', 'Votre temps: 00:00', 'Rejouer', 'Quitter')
    x_start_list, y_start_list = [-0.45, -0.5, -0.25, -0.3], [0.35, 0.15, -0.05, -0.25]
    x_end_list, y_end_list = [0.45, 0.5, 0.25, 0.3], [0.45, 0.25, 0.05, -0.15]
    create_multi_text(text_tuple, x_start_list, y_start_list, x_end_list, y_end_list, 'objs_end_menu')


    # run the viewer
    viewer.run()


if __name__ == '__main__':
    # initialization of constants
    seed(2)                 # seed for random generation (to always have the same generation if desired)
    nb_asteroid = 30        # number of asteroids
    nb_ring = 10            # number of rings

    # launch of the game
    main()
