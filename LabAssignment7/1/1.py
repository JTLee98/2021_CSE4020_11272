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


def createVertexArraySeparate():
    varr = np.array([
        (0, 0, 1),         # v0 normal
        (-1,  1,  1),  # v0 position
        (0, 0, 1),         # v2 normal
        (1, -1,  1),  # v2 position
        (0, 0, 1),         # v1 normal
        (1,  1,  1),  # v1 position

        (0, 0, 1),         # v0 normal
        (-1,  1,  1),  # v0 position
        (0, 0, 1),         # v3 normal
        (-1, -1,  1),  # v3 position
        (0, 0, 1),         # v2 normal
        (1, -1,  1),  # v2 position

        (0, 0, -1),
        (-1,  1, -1),  # v4
        (0, 0, -1),
        (1,  1, -1),  # v5
        (0, 0, -1),
        (1, -1, -1),  # v6

        (0, 0, -1),
        (-1,  1, -1),  # v4
        (0, 0, -1),
        (1, -1, -1),  # v6
        (0, 0, -1),
        (-1, -1, -1),  # v7

        (0, 1, 0),
        (-1,  1,  1),  # v0
        (0, 1, 0),
        (1,  1,  1),  # v1
        (0, 1, 0),
        (1,  1, -1),  # v5

        (0, 1, 0),
        (-1,  1,  1),  # v0
        (0, 1, 0),
        (1,  1, -1),  # v5
        (0, 1, 0),
        (-1,  1, -1),  # v4

        (0, -1, 0),
        (-1, -1,  1),  # v3
        (0, -1, 0),
        (1, -1, -1),  # v6
        (0, -1, 0),
        (1, -1,  1),  # v2

        (0, -1, 0),
        (-1, -1,  1),  # v3
        (0, -1, 0),
        (-1, -1, -1),  # v7
        (0, -1, 0),
        (1, -1, -1),  # v6

        (1, 0, 0),
        (1,  1,  1),  # v1
        (1, 0, 0),
        (1, -1,  1),  # v2
        (1, 0, 0),
        (1, -1, -1),  # v6

        (1, 0, 0),
        (1,  1,  1),  # v1
        (1, 0, 0),
        (1, -1, -1),  # v6
        (1, 0, 0),
        (1,  1, -1),  # v5

        (-1, 0, 0),
        (-1,  1,  1),  # v0
        (-1, 0, 0),
        (-1, -1, -1),  # v7
        (-1, 0, 0),
        (-1, -1,  1),  # v3

        (-1, 0, 0),
        (-1,  1,  1),  # v0
        (-1, 0, 0),
        (-1,  1, -1),  # v4
        (-1, 0, 0),
        (-1, -1, -1),  # v7
    ], 'float32')
    return varr


def drawCube_glDrawArray():
    global gVertexArraySeparate
    varr = gVertexArraySeparate
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize,
                    ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawArrays(GL_TRIANGLES, 0, int(varr.size/6))


def render():
    global gCamAng, gCamHeight, gLightCol, gObjCol
    glEnable(GL_DEPTH_TEST)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # provided code - transforms
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
    # provided code - drawing
    drawCube_glDrawArray()


def key_callback(window, key, scancode, action, mods):
    global gCamAng, gCamHeight, gLightCol, gObjCol
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
        # light color ctrls
        elif key == glfw.KEY_A:  # R
            gLightCol = (1.0, 0.1, 0.1, 1.0)
        elif key == glfw.KEY_S:  # G
            gLightCol = (0.1, 1.0, 0.1, 1.0)
        elif key == glfw.KEY_D:  # B
            gLightCol = (0.1, 0.1, 1.0, 1.0)
        elif key == glfw.KEY_F:  # W
            gLightCol = (1.0, 1.0, 1.0, 1.0)
        # obj color ctrls
        elif key == glfw.KEY_Z:  # R
            gObjCol = (1.0, 0.1, 0.1, 1.0)
        elif key == glfw.KEY_X:  # G
            gObjCol = (0.1, 1.0, 0.1, 1.0)
        elif key == glfw.KEY_C:  # B
            gObjCol = (0.1, 0.1, 1.0, 1.0)
        elif key == glfw.KEY_V:  # W
            gObjCol = (1.0, 1.0, 1.0, 1.0)


gVertexArraySeparate = None


def main():
    global gVertexArraySeparate
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
    gVertexArraySeparate = createVertexArraySeparate()

    while not glfw.window_should_close(window):
        glfw.wait_events()

        # render
        render()

        glfw.swap_buffers(window)
    glfw.terminate()

    return 0


if __name__ == "__main__":
    main()
