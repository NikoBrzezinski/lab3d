import glfw
from OpenGL.GL import *
import numpy as np

VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;
out vec3 ourColor;
void main() {
    gl_Position = vec4(aPos, 1.0);
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
    glfw.init()
    window = glfw.create_window(800, 600, "RGB", None, None)
    glfw.make_context_current(window)

    shader_program = compile_shaders()

    vertices = np.array([
        -0.5, -0.5, 0.0,  1.0, 0.0, 0.0,  # Bottom Left (Red)
         0.5, -0.5, 0.0,  0.0, 1.0, 0.0,  # Bottom Right (Green)
         0.0,  0.5, 0.0,  0.0, 0.0, 1.0   # Top Middle (Blue)
    ], dtype=np.float32)

    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)

    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)

    while not glfw.window_should_close(window):
        glClearColor(0.1, 0.1, 0.1, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(shader_program)
        glBindVertexArray(VAO)
        glDrawArrays(GL_TRIANGLES, 0, 3)
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

if __name__ == "__main__":
    main()
