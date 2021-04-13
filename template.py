import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

gCamAng = 0.0
gCamHeight = 0.0


def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()


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
    # glfw.set_key_callback(window, key_callback)
    glEnable(GL_DEPTH_TEST | GL_NORMALIZE)
    glEnableClientState(GL_VERTEX_ARRAY)
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    while not glfw.window_should_close(window):
        glfw.wait_events()

        # render
        render()

        glfw.swap_buffers(window)
    glfw.terminate()

    return 0


if __name__ == "__main__":
    main()
