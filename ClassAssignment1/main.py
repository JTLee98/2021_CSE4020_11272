import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

### Camera class ###
# contains view transform params
# and input handling
class Camera:
    def __init__(self):
        # control sensitivity (const)
        self.LMBsens = 0.005
        self.RMBsens = 0.001
        self.zoomsens = 0.5
        # view projection params
        self.fov = 50.0
        self.aspRatio = 1
        self.PROJMODE = True
        self.az = np.deg2rad(45.0)
        self.ev = np.deg2rad(37.0)
        self.panU = 0.0
        self.panV = 0.0
        self.zoom = 5.0
        # camera position
        self.eye = np.array([3.0, 3.0, 3.0])
        self.center = np.zeros(3)
        # misc input value buffers
        self.LMBbuff = True
        self.azbuff = 0.0
        self.evbuff = 0.0
        self.RMBbuff = True
        self.panUbuff = 0.0
        self.panVbuff = 0.0
        return

    def input(self,window):
        if glfw.get_key(window, glfw.KEY_0) == glfw.PRESS:
            self.az = np.deg2rad(45.0)
            self.ev = np.deg2rad(37.0)
            self.panU = 0.0
            self.panV = 0.0
            self.zoom = 5.0
        if glfw.get_key(window, glfw.KEY_V) == glfw.PRESS:
            self.PROJMODE = not self.PROJMODE
        if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            if self.LMBbuff:
                self.azbufftemp = self.RMBsens * \
                    -float(glfw.get_cursor_pos(window)[0])
                self.evbufftemp = self.RMBsens * \
                    float(glfw.get_cursor_pos(window)[1])
                self.LMBbuff = False
            else:
                self.az = self.azbuff - self.azbufftemp + self.RMBsens * - \
                    float(glfw.get_cursor_pos(window)[0])
                self.ev = self.evbuff - self.evbufftemp + self.RMBsens * \
                    float(glfw.get_cursor_pos(window)[1])
        elif glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.RELEASE:
            self.azbuff = self.az
            self.evbuff = self.ev
            self.LMBbuff = True
        if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS:
            if self.RMBbuff:
                self.panUbufftemp = self.LMBsens * \
                    -float(glfw.get_cursor_pos(window)[0])
                self.panVbufftemp = self.LMBsens * \
                    float(glfw.get_cursor_pos(window)[1])
                self.RMBbuff = False
            else:
                self.panU = self.panUbuff - self.panUbufftemp + self.LMBsens * - \
                    float(glfw.get_cursor_pos(window)[0])
                self.panV = self.panVbuff - self.panVbufftemp + self.LMBsens * \
                    float(glfw.get_cursor_pos(window)[1])
        elif glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT) == glfw.RELEASE:
            self.panUbuff = self.panU
            self.panVbuff = self.panV
            self.RMBbuff = True
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.terminate()
            return
    def update(self):
        # update view params
        az = self.az
        ev = self.ev
        # calculate camera frame
        u = np.array([np.cos(az), 0, -np.sin(az)])
        v = np.array([-np.sin(ev) * np.sin(az),
                    np.cos(ev),
                    -np.sin(ev) * np.cos(az)])
        w = np.array([np.cos(ev) * np.sin(az),
                    np.sin(ev),
                    np.cos(ev) * np.cos(az)])
        self.center = self.panU * u + self.panV * v
        self.eye = self.zoom * w + self.center
        return


### global vars
# window height
height = 720
# camera
cam = Camera()

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

# zoom scroll
def scrollCB(window, xoffset, yoffset):
    global cam
    cam.zoom -= cam.zoomsens * yoffset

### render ###
def render(cam):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    ### view (cam) ###
    # projection
    if cam.PROJMODE:
        gluPerspective(cam.fov, cam.aspRatio, 0.1, 100.0)
    else:
        glOrtho(-10, 10, -10, 10, -10, 10)
    gluLookAt(cam.eye[0], cam.eye[1], cam.eye[2],
              cam.center[0], cam.center[1], cam.center[2],
              0.0, 1.0, 0.0)
    ### drawing ###
    # draw grid
    drawGrid(5.0, 0.2, 1.0)
    # draw axes
    drawAxes(3.0)
    return


def main():
    if not glfw.init():
        print("glfw: failed to init")
        return -1
    window = glfw.create_window(
        int(height * cam.aspRatio), height, "Simple Viewer", None, None)
    if not window:
        glfw.terminate()
        return -1
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_scroll_callback(window, scrollCB)

    while not glfw.window_should_close(window):
        glfw.wait_events()
        cam.input(window)
        cam.update()
        # render
        render(cam)
        glfw.swap_buffers(window)
    glfw.terminate()
    return 0


if __name__ == "__main__":
    main()
