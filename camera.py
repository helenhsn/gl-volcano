import glfw
import glm
from transform import *
from math import cos, sin, pi
class Camera:
    def __init__(self):
        self.camera_pos = vec(0.0, 100.0, 100.0)
        self.world_up = vec(0.0, 1.0, 0.0)
        self.up = vec(0.0, 1.0, 0.0)
        self.right = vec(0.0, 0.0, 0.0)
        self.front = vec(0.0, 0.0, -1.0)

        self.velocity = vec(0.0, 0.0, 0.0)
        self.speed = 400.0
        self.previous_mouse_pos = vec(0.0, 0.0)
        self.sensitivity = 0.1
        self.pitch = -45.0
        self.yaw = 90.0
        self.first_mouse_move = True

        self.update_vectors()

    
    def update_vectors(self):

        rad_yaw = np.deg2rad(self.yaw)
        rad_pitch = np.deg2rad(self.pitch)
        self.front = vec(cos(rad_yaw)* cos(rad_pitch), sin(rad_pitch), sin(rad_yaw)*cos(rad_pitch))
        self.front = normalized(self.front)

        # updating right & up vectors
        self.right = normalized(np.cross(self.front, self.world_up))
        self.up = normalized(np.cross(self.right, self.front))


    def view_matrix(self):

        #print("eye =", self.front + self.camera_pos, "camera pos = ", self.camera_pos)

        rotation = np.identity(4)
        rotation[:3, :3] = np.vstack([self.right, self.up, -self.front])
        return rotation @ translate(-self.camera_pos)
        #return lookat(self.camera_pos, self.camera_pos + self.front, self.up)

    def projection_matrix(self, winsize):
        return perspective(45, winsize[0] / winsize[1], 0.1, 100000.0)

    def handle_keys(self, key, action, delta_time):

        velocity = self.speed * delta_time

        if (key == glfw.KEY_W and (action == glfw.REPEAT or action == glfw.PRESS)):
            self.camera_pos += self.front * velocity

        if (key == glfw.KEY_S and (action == glfw.REPEAT or action == glfw.PRESS)):

            self.camera_pos -= self.front * velocity
        
        if (key == glfw.KEY_A and (action == glfw.REPEAT or action == glfw.PRESS)):

            self.camera_pos -= self.right * velocity
        
        if (key == glfw.KEY_D and (action == glfw.REPEAT or action == glfw.PRESS)):

            self.camera_pos += self.right * velocity

        if (key == glfw.KEY_SPACE and (action == glfw.REPEAT or action == glfw.PRESS)):
            self.camera_pos += self.world_up * velocity
            
    def handle_mouse_movement(self, mouse_pos):
        if self.first_mouse_move:
            self.previous_mouse_pos = mouse_pos
            self.first_mouse_move = False
        else:
            slope_mouse = (mouse_pos[0] - self.previous_mouse_pos[0],  mouse_pos[1] - self.previous_mouse_pos[1])
            self.pitch -= slope_mouse[1] * self.sensitivity
            self.yaw -= slope_mouse[0] * self.sensitivity

            boundary = 89.0
            if self.pitch > boundary:
                self.pitch = boundary
            if self.pitch < -boundary:
                self.pitch = -boundary
            self.update_vectors()
            self.first_mouse_move = False
            self.previous_mouse_pos = mouse_pos

