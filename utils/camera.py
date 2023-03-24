import glfw
from utils.transform import *
from math import cos, sin, pi
class Camera:
    def __init__(self):
        self.camera_pos = vec(0.0, 1000.0, 3000.0)
        self.world_up = vec(0.0, 1.0, 0.0)
        self.up = vec(0.0, 1.0, 0.0)
        self.rgt = vec(0.0, 0.0, 0.0)
        self.fwd = vec(0.0, 0.0, -1.0)

        self.speed = vec(0.0, 0.0, 0.0)
        self.speed = 300.0
        self.sensitivity = 0.1
        self.pitch = -45.0
        self.yaw = 90.0
        self.update_vectors()

    
    def update_vectors(self):

        rad_yaw = np.deg2rad(self.yaw)
        rad_pitch = np.deg2rad(self.pitch)

        pitch_cos = np.cos(rad_pitch)
        self.fwd = np.array([np.cos(rad_yaw)* pitch_cos, np.sin(rad_pitch), -np.sin(rad_yaw)*pitch_cos])
        self.fwd = normalized(self.fwd)

        # updating rgt & up vectors
        self.rgt = normalized(np.cross(self.fwd, self.world_up))
        self.up = normalized(np.cross(self.rgt, self.fwd))



    def view_matrix(self):


        rotation = np.identity(4)
        rotation[:3, :3] = np.vstack([self.rgt, self.up, -self.fwd])
        return rotation @ translate(-self.camera_pos)

    def projection_matrix(self, winsize):
        return perspective(45, winsize[0] / winsize[1], 0.1, 10000.0)

    def handle_keys(self, key, action, delta_time):

        speed = self.speed * delta_time

        if (key == glfw.KEY_W and (action == glfw.REPEAT or action == glfw.PRESS)):
            self.camera_pos += self.fwd * speed

        if (key == glfw.KEY_S and (action == glfw.REPEAT or action == glfw.PRESS)):

            self.camera_pos -= self.fwd * speed
        
        if (key == glfw.KEY_A and (action == glfw.REPEAT or action == glfw.PRESS)):

            self.camera_pos -= self.rgt * speed
        
        if (key == glfw.KEY_D and (action == glfw.REPEAT or action == glfw.PRESS)):

            self.camera_pos += self.rgt * speed

        if (key == glfw.KEY_SPACE and (action == glfw.REPEAT or action == glfw.PRESS)):
            self.camera_pos += self.world_up * speed
            
    def handle_mouse_movement(self, offset_x, offset_y):

        self.pitch += (offset_y * self.sensitivity)
        self.yaw += (offset_x * self.sensitivity)

        boundary = 89.0
        if self.pitch > boundary:
            self.pitch = boundary
        if self.pitch < -boundary:
            self.pitch = -boundary
        self.update_vectors()

