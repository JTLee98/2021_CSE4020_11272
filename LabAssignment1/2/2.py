import numpy as np
import glfw
from OpenGL.GL import *

theta = np.linspace(0, 2 * np.pi, 13)[:-1]
vposbuff = np.vstack([np.cos(theta), np.sin(theta)]).T

clock_idx = 3 #vpos index for clock time
def update_clock(key):
    global clock_idx
    if key >= glfw.KEY_1 and key <= glfw.KEY_3: #1 to 3
        clock_idx = 3 - (key - glfw.KEY_0)
    elif key == glfw.KEY_Q: #Q
        clock_idx = 4
    elif key == glfw.KEY_W: #W
        clock_idx = 3    
    elif key == glfw.KEY_0: #zero
        clock_idx = 5
    elif key >= glfw.KEY_1 and key <= glfw.KEY_9: #4 to 9
        clock_idx = 15 - (key - glfw.KEY_0)
    else:
        return
    print(clock_idx)

def key_callback(window, key, scancode, action, mods):
    if action==glfw.PRESS:
        update_clock(key)

def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(GL_LINE_LOOP)
    for i in range(12):
        glVertex2fv(vposbuff[i])
    glEnd()
    glBegin(GL_LINES)
    glVertex2f(0.0, 0.0)
    glVertex2fv(vposbuff[clock_idx])
    glEnd()
    

def main():
    # Initialize the library
    if not glfw.init():
        return
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(480, 480, "2018014275", None,None)
    if not window:
        glfw.terminate()
        return
    #set key callback func
    glfw.set_key_callback(window, key_callback)

    # Make the window's context current
    glfw.make_context_current(window)

    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Poll events
        glfw.wait_events()

        # Render here, e.g. using pyOpenGL
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        glBegin(GL_LINE_LOOP)
        for i in range(12):
            glVertex2fv(vposbuff[i])
        glEnd()
        glBegin(GL_LINES)
        glVertex2f(0.0, 0.0)
        glVertex2fv(vposbuff[clock_idx])
        glEnd()
        #render()

        # Swap front and back buffers
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()

