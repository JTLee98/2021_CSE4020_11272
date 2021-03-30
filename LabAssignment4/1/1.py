import numpy as np
import glfw
from OpenGL.GL import *


def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    # draw cooridnate
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([1., 0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([0., 1.]))
    glEnd()
    glColor3ub(255, 255, 255)

    # implement here
    for cmd in keyHistL:
        cmd()  # execute each 'cmd' function

    # drawTriangle func
    drawTriangle()


def drawTriangle():
    glBegin(GL_TRIANGLES)
    glVertex2fv(np.array([0., .5]))
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([.5, 0.]))
    glEnd()


# key callback function
def Q():
    glTranslatef(-0.1, 0.0, 0.0)


def E():
    glTranslatef(0.1, 0.0, 0.0)


def A():
    glRotatef(10.0, 0.0, 0.0, 1.0)


def D():
    glRotatef(-10.0, 0.0, 0.0, 1.0)


# store key history (by appending) in 'keyHistL' list
cmdLookupD = {glfw.KEY_Q: Q, glfw.KEY_E: E, glfw.KEY_A: A, glfw.KEY_D: D}
keyHistL = []  # list of func pointers (Q(), E(), A() ,D())


def key_callback(window, key, scancode, action, mods):
    global keyHistL
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key in cmdLookupD:
            keyHistL.insert(0, cmdLookupD[key])
        elif key == glfw.KEY_1:
            keyHistL = []
        else:
            return


def main():
    # glfw stuff
    if not glfw.init():
        return
    window = glfw.create_window(480, 480, "2018014275", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_key_callback(window, key_callback)

    while not glfw.window_should_close(window):
        glfw.wait_events()

        # render
        render()

        glfw.swap_buffers(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
