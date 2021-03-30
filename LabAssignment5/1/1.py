import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

# (1-B) drawFrame() and drawTriangle()


def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([1., 0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([0., 1.]))
    glEnd()


def drawTriangle():
    glBegin(GL_TRIANGLES)
    glVertex2fv(np.array([0., .5]))
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([.5, 0.]))
    glEnd()


def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    # (1-C) global frame & white triangle
    drawFrame()
    glColor3ub(255, 255, 255)
    drawTriangle()
    # (1-D) blue triangle
    glPushMatrix()
    glTranslatef(0.6, 0.0, 0.0)
    glRotatef(30.0, 0.0, 0.0, 1.0)
    drawFrame()
    glColor3ub(0, 0, 255)
    drawTriangle()
    glPopMatrix()
    # (1-E) red triangle
    glPushMatrix()
    glRotatef(30.0, 0.0, 0.0, 1.0)
    glTranslatef(0.6, 0.0, 0.0)
    drawFrame()
    glColor3ub(255, 0, 0)
    drawTriangle()
    glPopMatrix()


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
    # glfw.set_key_callback(window, key_callback)

    while not glfw.window_should_close(window):
        glfw.wait_events()

        # render
        render()

        glfw.swap_buffers(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
