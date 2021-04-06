import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

gCamHeight = 0
gCamAng = 0

varr = np.array([(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1),
                (0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)], dtype=np.float32)
iarr = np.array([
    (0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (3, 2, 6, 7)], dtype=np.uint32)

# draw funcs


def drawFrame(size, xcol, ycol, zcol):
    glBegin(GL_LINES)
    glColor3ubv(xcol)
    glVertex3f(0, 0, 0)
    glVertex3f(size, 0, 0)
    glColor3ubv(ycol)
    glVertex3f(0, 0, 0)
    glVertex3f(0, size, 0)
    glColor3ubv(zcol)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, size)
    glEnd()
    return


def render():
    global iarr, varr
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluPerspective(45, 1, 1, 10)
    gluLookAt(5*np.sin(gCamAng), gCamHeight, 5 *
              np.cos(gCamAng), 0, 0, 0, 0, 1, 0)

    drawFrame(1.0, np.array([255, 0, 0]), np.array(
        [0, 255, 0]), np.array([0, 0, 255]))
    glColor3ub(255, 255, 255)
    glVertexPointer(3, GL_FLOAT, 12, 1.5*varr)
    glDrawElements(GL_QUADS, 16, GL_UNSIGNED_INT, iarr)


def key_callback(window, key, scancode, action, mods):
    global gCamAng, gCamHeight
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_1:
            gCamAng += np.radians(-10)
        elif key == glfw.KEY_3:
            gCamAng += np.radians(10)
        elif key == glfw.KEY_2:
            gCamHeight += .1
        elif key == glfw.KEY_W:
            gCamHeight += -.1


def main():
    if not glfw.init():
        print("glfw failed to init")
        return -1
    window = glfw.create_window(480, 480, "2018014275", None, None)
    if not window:
        glfw.terminate()
        return -1
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_key_callback(window, key_callback)
    glEnable(GL_DEPTH_TEST)
    glEnableClientState(GL_VERTEX_ARRAY)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # bind vertex pos buffer (varr)

    while not glfw.window_should_close(window):
        glfw.wait_events()

        # render
        render()

        glfw.swap_buffers(window)
    glfw.terminate()

    return 0


if __name__ == "__main__":
    main()
