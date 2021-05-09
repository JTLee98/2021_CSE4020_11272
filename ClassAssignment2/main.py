import numpy as np
from re import match, split
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

### mesh class ###


class Mesh:
    def __init__(self):
        # ### Mesh hierarchy (tree) ###
        # self.parent = None
        # self.children = []

        ### obj mesh ###
        # vertex data
        self.vpos = np.empty([0, 3], dtype=np.float32)  # pos coords (x,y,z)[]
        self.vtex = np.empty([0, 3], dtype=np.float32)  # tex coords (x,y,z)[]
        self.vnorm = np.empty([0, 3], dtype=np.float32)  # normals (x,y,z)[]

        # index buffer: 9-col numpy array
        # with each row = one triangle face
        # face [position | texture     | normal     ]
        # [ f0 = [v1,v2,v3,  vt1,vt2,vt3,  vn1,vn2,vn3]
        #   f1 = [v1,v2,v3,  vt1,vt2,vt3,  vn1,vn2,vn3]
        #   ...
        #   fn = [v1,v2,v3,  vt1,vt2,vt3,  vn1,vn2,vn3]  ]
        self.ibuff = np.empty(shape=(0, 9), dtype=np.uint32)
        self.poly_count = 0
        # dict of poly stats (indices: number of faces)
        self.poly_stats = {}
        # other vars
        self.name = None
        self.filepath = None
        # self.group = None
        self.mtllib = None
        self.warnings = []
        self.errors = []

    def exception(self, level, line_number, type, line):
        err = {'line#': line_number, 'type': type, 'line': line}
        if level == 'warning':
            self.warnings.append(err)
        elif level == 'error':
            self.errors.append(err)
        return f'{line} --> {level}: {type}'

    def append_ibuff(self, ibuff):
        # each face row is formatted as
        # np.array([v1,v2,v3, vt1,vt2,vt3, vn1,vn2,vn3]
        #           dtype=np.uint32)
        self.ibuff = np.vstack((self.ibuff, ibuff))
        self.poly_count += ibuff.shape[0]


### global vars ###
# mesh
mesh = Mesh()
filepath = None
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
# buffer vars etc
LMBbuff = True
azbuff = 0.0
evbuff = 0.0
RMBbuff = True
panUbuff = 0.0
panVbuff = 0.0
panUbufftemp = 0.0
panVbufftemp = 0.0
azbufftemp = 0.0
evbufftemp = 0.0
# render params
wireframe = False
# hirearchical model animation mode toggle
hmode = False


# geometry draw funcs
def drawGrid(size, MinStep, MinColor, MajStep, MajColor):
    glBegin(GL_LINES)
    glColor3ubv(MinColor)
    for i in np.arange(-size, size+MinStep, MinStep):
        glVertex3f(i, 0.0, -size)
        glVertex3f(i, 0.0,  size)
        glVertex3f(-size, 0.0, i)
        glVertex3f(size, 0.0, i)
    glColor3ubv(MajColor)
    for i in np.arange(-size, size+MajStep, MajStep):
        glVertex3f(i, 0.0, -size)
        glVertex3f(i, 0.0,  size)
        glVertex3f(-size, 0.0, i)
        glVertex3f(size, 0.0, i)
    glEnd()
    return


def drawAxes(length):
    glPushMatrix()
    glScalef(length, length, length)
    glBegin(GL_LINES)
    glColor3ub(255, 16, 16)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(1.0, 0.0, 0.0)
    glColor3ub(16, 255, 16)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 1.0, 0.0)
    glColor3ub(16, 16, 255)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 1.0)
    glEnd()
    glPopMatrix()
    return

# camera


def update_cam(window):
    global ev, az, panU, panV, zoom, center, eye
    global LMBbuff, azbuff, evbuff, RMBbuff, panUbuff, panVbuff
    global panUbufftemp, panVbufftemp, azbufftemp, evbufftemp

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


# file drop
def fileparse(window, paths):
    global mesh, filepath
    filepath = paths[0]
    mesh = parse_obj(filepath)
    return

# keyboard commands


