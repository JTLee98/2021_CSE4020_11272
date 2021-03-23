import numpy as np
import glfw
from OpenGL.GL import *

p1 = np.array([[0.5], [0.0], [1.0]])
p2 = np.array([[0.0], [0.5], [1.0]])

v1 = np.array([[0.5], [0.0], [0.0]])
v2 = np.array([[0.0], [0.5], [0.0]])


def render(th):
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

    # calculate matrix M1, M2 using time
    # your implementation
    M1 = np.identity(3)
    M2 = np.identity(3)

    M1[0, 2] = 0.5
    M2[1, 2] = 0.5

    Mr = np.array([[np.cos(th), -np.sin(th), 0.0],
                   [np.sin(th),  np.cos(th), 0.0],
                   [0.0, 0.0, 1.0]])

    M1 = Mr @ M1
    M2 = Mr @ M2

    # draw point p
    glBegin(GL_POINTS)
    # your implementation
    # p1
    glVertex2fv((M1 @ p1)[:2])
    # p2
    glVertex2fv((M2 @ p2)[:2])
    glEnd()

    # draw vector v
    glBegin(GL_LINES)
    # v1
    glVertex2f(0.0, 0.0)
    glVertex2fv((M1 @ v1)[:2])
    # v2
    glVertex2f(0.0, 0.0)
    glVertex2fv((M2 @ v2)[:2])
    glEnd()


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
    glfw.set_time(0)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        # render
        render(glfw.get_time())

        glfw.swap_buffers(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
