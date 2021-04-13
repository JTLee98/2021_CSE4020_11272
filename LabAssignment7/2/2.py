import numpy as np
import glfw
import ctypes
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

gCamAng = 0.0
gCamHeight = 0.0
gLightPos = (3., 4., 5., 1.)
gLightCol = (0.5, 0.5, 0.5, 1.0)  # diffuse & spec
gObjCol = (1.0, 1.0, 1.0, 1.0)  # ambient & diffuse
gVertexArraySeparate = None
gIndexArraySeparate = None

flag = 0
R = (1.0, 0.1, 0.1, 1.0)
G = (0.1, 1.0, 0.1, 1.0)
B = (0.1, 0.1, 1.0, 1.0)
W = (1.0, 1.0, 1.0, 1.0)


def create_varr():
    varr = np.array([
        (-1,  1,  1),  # v0 position
        (1,  1,  1),  # v1 position
        (1, -1,  1),  # v2 position
        (-1, -1,  1),  # v3 position
        (-1,  1, -1),  # v4
        (1,  1, -1),  # v5
        (1, -1, -1),  # v6
        (-1, -1, -1),  # v7
    ], dtype=np.float32)
    return varr


def create_iarr():
    iarr = np.array([
        (0, 2, 1),
        (0, 3, 2),
        (4, 5, 6),
        (4, 6, 7),
        (0, 1, 5),
        (0, 5, 4),
        (3, 6, 2),
        (3, 7, 6),
        (1, 2, 6),
        (1, 6, 5),
        (0, 7, 3),
        (0, 4, 7)
    ], dtype=np.uint32)
    return iarr


def render():
    global gCamAng, gCamHeight, gLightCol, gObjCol
    glEnable(GL_DEPTH_TEST)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    varr = create_varr()
    iarr = create_iarr()
    glVertexPointer(3, GL_FLOAT, 12, varr)
    glNormalPointer(GL_FLOAT, 12, varr)
    # provided code - transforms
    glLoadIdentity()
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 1, 10)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(5*np.sin(gCamAng), gCamHeight, 5 *
              np.cos(gCamAng), 0, 0, 0, 0, 1, 0)
    # provided code - lighting, shading
    glEnable(GL_NORMALIZE)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    lightPos = (3., 4., 5., 1.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
    ambientLightColor = (.1, .1, .1, 1.)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)
    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    # added code - lighting, shading
    glLightfv(GL_LIGHT0, GL_DIFFUSE, gLightCol)
    glLightfv(GL_LIGHT0, GL_SPECULAR, gLightCol)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, gObjCol)
    # drawing

    glDrawElements(GL_TRIANGLES, 36, GL_UNSIGNED_INT, iarr)


def key_callback(window, key, scancode, action, mods):
    global gCamAng, gCamHeight, gLightCol, gObjCol, flag
    if action == glfw.PRESS or action == glfw.REPEAT:
        # camera ctrls
        if key == glfw.KEY_1:
            gCamAng += np.radians(-10)
        elif key == glfw.KEY_3:
            gCamAng += np.radians(10)
        elif key == glfw.KEY_2:
            gCamHeight += .1
        elif key == glfw.KEY_W:
            gCamHeight += -.1
    if action == glfw.PRESS:
        # obj color ctrls
        if key == glfw.KEY_R:  # R
            if flag == 1:
                gObjCol = R
                flag = 0
            else:
                gObjCol = W
                flag = 1
        elif key == glfw.KEY_G:  # G
            if flag == 1:
                gObjCol = G
                flag = 0
            else:
                gObjCol = W
                flag = 1
        elif key == glfw.KEY_B:  # B
            if flag == 1:
                gObjCol = B
                flag = 0
            else:
                gObjCol = W
                flag = 1


def main():
    global gVertexArraySeparate, gIndexArraySeparate
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
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    gVertexArrayseperate = create_varr()
    gIndexArraySeparate = create_iarr()
    while not glfw.window_should_close(window):
        glfw.wait_events()

        # render
        render()

        glfw.swap_buffers(window)
    glfw.terminate()

    return 0


if __name__ == "__main__":
    main()
