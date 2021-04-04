import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *


### global vars
# perspective
fov = 50.0  # y axis, in degrees
aspRatio = 16/9  # = width/height
# window height
height = 720
# true = perspective / false = ortho
PROJMODE = True
# control sensitivity (const)
LMBsens = 0.005
RMBsens = 0.001
zoomsens = 0.5
# camera params
az = np.deg2rad(45.0)
ev = np.deg2rad(37.0)
panU = 0.0
panV = 0.0
zoom = 5.0
# view params
eye = np.array([3.0, 3.0, 3.0])
center = np.zeros(3)

# geometry draw funcs


def drawGrid(gSize, gStepMin, gStepMaj):
    glBegin(GL_LINES)
    glColor3ub(127, 127, 127)
    for i in np.arange(-gSize, gSize+gStepMin, gStepMin):
        glVertex3f(i, 0.0, -gSize)
        glVertex3f(i, 0.0,  gSize)
        glVertex3f(-gSize, 0.0, i)
        glVertex3f(gSize, 0.0, i)
    glColor3ub(255, 255, 255)
    for i in np.arange(-gSize, gSize+gStepMaj, gStepMaj):
        glVertex3f(i, 0.0, -gSize)
        glVertex3f(i, 0.0,  gSize)
        glVertex3f(-gSize, 0.0, i)
        glVertex3f(gSize, 0.0, i)
    glEnd()
    return


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

# camera


def update_cam():
    global ev, az, panU, panV, zoom, center, eye
    # calculate camera frame

    u = np.array([np.cos(az), 0, -np.sin(az)])
    v = np.array([-np.sin(ev) * np.sin(az),
                  np.cos(ev),
                  -np.sin(ev) * np.cos(az)])
    w = np.array([np.cos(ev) * np.sin(az),
                  np.sin(ev),
                  np.cos(ev) * np.cos(az)])
    center = panU * u + panV * v
    eye = zoom * w + center
    return

# zoom scroll


def scrollCB(window, xoffset, yoffset):
    global zoom, zoomsens
    zoom -= zoomsens * yoffset

# render


def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    ### view (cam)
    # projection
    if PROJMODE:
        gluPerspective(fov, aspRatio, 0.1, 100.0)
    else:
        glOrtho(-10, 10, -10, 10, -10, 10)
    gluLookAt(eye[0], eye[1], eye[2],
              center[0], center[1], center[2],
              0.0, 1.0, 0.0)
    # drawing

    # draw grid
    drawGrid(5.0, 0.2, 1.0)
    # draw axes
    drawAxes(3.0)

    return


def main():
    global fov, aspRatio, height, PROJMODE
    global LMBsens, RMBsens, zoomsens
    global ev, az, panU, panV, zoom, center, eye
    if not glfw.init():
        print("glfw: failed to init")
        return -1
    window = glfw.create_window(
        int(height * aspRatio), height, "Simple Viewer", None, None)
    if not window:
        glfw.terminate()
        return -1
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_scroll_callback(window, scrollCB)

    LMBbuff = True
    azbuff = 0.0
    evbuff = 0.0
    RMBbuff = True
    panUbuff = 0.0
    panVbuff = 0.0
    while not glfw.window_should_close(window):
        glfw.wait_events()
        # input handling
        if glfw.get_key(window, glfw.KEY_0) == glfw.PRESS:
            az = np.deg2rad(45.0)
            ev = np.deg2rad(37.0)
            panU = 0.0
            panV = 0.0
            zoom = 5.0
        if glfw.get_key(window, glfw.KEY_V) == glfw.PRESS:
            PROJMODE = not PROJMODE
        if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            if LMBbuff:
                azbufftemp = RMBsens * \
                    -float(glfw.get_cursor_pos(window)[0])
                evbufftemp = RMBsens * \
                    float(glfw.get_cursor_pos(window)[1])
                LMBbuff = False
            else:
                az = azbuff - azbufftemp + RMBsens * - \
                    float(glfw.get_cursor_pos(window)[0])
                ev = evbuff - evbufftemp + RMBsens * \
                    float(glfw.get_cursor_pos(window)[1])
        elif glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.RELEASE:
            azbuff = az
            evbuff = ev
            LMBbuff = True
        if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS:
            if RMBbuff:
                panUbufftemp = LMBsens * \
                    -float(glfw.get_cursor_pos(window)[0])
                panVbufftemp = LMBsens * \
                    float(glfw.get_cursor_pos(window)[1])
                RMBbuff = False
            else:
                panU = panUbuff - panUbufftemp + LMBsens * - \
                    float(glfw.get_cursor_pos(window)[0])
                panV = panVbuff - panVbufftemp + LMBsens * \
                    float(glfw.get_cursor_pos(window)[1])
        elif glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT) == glfw.RELEASE:
            panUbuff = panU
            panVbuff = panV
            RMBbuff = True
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            break

        update_cam()

        # render
        render()
        glfw.swap_buffers(window)
    glfw.terminate()
    return 0


if __name__ == "__main__":
    main()
