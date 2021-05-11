from re import match, split
import os
import numpy as np
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

    def get_input(self,window):
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

### global vars ###
# mesh
drop_mesh = Mesh()
filepath = None
# window height
height = 720
# camera
cam1 = Camera()
# render params
wireframe = True
# hirearchical model animation mode toggle
hmode = True


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

# zoom scroll
def scrollCB(window, xoffset, yoffset):
    global cam1
    cam1.zoom -= cam1.zoomsens * yoffset

# file drop
def fileparse(window, paths):
    global drop_mesh, filepath
    filepath = paths[0]
    drop_mesh = parse_obj(filepath)
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

### PARSING ###
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
script_dir = os.path.dirname(__file__)
# island
island_file = os.path.join(script_dir, 'resources/0-island.obj')
island_mesh = parse_obj(island_file)
# mill
mill_file = os.path.join(script_dir, 'resources/1-mill.obj')
mill_mesh = parse_obj(mill_file)
# propeller
prop_file = os.path.join(script_dir, 'resources/2-propeller.obj')
prop_mesh = parse_obj(prop_file)
# island_mesh = parse_obj(
#     'D:\\DRIVE\\SCHOOL\\CSE4020-CGI\\repos\\2021_cse4020_2018014275\\ClassAssignment2\\0-island.obj')
# mill_mesh = parse_obj(
#     'D:\\DRIVE\\SCHOOL\\CSE4020-CGI\\repos\\2021_cse4020_2018014275\\ClassAssignment2\\1-mill.obj')
# prop_mesh = parse_obj(
#     'D:\\DRIVE\\SCHOOL\\CSE4020-CGI\\repos\\2021_cse4020_2018014275\\ClassAssignment2\\2-propeller.obj')


### render ###
def render(window, camera, mesh):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)

    ### camera ###
    eye = camera.eye
    center = camera.center
    # projection
    if camera.PROJMODE:
        gluPerspective(camera.fov, camera.aspRatio, 0.1, 1000.0)
    else:
        glOrtho(-10, 10, -10, 10, -10, 10)
    # view
    gluLookAt(eye[0], eye[1], eye[2],
              center[0], center[1], center[2],
              0.0, 1.0, 0.0)
    
    ### drawing ###
    # draw grid
    drawGrid(50.0, 2.0, [96, 96, 96], 10.0, [192, 192, 192])
    # draw axes
    drawAxes(50.0)
    # draw obj
    glColor3ub(127, 255, 255)
    if filepath != None and hmode == False:
        drawmesh(mesh)
    elif hmode == True:
        t = glfw.get_time()
        sin1 = np.sin(1.5*t)
        sin2 = np.sin(3.7*t)
        s2 = 1 + abs(sin2 * 0.05)
        glRotatef(-90, 1, 0, 0)
        glScalef(0.5, 0.5, 0.5)
        # island
        glPushMatrix()
        glRotatef(-20*t, 0, 0, 1)
        glTranslatef(0, 0, 50+10*sin1)
        glTranslatef(0, 70, 0)
        drawmesh(island_mesh)
        # mill
        glPushMatrix()
        glScalef(s2, s2, s2)
        drawmesh(mill_mesh)
        # propeller
        glPushMatrix()
        glTranslatef(0, 20, 50)
        glRotatef(90, 0, 1, 0)
        glPushMatrix()
        glRotatef(400*t, 0, 0, 1)
        drawmesh(prop_mesh)
        glPopMatrix()
        glPopMatrix()
        glPopMatrix()
        glPopMatrix()
    return

# draw mesh
def drawmesh(p_mesh):
    glVertexPointer(3, GL_FLOAT, 3*p_mesh.vpos.itemsize, p_mesh.vpos)
    glNormalPointer(GL_FLOAT, 12, p_mesh.vnorm)
    indices = np.ravel(p_mesh.ibuff[:, 0:3])
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, indices)

### lighting ###
def light(light_id, lightPos, lightCol):
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    glEnable(light_id)
    glLightfv(light_id, GL_POSITION, lightPos)
    ambientLightColor = (.1, .1, .1, 1.)
    glLightfv(light_id, GL_AMBIENT, ambientLightColor)
    glLightfv(light_id, GL_DIFFUSE, lightCol)
    glLightfv(light_id, GL_SPECULAR, lightCol)


def main():
    global wireframe
    if not glfw.init():
        print("glfw: failed to init")
        return -1
    window = glfw.create_window(
        int(height * cam1.aspRatio), height, "obj Viewer", None, None)
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
        cam1.get_input(window)
        cam1.update()
        if wireframe:
            glDisable(GL_LIGHTING)
            glDisable(GL_DEPTH_TEST)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT, GL_FILL)
            glMaterialfv(GL_FRONT, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
            glMaterialfv(GL_FRONT, GL_SHININESS, 10)
            glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE,
                         (0.9, 0.9, 0.8, 1.0))
            light(GL_LIGHT0, (-400, 500, 0, 1), (0.7, 0.5, 0.9, 1.0))
            light(GL_LIGHT1, (1000, 500, 0, 1), (0.95, 0.9, 0.6, 1.0))
        # render
        render(window, cam1, drop_mesh)

        glfw.swap_buffers(window)
    print('goodbye!')
    glfw.terminate()
    return 0


if __name__ == "__main__":
    main()
