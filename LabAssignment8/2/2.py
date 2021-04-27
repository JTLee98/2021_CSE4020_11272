import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *


def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-2, 2, -2, 2, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    drawAxes(1)
    t = glfw.get_time()
    # blue base transformation
    glPushMatrix()
    glTranslatef(np.sin(t), 0, 0)
    drawAxes(1)
    # blue base drawing
    glPushMatrix()
    glScalef(.2, .2, .2)
    glColor3ub(0, 0, 255)
    drawBox()
    glPopMatrix()
    # red arm transformation
    glPushMatrix()
    glRotatef(t*(180/np.pi), 0, 0, 1)
    glTranslatef(.5, 0, .01)
    drawAxes(1)
    # red arm drawing
    glPushMatrix()
    glScalef(.5, .1, .1)
    glColor3ub(255, 0, 0)
    drawBox()
    glPopMatrix()
    # green box transformation
    glPushMatrix()
    glTranslatef(0.5, 0, 0)
    glRotatef(t*(180/np.pi), 0, 0, 1)
    drawAxes(1)
    # green box drawing
    glPushMatrix()
    glColor3ub(0, 255, 0)
    glScalef(0.2, 0.2, 1)
    drawBox()
    glPopMatrix()
    ###
    glPopMatrix()
    glPopMatrix()
    glPopMatrix()


def drawAxes(length):
    glPushMatrix()
    glScalef(length, length, length)
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(1.0, 0.0, 0.0)
    glColor3ub(0, 255, 0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 1.0, 0.0)
    glColor3ub(0, 0, 255)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 1.0)
    glEnd()
    glPopMatrix()
    return


def drawBox():
    glBegin(GL_QUADS)
    glVertex3f(1.0, 1.0, 0.0)
    glVertex3f(-1.0, 1.0, 0.0)
    glVertex3f(-1.0, -1.0, 0.0)
    glVertex3f(1.0, -1.0, 0.0)
    glEnd()


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
    # glfw.set_key_callback(window, key_callback)
    glEnable(GL_DEPTH_TEST | GL_NORMALIZE)
    # glEnableClientState(GL_VERTEX_ARRAY)
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        # render
        render()

        glfw.swap_buffers(window)
    glfw.terminate()

    return 0


if __name__ == "__main__":
    main()
