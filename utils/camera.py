import glfw
from utils.transform import vec, translate, normalized, np, perspective

class Camera:
    """
    Home made camera (based on Euler angles).
    """
    def __init__(self):
        # different camera positions        camera_pos      pitch   yaw
        self.camera_positions = [(vec(0.0, 1000.0, 2200.0), -20.0, 95.0), # distant camera
                                 (vec(-1022.3244, 362.63553, 810.2243), 10.0, 80.0), # near koalas
                                 (vec(2000.0, 280.0, 2000.0), -20.0, -90.0), # above the water
                                 (vec(0.0, 1200.0, -2300.0), -20.0, -90.0), # behind the island
                                 (vec(800.0, 610.0, 840.0), -10.0, 0.0), # near the sheep all alone
                                 (vec(850.0, 570.0, 810.0), 10.0, 5.0)] # near the sheep all alone
        self.index_camera = 1

        # current camera attributes (pos, yaw, pitch...) default = distant camera
        self.camera_pos = np.copy(self.camera_positions[5][0]) # current camera pos
        self.pitch = self.camera_positions[5][1]
        self.yaw = self.camera_positions[5][2]

        # camera referential
        self.world_up = vec(0.0, 1.0, 0.0)
        self.up = vec(0.0, 1.0, 0.0)
        self.rgt = vec(0.0, 0.0, 0.0)
        self.fwd = vec(0.0, 0.0, -1.0)

        # sensitivity, speed
        self.speed = 300.0
        self.sensitivity = 0.1
        self.update_vectors()

        # camera matrices
        self.view = None
        self.proj = None



    def update_vectors(self):

        rad_yaw = np.deg2rad(self.yaw)
        rad_pitch = np.deg2rad(self.pitch)

        pitch_cos = np.cos(rad_pitch)
        self.fwd = np.array([np.cos(rad_yaw)* pitch_cos, np.sin(rad_pitch),
                             -np.sin(rad_yaw)*pitch_cos])
        self.fwd = normalized(self.fwd)

        # updating rgt & up vectors
        self.rgt = normalized(np.cross(self.fwd, self.world_up))
        self.up = normalized(np.cross(self.rgt, self.fwd))



    def view_matrix(self):
        rotation = np.identity(4)
        rotation[:3, :3] = np.vstack([self.rgt, self.up, -self.fwd])
        self.view = rotation @ translate(-self.camera_pos)
        return self.view

    def projection_matrix(self, winsize):
        self.proj = perspective(90, winsize[0] / winsize[1], 0.1, 15000.0)
        return self.proj

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

        if (key == glfw.KEY_BACKSPACE and (action == glfw.REPEAT or action == glfw.PRESS)):
            self.camera_pos -= self.world_up * speed

        if (key == glfw.KEY_RIGHT and (action == glfw.REPEAT or action == glfw.PRESS)):
            self.yaw -= 5

        if (key == glfw.KEY_LEFT and (action == glfw.REPEAT or action == glfw.PRESS)):
            self.yaw += 5

        if (key == glfw.KEY_UP and (action == glfw.REPEAT or action == glfw.PRESS)):
            if self.pitch + 5 < 90:
                self.pitch += 5

        if (key == glfw.KEY_DOWN and (action == glfw.REPEAT or action == glfw.PRESS)):
            if self.pitch - 5 > - 90:
                self.pitch -= 5

        if (key == glfw.KEY_C and (action == glfw.REPEAT or action == glfw.PRESS)):
            if self.index_camera == 5:
                self.index_camera = 0

            self.camera_pos = np.copy(self.camera_positions[self.index_camera][0])
            self.pitch = self.camera_positions[self.index_camera][1]
            self.yaw = self.camera_positions[self.index_camera][2]
            self.index_camera += 1

            self.world_up = vec(0.0, 1.0, 0.0)
            self.up = vec(0.0, 1.0, 0.0)
            self.rgt = vec(0.0, 0.0, 0.0)
            self.fwd = vec(0.0, 0.0, -1.0)

        # we update the vectors in case we modified the pitch or the yaw
        self.update_vectors()

    def handle_mouse_movement(self, offset_x, offset_y):

        self.pitch += (offset_y * self.sensitivity)
        self.yaw += (offset_x * self.sensitivity)

        boundary = 89.0
        if self.pitch > boundary:
            self.pitch = boundary
        if self.pitch < -boundary:
            self.pitch = -boundary
        self.update_vectors()

