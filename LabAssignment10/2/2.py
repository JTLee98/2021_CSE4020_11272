import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from numpy import linalg
from OpenGL.arrays import vbo


### vector tools ###
# get vect length
def vmag(vec):
    return linalg.norm(vec)
# get angle between vecs
def vang(vec1, vec2):
    return np.arccos(np.dot(vec1,vec2) / vmag(vec1)*vmag(vec2))


# normalize vect
def vnorm(vec):
    return vec / vmag(vec)

# convert rotation matrix to rotation vector
def rota_mat2vec(R):
    v0 = np.array([1,0,0,0])
    v1 = R @ v0
    theta = vang(v0,v1)
    axis = vnorm(np.cross(v0[:3],v1[:3])) 
    out_vec = np.zeros(4)
    out_vec[:3] = theta*axis
    return out_vec


# convert rotation vector to rotation matrix
def rota_vec2mat(vec):
    angle = vmag(vec)
    axis = vnorm(vec)[:3]
    cos = np.cos(angle)
    sin = np.sin(angle)
    R = np.identity(3)
    # compute rotation matrix R (3x3)
    # R =  I * cos
    #    + (cross prod matx of u) * sin
    #    + (outer prod u x u) * (1-cos)
    R = cos * R + sin * np.cross(axis, -1 * R) + (1-cos) * np.outer(axis, axis)
    # convert to homogeneous 4x4
    out = np.identity(4)
    out[0:3, 0:3] = R
    return out

### spherical LERP ###
def slerp(R1, R2, t):
    if t == 0.0: 
        return R1
    elif t <= 1.0:
        return R1 @ rota_vec2mat(t * rota_mat2vec(R1.T @ R2))
    else:
        return R2


### general rotation matrix (affine homo 4x4) ###
def rotation(angle_rad, x, y, z):
    cos = np.cos(angle_rad)
    sin = np.sin(angle_rad)
    u = vnorm(np.array([x, y, z])) # axis
    R = np.identity(3)
    # compute rotation matrix R (3x3)
    # R =  I * cos
    #    + (cross prod matx of u) * sin
    #    + (outer prod u x u) * (1-cos)
    R = cos * R + sin * np.cross(u, -1 * R) + (1-cos) * np.outer(u, u)
    # convert to homogeneous 4x4
    out = np.identity(4)
    out[0:3, 0:3] = R
    return out

# rotation by euler angles
def rotation_euler(x,y,z):
    th = np.deg2rad([x,y,z])
    return rotation(th[2], 0,0,1) @ rotation(th[1], 0,1,0) @ rotation(th[0], 1,0,0) 


# globals 
gCamAng = 0.
gCamHeight = 1.
objCol = (1., 1., 1., 1.)
endpoint = np.zeros(3)
f = 0
# R1, R2
keyf1 = (rotation_euler(20,30,30),
      rotation_euler(45,60,40),
      rotation_euler(60,70,50),
      rotation_euler(80,85,70))
keyf2 = (rotation_euler(15,30,25),
      rotation_euler(25,40,40),
      rotation_euler(40,60,50),
      rotation_euler(55,80,65))

def createVertexAndIndexArrayIndexed():
    varr = np.array([
        (-0.5773502691896258, 0.5773502691896258,  0.5773502691896258),
        (-1,  1,  1),  # v0
        (0.8164965809277261, 0.4082482904638631,  0.4082482904638631),
        (1,  1,  1),  # v1
        (0.4082482904638631, -0.4082482904638631,  0.8164965809277261),
        (1, -1,  1),  # v2
        (-0.4082482904638631, -0.8164965809277261,  0.4082482904638631),
        (-1, -1,  1),  # v3
        (-0.4082482904638631, 0.4082482904638631, -0.8164965809277261),
        (-1,  1, -1),  # v4
        (0.4082482904638631, 0.8164965809277261, -0.4082482904638631),
        (1,  1, -1),  # v5
        (0.5773502691896258, -0.5773502691896258, -0.5773502691896258),
        (1, -1, -1),  # v6
        (-0.8164965809277261, -0.4082482904638631, -0.4082482904638631),
        (-1, -1, -1),  # v7
    ], 'float32')
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
        (0, 4, 7),
    ])
    return varr, iarr


