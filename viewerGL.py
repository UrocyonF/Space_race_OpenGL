#!/usr/bin/env python3

from cpe3d import Object3D
from time import time
import OpenGL.GL as GL
import numpy as np
import glfw
import pyrr


class ViewerGL:
    def __init__(self, nb_asteroid, nb_ring):
        # initialization of the GLFW library
        glfw.init()

        # initializing window settings
        self.width = 800
        self.height = 800

        # OpenGL context setting
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        # creation and configuration of the window
        glfw.window_hint(glfw.RESIZABLE, False)
        self.window = glfw.create_window(self.width, self.height, 'OpenGL', None, None)

        # configuration of the event management function
        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)
    
        # enabling OpenGL context for window
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)

        # enabling depth management
        GL.glEnable(GL.GL_DEPTH_TEST)

        # choice of background color
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        print(f"OpenGL: {GL.glGetString(GL.GL_VERSION).decode('ascii')}")

        # initialization of variables
        self.screen = 0                         # screen number (0: start menu, 1: game, 2: end menu)

        self.objs = []                          # list of objects to display
        self.objs_start_menu = []               # list of start menu objects
        self.objs_end_menu = []                 # list of end menu objects
        self.touch = {}                         # dictionary containing pressed keys

        self.speed = 0.0                        # speed of the player's ship (initialized to 0)

        self.score = 0                          # player score (initialized at 0 and corresponds to the number of rings crossed)
        self.vie = 3                            # number of player lives (initialized at 3)

        self.start_time = 0                     # player departure time (initialized to 0)
        self.count_started = False              # boolean to know if the time counter is started or not (has the player started to move forward)

        # initialization of constants
        self.nb_asteroid = nb_asteroid          # number of asteroids to display
        self.nb_ring = nb_ring                  # number of rings to display

        self.speed_max_forward = 1              # maximum speed of the player's ship forward
        self.speed_max_back = 0.6               # maximum speed of the player's ship in reverse
        self.rotation_speed = 0.1               # rotation speed of the player's ship

        self.border = 35                        # size of the playing area (the player cannot leave this area)

        # initializing the initial quaternion of the player's ship
        self.current_quaterion = pyrr.Quaternion([0, 0, 0, 1])


    # function allowing you to close the window if you press the 'esc' key
    def key_callback(self, win, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(win, glfw.TRUE)
        self.touch[key] = action


    # function to manage mouse button presses
    def mouse_button_callback(self, win, button, action, mods):
        x , y = glfw.get_cursor_pos(self.window)
        x = (x-self.width/2)/self.width*2
        y = (-y+self.height/2)/self.height*2

        if self.screen == 0:
            button_play = self.objs_start_menu[0]
            button_quit = self.objs_start_menu[1]

            if button_play.is_inside(x, y):
                self.screen = 1

            elif button_quit.is_inside(x, y):
                glfw.set_window_should_close(win, glfw.TRUE)

        elif self.screen == 2:
            button_play = self.objs_end_menu[2]
            button_quit = self.objs_end_menu[3]

            if button_play.is_inside(x, y):
                self.screen = 1
                self.reload_game()

            elif button_quit.is_inside(x, y):
                glfw.set_window_should_close(win, glfw.TRUE)


    # function allowing you to add an object to one of the lists of objects to display (game, start menu or end menu)
    def add_object(self, obj, screen_name):
        if screen_name == 'objs':
            self.objs.append(obj)
        elif screen_name == 'objs_start_menu':
            self.objs_start_menu.append(obj)
        elif screen_name == 'objs_end_menu':
            self.objs_end_menu.append(obj)


    # function to add the camera
    def set_camera(self, cam):
        self.cam = cam


    # function containing the main loop of the program
    def run(self):
        while not glfw.window_should_close(self.window):
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            self.run_menu_start()

            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
            self.run_game()

            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)
            self.run_menu_end()


    # function containing the main loop of the start menu
    def run_menu_start(self):
        while not glfw.window_should_close(self.window) and self.screen == 0:
            # window cleaning
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            # updating pressed keys
            self.update_key()

            # display of objects
            for obj in self.objs_start_menu:
                GL.glUseProgram(obj.program)
                obj.draw()

            # window update
            glfw.swap_buffers(self.window)
            glfw.poll_events()


    # function containing the main loop of the game
    def run_game(self):
        while not glfw.window_should_close(self.window) and self.screen == 1:
            # window cleaning
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            # updating pressed keys
            self.update_key()

            # translation of the player's ship forward
            self.objs[0].transformation.translation += \
                pyrr.matrix33.apply_to_vector(pyrr.matrix33.create_from_quaternion(self.objs[0].transformation.quaternion), pyrr.Vector3([0, 0, -1])) * self.speed

            # collision check between the player's ship and asteroids, rings and edges of the playing area
            self.search_collision_objects(7, 7+self.nb_asteroid, 1.2, 'asteroid')
            self.search_collision_objects(7+self.nb_asteroid, 7+self.nb_asteroid+self.nb_ring, 2.2, 'ring')
            self.collision_border(self.objs[0])

            # updating the camera position based on the new position of the player's ship
            self.update_camera_position()

            # updating the position of the 6 images of the skybox by translation
            for i in range(1,7):
                self.objs[i].transformation.translation = self.objs[0].transformation.translation

            # updating texts (speed, life, score and time)
            self.speed_handler()
            self.objs[7+self.nb_asteroid+self.nb_ring].value = f'vie restante: {self.vie}'
            self.objs[7+self.nb_asteroid+self.nb_ring+1].value = f'anneaux: {self.score}/10'
            if self.count_started:
                self.objs[7+self.nb_asteroid+self.nb_ring+2].value = self.format_time()

            # display of objects
            for obj in self.objs:
                GL.glUseProgram(obj.program)
                if isinstance(obj, Object3D):
                    self.update_camera(obj.program)
                obj.draw()

            # change of display buffer to avoid a flickering effect
            glfw.swap_buffers(self.window)

            # event management
            glfw.poll_events()


    # function containing the main end menu loop
    def run_menu_end(self):
        while not glfw.window_should_close(self.window) and self.screen == 2:
            # window cleaning
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            # updating pressed keys
            self.update_key()

            # display of objects
            for obj in self.objs_end_menu:
                GL.glUseProgram(obj.program)
                obj.draw()

            # window update
            glfw.swap_buffers(self.window)
            glfw.poll_events()


    # function to update camera position
    def update_camera_position(self):
        self.cam.transformation.quaternion = pyrr.quaternion.inverse(self.objs[0].transformation.quaternion.copy())
        self.cam.transformation.rotation_center = self.objs[0].transformation.translation + self.objs[0].transformation.rotation_center
        self.cam.transformation.translation = self.objs[0].transformation.translation + pyrr.Vector3([0, 1.2, 6])


    # function to update the camera
    def update_camera(self, prog):
        GL.glUseProgram(prog)
        loc = GL.glGetUniformLocation(prog, "translation_view")
        if (loc == -1) :
            print("Pas de variable uniforme : translation_view")

        translation = -self.cam.transformation.translation
        GL.glUniform4f(loc, translation.x, translation.y, translation.z, 0)

        loc = GL.glGetUniformLocation(prog, "rotation_center_view")
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_center_view")

        rotation_center = self.cam.transformation.rotation_center
        GL.glUniform4f(loc, rotation_center.x, rotation_center.y, rotation_center.z, 0)

        rot = pyrr.matrix44.create_from_quaternion(-self.cam.transformation.quaternion)
        loc = GL.glGetUniformLocation(prog, "rotation_view")
        if (loc == -1) :
            print("Pas de variable uniforme : rotation_view")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, rot)
    
        loc = GL.glGetUniformLocation(prog, "projection")
        if (loc == -1) :
            print("Pas de variable uniforme : projection")
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, self.cam.projection)


    # function that manages key presses
    def update_key(self):
        if glfw.KEY_UP in self.touch and self.touch[glfw.KEY_UP] > 0 and self.speed < self.speed_max_forward:
            self.speed += 0.05
            if not self.count_started:
                self.count_started = True
                self.start_time = time()
        if glfw.KEY_DOWN in self.touch and self.touch[glfw.KEY_DOWN] > 0 and self.speed > -self.speed_max_back:
            self.speed -= 0.03
            if not self.count_started:
                self.count_started = True
                self.start_time = time()

        if glfw.KEY_A in self.touch and self.touch[glfw.KEY_A] > 0:
            self.rotation_handler(self.objs[0], "yaw", -self.rotation_speed)
        if glfw.KEY_D in self.touch and self.touch[glfw.KEY_D] > 0:
            self.rotation_handler(self.objs[0], "yaw", self.rotation_speed)

        if glfw.KEY_W in self.touch and self.touch[glfw.KEY_W] > 0:
            self.rotation_handler(self.objs[0], "pitch", self.rotation_speed)
        if glfw.KEY_S in self.touch and self.touch[glfw.KEY_S] > 0:
            self.rotation_handler(self.objs[0], "pitch", -self.rotation_speed)

        if glfw.KEY_Q in self.touch and self.touch[glfw.KEY_Q] > 0:
             self.rotation_handler(self.objs[0], "roll", -self.rotation_speed)
        if glfw.KEY_E in self.touch and self.touch[glfw.KEY_E] > 0:
             self.rotation_handler(self.objs[0], "roll", self.rotation_speed)

        if glfw.KEY_R in self.touch and self.touch[glfw.KEY_R] > 0:
            self.reload_game()


    # function which allows you to manage the display of the ship's speed
    def speed_handler(self):
        for i in range(0,6):
            if abs(self.speed) >= self.speed_max_forward*(i+1)/6:
                self.objs[10+self.nb_asteroid+self.nb_ring+i].value = '-'
            else:
                self.objs[10+self.nb_asteroid+self.nb_ring+i].value = ' '


    # function which manages the rotation of the ship depending on the button pressed
    def rotation_handler(self, obj, rot, speed):
        if rot =='pitch': new_quaternion = pyrr.Quaternion.from_x_rotation(speed)
        elif rot == 'yaw': new_quaternion = pyrr.Quaternion.from_y_rotation(speed)
        else: new_quaternion = pyrr.Quaternion.from_z_rotation(speed)

        self.current_quaterion = new_quaternion * self.current_quaterion #/!\ do not touch this line and especially do not replace it with *=
        obj.transformation.quaternion = self.current_quaterion


    # function allowing you to search for collisions between the ship and the objects passed as a parameter
    def search_collision_objects(self, objects_ind_start, objects_ind_end, trigger_dist, type):
        for i in range(objects_ind_start, objects_ind_end):
            dist = self.objs[0].transformation.translation - self.objs[i].transformation.translation
            if np.linalg.norm(dist) <= trigger_dist and self.objs[i].visible == True:
                self.objs[i].visible = False
                if type == 'ring':
                    self.score += 1
                    if self.score == 10:
                        self.objs_end_menu[0].value = "Vous avez gagne !"
                        self.objs_end_menu[1].value = f'Votre temps: {self.format_time()}'
                        self.screen = 2
                else:
                    self.vie -= 1
                    if self.vie == 0:
                        self.objs_end_menu[1].value = f'Votre temps: {self.format_time()}'
                        self.screen = 2
                    if self.speed > 0:
                        if self.speed > 0.5: self.speed -= 0.3
                        else: self.speed = 0.1
                    else:
                        if self.speed < -0.5: self.speed += 0.3
                        else: self.speed = -0.1


    # function to check for collisions between the ship and the borders
    def collision_border(self, obj):
        for i in range(0,3):
            if obj.transformation.translation[i] > self.border:
                obj.transformation.translation[i] = -self.border
            elif obj.transformation.translation[i] < -self.border:
                obj.transformation.translation[i] = self.border


    # function allowing you to reload the game at the end of a game to restart another
    def reload_game(self):
        self.objs[0].transformation.translation = pyrr.Vector3()
        self.current_quaterion = pyrr.Quaternion([0, 0, 0, 1])
        self.objs[0].transformation.quaternion = self.current_quaterion.copy()
        self.speed = 0.0
        self.score = 0
        self.vie = 3
        self.count_started = False
        self.start_time = 0
        self.objs[7+self.nb_asteroid+self.nb_ring+2].value = '00:00'
        for i in range(7, 7+self.nb_asteroid+self.nb_ring):
            self.objs[i].visible = True


    # function to format time in ss:msms format
    def format_time(self):
        car_l = str(round(time() - self.start_time, 2)).split('.')
        for i in range(len(car_l)): car_l[i] = car_l[i].zfill(2)
        return(":".join(car_l))