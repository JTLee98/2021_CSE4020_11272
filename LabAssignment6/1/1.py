import numpy as np
import glfw
from numpy import linalg
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.error import *

varr = np.array([(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1),
                (0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)], dtype=np.float32)
iarr = np.array([
    (0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (3, 2, 6, 7)], dtype=np.uint32)


# gluLookAt()
def myLookAt(eye, at, up):
    # exception handling
    # if up is parallel to look direction
    if linalg.matrix_rank(np.stack([(eye-at), up])) < 2:
        raise linalg.LinAlgError(
            'ERROR myLookAt(): up cannot be parallel to line of sight')

    # calculate matrix Mlook
    up = up/linalg.norm(up)
    f = (at - eye)/linalg.norm(at-eye)
    u = np.cross(np.cross(f, up), f)
    Mlook = np.identity(4)
    Mlook[0, 0:3] = np.cross(f, up)
    Mlook[1, 0:3] = u
    Mlook[2, 0:3] = -f
    glMatrixMode(GL_PROJECTION)
    glMultMatrixf(Mlook.T)
    glTranslatef(-eye[0], -eye[1], -eye[2])
    return

# glFrustum()


def myFrustum(left, right, bottom, top, near, far):
    # error handling
    if near <= 0 or far <= 0:
        raise GLerror(err=GL_INVALID_VALUE,
                      description='ERROR myFrustum: near and far values must be positive')
    elif left == right:
        raise GLerror(err=GL_INVALID_VALUE,
                      description='ERROR myFrustum: left and right values cannot be equal')
    elif bottom == top:
        raise GLerror(err=GL_INVALID_VALUE,
                      description='ERROR myFrustum: bottom and top values cannot be equal')
    elif near == far:
        raise GLerror(err=GL_INVALID_VALUE,
                      description='ERROR myFrustum: near and far values values cannot be equal')
    else:
        Mp = np.array([[2*near/(right-left), 0, (right+left)/(right-left),  0],
                       [0, 2*near/(top-bottom), (top+bottom) /
                        (top-bottom),  0],
                       [0, 0, (far+near)/(near-far),
                        2*far*near/(near-far)],
                       [0, 0, -1, 0]], dtype=np.float32)
        glMatrixMode(GL_PROJECTION)
        glMultMatrixf(Mp.T)
        return


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


def drawCubeArray():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                glPushMatrix()
                glTranslatef(i, j, -k-1)
                glScale(0.5, 0.5, 0.5)
                glVertexPointer(3, GL_FLOAT, 12, varr)
                glDrawElements(GL_QUADS, 16, GL_UNSIGNED_INT, iarr)
                glPopMatrix()


def render():
    global varr, iarr
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    # glFrustum(-1, 1, -1, 1, 1, 10)
    myFrustum(-1, 1, -1, 1, 1, 10)
    # gluLookAt(5, 3, 5, 1, 1, -1, 0, 1, 0)
    myLookAt(np.array([5, 3, 5]), np.array([1, 1, -1]), np.array([0, 1, 0]))
    drawFrame(1.0, np.array([255, 0, 0]), np.array(
        [0, 255, 0]), np.array([0, 0, 255]))
    # draw cube array
    glColor3ub(255, 255, 255)
    drawCubeArray()


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
    glEnableClientState(GL_VERTEX_ARRAY)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    while not glfw.window_should_close(window):
        glfw.wait_events()
        # render
        render()

        glfw.swap_buffers(window)
    glfw.terminate()

    return 0


if __name__ == "__main__":
    main()
