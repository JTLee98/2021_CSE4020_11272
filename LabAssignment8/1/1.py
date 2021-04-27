import numpy as np
from numpy import linalg
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

gCamAng = 0.0
gComposedM = np.identity(4)


def render(Matrix, CamAng):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glLoadIdentity()
    glOrtho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0)
    gluLookAt(.1*np.sin(CamAng), .1, .1*np.cos(CamAng), 0, 0, 0, 0, 1, 0)
    # draw axes
    drawAxes(1.0)
    # draw triangle
    glBegin(GL_TRIANGLES)
    glColor3ub(255, 255, 255)
    glVertex3fv((Matrix @ np.array([.0, .5, 0., 1.]))[:-1])
    glVertex3fv((Matrix @ np.array([.0, .0, 0., 1.]))[:-1])
    glVertex3fv((Matrix @ np.array([.5, .0, 0., 1.]))[:-1])
    glEnd()


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

# return a 3d roation matrix
# (axis is 3d vector, angle is ccw)


def rotateM(axis, angle):
    angle = angle*(np.pi/180)
    cos = np.cos(angle)
    sin = np.sin(angle)
    u = axis/linalg.norm(axis)  # normalized axis vect
    u_crossM = np.cross(u, -1*np.identity(3))  # cross prod matrix of u (3x3)
    R_3x3 = cos*np.identity(3) + sin*u_crossM + (1-cos)*np.outer(u, u)
    R_affine = np.hstack(
        (np.vstack((R_3x3, np.zeros([1, 3]))), np.zeros([4, 1])))
    R_affine[3, 3] = 1.0
    return R_affine


### controls ###
# key | control               | coords
# ---------------------------------------------
# Q   | Translate x dir -0.1  | global
# E   | Translate x dir +0.1  | global
# A   | Rotate y axis -10 deg | local
# D   | Rotate y axis +10 deg | local
# W   | Rotate x axis -10 deg | local
# S   | Rotate x axis +10 deg | local
# 1   | Rotate cam -10 deg
# 3   | Rotate cam +10 deg
# ESC | exit program

def key_callback(window, key, scancode, action, mods):
    global gCamAng, gComposedM
    xaxis = np.array([1.0, 0.0, 0.0])
    yaxis = np.array([0.0, 1.0, 0.0])
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_Q:
            gComposedM[0:3, 3] += -0.1
        elif key == glfw.KEY_E:
            gComposedM[0:3, 3] += +0.1
        elif key == glfw.KEY_A:
            gComposedM = gComposedM @ rotateM(yaxis, -10)
        elif key == glfw.KEY_D:
            gComposedM = gComposedM @ rotateM(yaxis, +10)
        elif key == glfw.KEY_W:
            gComposedM = gComposedM @ rotateM(xaxis, -10)
        elif key == glfw.KEY_S:
            gComposedM = gComposedM @ rotateM(xaxis, +10)
        elif key == glfw.KEY_1:
            gCamAng += np.radians(-10)
        elif key == glfw.KEY_3:
            gCamAng += np.radians(+10)
        elif key == glfw.KEY_ESCAPE:
            exit()


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
    glEnable(GL_DEPTH_TEST | GL_NORMALIZE)
    glEnableClientState(GL_VERTEX_ARRAY)
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    while not glfw.window_should_close(window):
        glfw.wait_events()

        # render
        render(gComposedM, gCamAng)

        glfw.swap_buffers(window)
    glfw.terminate()

    return 0


if __name__ == "__main__":
    main()