def kb_cmd(window, key, scancode, action, mods):
    global wireframe, hmode
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.terminate()
        elif key == glfw.KEY_Z:
            wireframe = not wireframe
        elif key == glfw.KEY_H:
            hmode = not hmode
        elif key == glfw.KEY_C:
            print('''------ commands ------
                - Z : toggle wireframe mode
                - S : toggle smooth shading
                - H : toggle hierarchical model animation mode
                - C : show this help dialogue
                - ESC : exit program''')

### parse function ###
# line printer for obj parser


def lineprint(line, number, max_digits):
    digits = len(str(number))
    if number == None:
        spacing = ' '*max_digits
    else:
        spacing = ' '*(max_digits-digits)
    print(f'{spacing}{number} | {line}')

# parse_obj() : takes obj file and returns a Mesh


def parse_obj(filepath):
    # open file
    if match(r'.*\.obj$', filepath) == None:
        print(f'filedrop error : {filepath} is not an obj file')
        return
    try:
        raw = open(filepath)
        text = raw.read()
    except OSError as err:
        print(err)
        return
    else:
        print(f'opened obj file {filepath}')

    # instantiate Mesh
    mesh = Mesh()
    mesh.filepath = filepath
    # parse file
    print('==============start parsing===============')
    lines = text.split('\n')
    i = 0
    max_digits = len(str(len(lines)))
    err = None
    for i in range(len(lines)):
        line = lines[i]
        if line == '':
            continue
        line_split = split(r' +', line)
        while '' in line_split:
            line_split.remove('')
        type = line_split[0]
        data = line_split[1:]
        data.index
        # mtl file
        if type == 'mtllib':
            if match(r'^.*\.mtl$', data[0]) == None:
                mesh.exception('error', i, 'mtl file extension', line)
                continue
            else:
                mesh.mtllib = str(data[0])
        # name data
        elif type == 'o':
            mesh.name = str(data[0])
        # vertex data (v, vn, vt)
        elif type == 'v':  # x,y,z
            data = np.array(data[:3], dtype=np.float32)
            mesh.vpos = np.vstack((mesh.vpos, data))
        elif type == 'vn':  # x,y,z
            data = np.array(data[:3], dtype=np.float32)
            mesh.vnorm = np.vstack((mesh.vnorm, data))
        elif type == 'vt':  # x,[y,z]
            data = np.array(data, dtype=np.float32)
            data.resize(3, refcheck=False)
            mesh.vtex = np.vstack((mesh.vtex, data))
        # index (face) data -> ibuff -> append to mesh.groups
        # groups are created with command 'g'
        elif type == 'f':
            n = len(data)
            # assume n-sided convex polygon
            #  ex) f v1 v2 ... vn
            #   or f v1/vt1 v3/vt2 ... vn/vtn
            #   or f v1/vt1/vn1 ... vn/vtn/vnn
            #   or f v1//vn1 ... vn//vnn
            # -> subdivide into n-2 triangle faces
            #    and stack faces into ibuff
            #    (ibuff is [n-2,9] array)
            ibuff = np.empty([0, 9], dtype=np.uint32)
            for j in range(n-2):
                # data_div is a single subdivided triangle
                # (i.e. len(data_div) = 3)
                # total data_divs in data = n-2
                data_div = [data[0], data[j+1], data[j+2]]
                face = np.zeros([9], dtype=np.uint32)
                # data_div is [v1, v2, v3]
                if match(r'\d+$', data_div[0]) != None:
                    face[0:3] = np.array(data_div, dtype=np.uint32)
                # data_div is [v1/vt1, v2/vt2, v3/vt3]
                elif match(r'\d+/\d+$', data_div[0]) != None:
                    for k in range(3):
                        temp = data_div[k].split('/')
                        face[0+k] += np.uint32(temp[0])  # v
                        face[3+k] += np.uint32(temp[1])  # vt
                # data_div is [v1/vt1/vn1, v2/vt2/vn2, v3/vt3/vn3]
                elif match(r'\d+/\d+/\d+$', data_div[0]) != None:
                    for k in range(3):
                        temp = data_div[k].split('/')
                        face[0+k] += np.uint32(temp[0])  # v
                        face[3+k] += np.uint32(temp[1])  # vt
                        face[6+k] += np.uint32(temp[2])  # vn
                # data_div is [v1//vn1, v2//vn2, v3//vn3]
                elif match(r'\d+//\d+$', data_div[0]) != None:
                    for k in range(3):
                        temp = data_div[k].split('//')
                        face[0+k] += np.uint32(temp[0])  # v
                        face[6+k] += np.uint32(temp[1])  # vn
                # wrong formatting
                else:
                    err = mesh.exception(
                        'error', i, 'wrong face formatting', line)
                    break
                # stack parsed face on ibuff
                ibuff = np.vstack((ibuff, face))
            # append stacked ibuff to mesh
            mesh.append_ibuff(ibuff)
            # update poly stats
            if mesh.poly_stats.get(n, False):
                mesh.poly_stats[n] += 1
            else:
                mesh.poly_stats[n] = 1

        # comment (#)
        elif type == '#' or ' ':
            spacing = ' '*max_digits
            print(f'{spacing}{i} | {line}')
            i += 1
            continue
        # exceptions
        else:
            err = mesh.exception('warning', i, 'unsupported formatting', line)
            i += 1
        ### finish ###
        # catch exceptions & print
        if err != None:
            spacing = ' '*(max_digits-1)
            print(f'{spacing}e | {err}')
            err = None
            i += 1
            continue
        # print line & increment i
        digits = int(np.log10(i))
        spacing = ' '*(max_digits-digits)
        print(f'{spacing}{i} | {line}')
        i += 1
    mesh.ibuff -= 1
    print(f'============finished parsing================')
    # infodump
    face_count = 0
    for f in mesh.poly_stats.items():
        print(f'{f[0]}-sided polygons = {f[1]}')
        face_count += f[1]
    print(f'--> total number of faces = {face_count}')
    print(f'    total number of triangles = {mesh.poly_count}')
    return mesh


