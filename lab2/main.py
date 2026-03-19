import glfw
from OpenGL.GL import *
import numpy as np
import csv

filename = 'coordinates.csv'
#aPos/20 normalizuje koordynaty
VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;
out vec3 ourColor;

uniform mat4 transform;

void main() {
    gl_Position = transform * vec4(aPos.x/20,aPos.y/20,aPos.z/20, 1.0);
    ourColor = aColor;
}
"""

FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;
in vec3 ourColor;
void main() {
    FragColor = vec4(ourColor, 1.0f);
}
"""

def main():
    rows = []#xyzrgb
    with open(filename,'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvfile)
        for row in csvreader:
            x,y,z = [float(val) for val in row]
            r = (x+20)/40
            g = (y+20)/40
            b = (z+20)/40
            rows.extend([x,y,z,r,g,b])
    vertices = np.array(rows,dtype = np.float32)
    vertex_count = len(vertices)//6

    grid_size = 5 
    indices = []
    for i in range(grid_size - 1):
        for j in range(grid_size - 1):
            # Calculate the 4 corners of the current quad
            top_left = i * grid_size + j
            top_right = top_left + 1
            bottom_left = (i + 1) * grid_size + j
            bottom_right = bottom_left + 1
            
            # Triangle 1
            indices.extend([top_left, top_right, bottom_left])
            # Triangle 2
            indices.extend([top_right, bottom_right, bottom_left])

    indices = np.array(indices, dtype=np.uint32)

    glfw.init()
    window = glfw.create_window(800, 600, "RGB", None, None)
    glfw.make_context_current(window)

    shader_program = compile_shaders()

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)

    glBindVertexArray(VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)

    transform_loc = glGetUniformLocation(shader_program,"transform")

    while not glfw.window_should_close(window):
        glClearColor(0.1, 0.1, 0.1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        glUseProgram(shader_program)
        time_val = glfw.get_time()
        rotation = get_rotation_y(time_val)
        glUniformMatrix4fv(transform_loc, 1, GL_TRUE, rotation)

        glBindVertexArray(VAO)
        
        glPointSize(10)
        glDrawElements(GL_TRIANGLES,len(indices),GL_UNSIGNED_INT,None)
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

def compile_shaders():
    vs = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vs, VERTEX_SHADER)
    glCompileShader(vs)
    
    fs = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fs, FRAGMENT_SHADER)
    glCompileShader(fs)
    
    prog = glCreateProgram()
    glAttachShader(prog, vs)
    glAttachShader(prog, fs)
    glLinkProgram(prog)
    return prog

def get_rotation_y(theta):
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([
        [c,  0,  s,  0],
        [0,  1,  0,  0],
        [-s, 0,  c,  0],
        [0,  0,  0,  1]
    ], dtype=np.float32)

if __name__ == "__main__":
    main()