def drawCube_glDrawElements():
    global gVertexArrayIndexed, gIndexArray
    varr = gVertexArrayIndexed
    iarr = gIndexArray
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize,
                    ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawElements(GL_TRIANGLES, iarr.size, GL_UNSIGNED_INT, iarr)


def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([3., 0., 0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([0., 3., 0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0., 0., 0]))
    glVertex3fv(np.array([0., 0., 3.]))
    glEnd()


def render(t):
    global gCamAng, gCamHeight, objCol, vel, endpoint, R1, R2, f
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 1, 10)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(5*np.sin(gCamAng), gCamHeight, 5 *
              np.cos(gCamAng), 0, 0, 0, 0, 1, 0)

    # draw global frame
    drawFrame()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glEnable(GL_RESCALE_NORMAL)

    lightPos = (3., 4., 5., 1.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)

    lightColor = (1., 1., 1., 1.)
    ambientLightColor = (.1, .1, .1, 1.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)

    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objCol)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    # update frame number f (cycle from 0 to 59)
    if f == 59: f = 0
    else: f += 1
    # tweening R1, R2 with slerp 
    if f < 20: 
        R1 = slerp(keyf1[0], keyf1[1], (f - 0)/20.0)
        R2 = slerp(keyf2[0], keyf2[1], (f - 0)/20.0)
        if f == 0: objCol = (1., 0., 0., 1.)
        # else: objCol = (1., 1., 1., 1.)
    elif f >= 20 and f < 40: 
        R1 = slerp(keyf1[1], keyf1[2], (f - 20)/20.0)
        R2 = slerp(keyf2[1], keyf2[2], (f - 20)/20.0)
        if f == 20: objCol = (0., 1., 0., 1.)
        # else: objCol = (1., 1., 1., 1.)
    elif f >= 40 and f < 60: 
        R1 = slerp(keyf1[2], keyf1[3], (f - 40)/20.0)
        R2 = slerp(keyf2[2], keyf2[3], (f - 40)/20.0) 
        if f == 40: objCol = (0., 0., 1., 1.)
        # else: objCol = (1., 1., 1., 1.)

    
    # transform & draw    
    J1 = R1
    # J1
    glPushMatrix()
    glMultMatrixf(J1.T)
    # L1
    glPushMatrix()
    glTranslatef(0.5, 0, 0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()

    T1 = np.identity(4)
    T1[0][3] = 1.  # translate by (+1,0,0)
    J2 = R1 @ T1 @ R2

    glPushMatrix()
    glMultMatrixf(J2.T)
    glPushMatrix()
    glTranslatef(0.5, 0, 0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()

    # computing endpoint and velocity
    pre_endpoint = endpoint
    cur_endpoint =  (J2 @ np.array([1.,0.,0.,1.]))[:3]
    vel = 10 * (cur_endpoint - pre_endpoint)
    endpoint = cur_endpoint
    # drawing vel arrow
    glDisable(GL_LIGHTING)
    glBegin(GL_LINES)
    glColor3ub(255,255,127)
    glVertex3fv(endpoint)
    glVertex3fv(endpoint+vel)
    glEnd()



def key_callback(window, key, scancode, action, mods):
    global gCamAng, gCamHeight
    # rotate the camera when 1 or 3 key is pressed or repeated
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_1:
            gCamAng += np.radians(-10)
        elif key == glfw.KEY_3:
            gCamAng += np.radians(10)
        elif key == glfw.KEY_2:
            gCamHeight += .1
        elif key == glfw.KEY_W:
            gCamHeight += -.1


gVertexArrayIndexed = None
gIndexArray = None


def main():
    global gVertexArrayIndexed, gIndexArray
    if not glfw.init():
        return
    window = glfw.create_window(640, 640, '2018014275', None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.swap_interval(1)

    gVertexArrayIndexed, gIndexArray = createVertexAndIndexArrayIndexed()

    while not glfw.window_should_close(window):
        glfw.poll_events()

        t = glfw.get_time()
        render(t)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