### hmode meshes ###
# island
island_mesh = parse_obj('media/0-island.obj')
# mill
mill_mesh = parse_obj('media/1-mill.obj')
# propeller
mill_mesh = parse_obj('media/2-propeller.obj')


# render


def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glEnable(GL_NORMALIZE)

    ### view (cam)
    # projection
    if PROJMODE:
        gluPerspective(fov, aspRatio, 0.1, 1000.0)
    else:
        glOrtho(-10, 10, -10, 10, -10, 10)
    gluLookAt(eye[0], eye[1], eye[2],
              center[0], center[1], center[2],
              0.0, 1.0, 0.0)
    # drawing
    # draw grid
    drawGrid(50.0, 2.0, [96, 96, 96], 10.0, [192, 192, 192])
    # draw axes
    drawAxes(50.0)
    # draw obj
    glColor3ub(127, 255, 255)
    if filepath != None and hmode == False:
        drawmesh(mesh)
    elif hmode == True:
        t = glfw.get_time()/20
        sin1 = np.sin(t)
        sin2 = np.sin(2.3*t)
        glPushMatrix()
        glTranslatef(0, 10*sin1, 0)
        drawmesh(island_mesh)
        glPushMatrix()

        s2 = 1 + sin2*0.1
        glScalef(s2)
        return


def drawmesh(p_mesh):
    glVertexPointer(3, GL_FLOAT, 3*p_mesh.vpos.itemsize, p_mesh.vpos)
    glNormalPointer(GL_FLOAT, 12, p_mesh.vnorm)
    indices = np.ravel(p_mesh.ibuff[:, 0:3])
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, indices)


def main():
    global fov, aspRatio, height, PROJMODE
    global LMBsens, RMBsens, zoomsens
    global ev, az, panU, panV, zoom, center, eye
    global wireframe
    if not glfw.init():
        print("glfw: failed to init")
        return -1
    window = glfw.create_window(
        int(height * aspRatio), height, "obj Viewer", None, None)
    if not window:
        glfw.terminate()
        return -1
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_scroll_callback(window, scrollCB)
    glfw.set_drop_callback(window, fileparse)
    glfw.set_key_callback(window, kb_cmd)
    while not glfw.window_should_close(window):
        glfw.poll_events()

        update_cam(window)

        if wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT, GL_FILL)

        # render
        render()

        glfw.swap_buffers(window)
    print('goodbye!')
    glfw.terminate()
    return 0


if __name__ == "__main__":
    main()
