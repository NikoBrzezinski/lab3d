import glfw
from OpenGL.GL import *
import numpy as np
import csv
import ctypes
from pyrr import Matrix44, Vector3

class TerrainRenderer:
    def __init__(self, filename, grid_size=5):
        self.filename = filename
        self.grid_size = grid_size
        self.shader_program = None
        
        # Camera State
        self.cam_pos = np.array([0.0, 10.0, 40.0], dtype=np.float32)
        self.cam_yaw = 0.0
        
        # Sphere State
        self.sphere_pos = np.array([0.0, 5.0, 0.0], dtype=np.float32)
        self.sphere_yaw = 0.0  # Rotation in radians

    def load_data(self):
        rows = []
        try:
            with open(self.filename, 'r') as csvfile:
                csvreader = csv.reader(csvfile)
                next(csvreader)  # Skip header
                for row in csvreader:
                    if not row: continue
                    x, y, z = [float(val) for val in row]
                    # Use actual coordinates for position, and normalized for color
                    r, g, b = (x + 20) / 40, (y + 20) / 40, (z + 20) / 40
                    rows.extend([x, y, z, r, g, b])
        except FileNotFoundError:
            print("CSV not found, using dummy data.")
            return None, None

        vertices = np.array(rows, dtype=np.float32)
        indices = []
        for i in range(self.grid_size - 1):
            for j in range(self.grid_size - 1):
                top_left = i * self.grid_size + j
                top_right = top_left + 1
                bottom_left = (i + 1) * self.grid_size + j
                bottom_right = bottom_left + 1
                indices.extend([top_left, top_right, bottom_left])
                indices.extend([top_right, bottom_right, bottom_left])

        return vertices, np.array(indices, dtype=np.uint32)

    def create_sphere(self, radius=1.5, rings=20, sectors=20):
        verts, indices = [], []
        for r in range(rings + 1):
            phi = np.pi * r / rings
            for s in range(sectors + 1):
                theta = 2 * np.pi * s / sectors
                x = radius * np.sin(phi) * np.cos(theta)
                y = radius * np.cos(phi)
                z = radius * np.sin(phi) * np.sin(theta)
                verts.extend([x, y, z, 1.0, 1.0, 0.0]) # Yellow Sphere
        for r in range(rings):
            for s in range(sectors):
                cur, nxt = r * (sectors + 1) + s, (r + 1) * (sectors + 1) + s
                indices.extend([cur, nxt, cur + 1, nxt, nxt + 1, cur + 1])
        return np.array(verts, dtype=np.float32), np.array(indices, dtype=np.uint32)

    def init_opengl(self, t_verts, t_indices):
        v_src = """
        #version 330 core
        layout (location = 0) in vec3 aPos;
        layout (location = 1) in vec3 aColor;
        out vec3 ourColor;
        uniform mat4 model, view, proj;
        void main() {
            gl_Position = proj * view * model * vec4(aPos, 1.0);
            ourColor = aColor;
        }"""
        f_src = """
        #version 330 core
        out vec4 FragColor;
        in vec3 ourColor;
        void main() { FragColor = vec4(ourColor, 1.0); }"""
        
        self.shader_program = self._compile(v_src, f_src)
        
        def gen_vao(v, i):
            vao = glGenVertexArrays(1)
            glBindVertexArray(vao)
            vbo, ebo = glGenBuffers(2)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, v.nbytes, v, GL_STATIC_DRAW)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, i.nbytes, i, GL_STATIC_DRAW)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
            glEnableVertexAttribArray(1)
            return vao, len(i)

        self.t_vao, self.t_cnt = gen_vao(t_verts, t_indices)
        s_v, s_i = self.create_sphere()
        self.s_vao, self.s_cnt = gen_vao(s_v, s_i)

    def _compile(self, vs, fs):
        p = glCreateProgram()
        for s, t in [(vs, GL_VERTEX_SHADER), (fs, GL_FRAGMENT_SHADER)]:
            sh = glCreateShader(t); glShaderSource(sh, s); glCompileShader(sh)
            glAttachShader(p, sh)
        glLinkProgram(p)
        return p

    def update(self, window, dt):
        speed = 10.0 * dt
        rot_speed = 2.0 * dt

        # Camera WSADQE
        if glfw.get_key(window, glfw.KEY_W): self.cam_pos[2] -= speed
        if glfw.get_key(window, glfw.KEY_S): self.cam_pos[2] += speed
        if glfw.get_key(window, glfw.KEY_A): self.cam_pos[0] -= speed
        if glfw.get_key(window, glfw.KEY_D): self.cam_pos[0] += speed
        if glfw.get_key(window, glfw.KEY_Q): self.cam_yaw += rot_speed
        if glfw.get_key(window, glfw.KEY_E): self.cam_yaw -= rot_speed

        # Sphere Arrows (Directional Movement)
        if glfw.get_key(window, glfw.KEY_LEFT):  self.sphere_yaw += rot_speed
        if glfw.get_key(window, glfw.KEY_RIGHT): self.sphere_yaw -= rot_speed
        
        # Calculate Forward Vector based on Yaw
        forward_x = np.sin(self.sphere_yaw)
        forward_z = np.cos(self.sphere_yaw)

        if glfw.get_key(window, glfw.KEY_UP):
            self.sphere_pos[0] += forward_x * speed
            self.sphere_pos[2] += forward_z * speed
        if glfw.get_key(window, glfw.KEY_DOWN):
            self.sphere_pos[0] -= forward_x * speed
            self.sphere_pos[2] -= forward_z * speed

    def render(self, window):
        glEnable(GL_DEPTH_TEST)
        m_loc = glGetUniformLocation(self.shader_program, "model")
        v_loc = glGetUniformLocation(self.shader_program, "view")
        p_loc = glGetUniformLocation(self.shader_program, "proj")
        last_t = glfw.get_time()

        while not glfw.window_should_close(window):
            dt = glfw.get_time() - last_t
            last_t = glfw.get_time()
            self.update(window, dt)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glUseProgram(self.shader_program)

            proj = Matrix44.perspective_projection(45.0, 800/600, 0.1, 200.0)
            view = Matrix44.from_y_rotation(self.cam_yaw) * Matrix44.from_translation(-self.cam_pos)
            glUniformMatrix4fv(p_loc, 1, GL_FALSE, proj)
            glUniformMatrix4fv(v_loc, 1, GL_FALSE, view)

            # Draw Terrain
            glUniformMatrix4fv(m_loc, 1, GL_FALSE, Matrix44.identity())
            glBindVertexArray(self.t_vao)
            glDrawElements(GL_TRIANGLES, self.t_cnt, GL_UNSIGNED_INT, None)

            # Draw Sphere
            s_model = Matrix44.from_translation(self.sphere_pos) * Matrix44.from_y_rotation(self.sphere_yaw)
            glUniformMatrix4fv(m_loc, 1, GL_FALSE, s_model)
            glBindVertexArray(self.s_vao)
            glDrawElements(GL_TRIANGLES, self.s_cnt, GL_UNSIGNED_INT, None)

            glfw.swap_buffers(window)
            glfw.poll_events()

def main():
    glfw.init()
    win = glfw.create_window(800, 600, "Terrain Fix", None, None)
    glfw.make_context_current(win)
    
    # Grid size for your CSV is 5x5
    r = TerrainRenderer('coordinates.csv', grid_size=5)
    v, i = r.load_data()
    if v is not None:
        r.init_opengl(v, i)
        r.render(win)
    glfw.terminate()

if __name__ == "__main__":
    main()
