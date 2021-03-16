import numpy as np
import glfw
from OpenGL.GL import *


def render(T):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    # draw cooridnate
    glBegin(GL_LINES)
    glColor3ub(255,0,0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([1.,0.]))
    glColor3ub(0,255,0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([0.,1.]))
    glEnd()
    # draw triangle
    glBegin(GL_TRIANGLES)
    glColor3ub(255,255,255)
    glVertex2fv( (T @np.array([.0,.5,1.]))[:-1] )
    glVertex2fv( (T @np.array([.0,.0,1.]))[:-1] )
    glVertex2fv( (T @np.array([.5,.0,1.]))[:-1] )
    glEnd()

# homogeneous tranform matrices
def Identity2d():
    return np.array([[1., 0., 0.],
                    [0., 1., 0.],
                    [0., 0., 1.]])
def scale2d(self,x,y):
    return np.array([[x,  0., 0.],
                    [0., y,  0.],
                    [0., 0., 1.]])
def rotate2d(theta):
    return np.array([[np.cos(theta), -np.sin(theta), 0.],
                    [np.sin(theta),  np.cos(theta), 0.],
                    [0.           ,  0.           , 1.]])
def transl2d(x,y):
    return np.array([[1., 0., x ],
                    [0., 1., y ],
                    [0., 0., 1.]])


def main():
    # glfw stuff
    if not glfw.init():
        return
    window = glfw.create_window(480, 480, "2018014275", None,None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_time(0)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        # get time t (in seconds)

        t = glfw.get_time()
        # make transform matrix T
        T = Identity2d()    
        # render
        render(T @ rotate2d(t) @ transl2d(0., 0.5))
        
        glfw.swap_buffers(window)
    glfw.terminate()

if __name__ == "__main__":
    main()