from re import match, split
import parser as prs
import os
from sys import exit
import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt
from numpy.lib.function_base import append

### MESH class ###
class Mesh:
    def __init__(self,filepath:str):
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
        self.filepath = filepath
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
            self.fov = 50.0
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

### BVH joint class ###
class Joint():
    pass
class Joint():
    def __init__(self) -> None:
        self.name = None
        self.id = None
        self.parent = None
        self.children = []
        self.channels = {}
        self.offset = None
        self.pos = None
        return
    def __init__(self, name:str, id:int, parent:Joint, rotation:np.array, offset:np.array) -> None:
        self.name = name
        self.id = id
        self.parent = parent
        self.children = []
        self.rotation = rotation
        self.offset = offset
        self.pos = None
        return
    def set_root(self,position:np.array) -> None:
        self.id = 0
        self.parent = None
        self.pos = position
        return
    def add_child(self, child : Joint):
        self.children.append(child)
        return

### BVH class ###
class BVH:
    def __init__(self) -> None:
        self.filepath = None
        self.frames = 0
        self.fps = 0
        self.curframe = 0
        self.root = None
        self.Joints = {}
        self.channels = None
        self.motion_data = None
        return
    
    def set_root(self, root:Joint):
        self.root = root
        return

    # def set_anim() : get animation data
    # def 

    def update(self, time:float):
        self.curframe = int((time % (self.framecount*self.fps))*self.fps)
        # update channel values
        return
    
    # exceptions
    def exception(self, level, line_number, type, line):
        err = {'line#': line_number, 'type': type, 'line': line}
        if level == 'warning':
            self.warnings.append(err)
        elif level == 'error':
            self.errors.append(err)
        return f'{line} --> {level}: {type}'


### global vars ###
# dropped file
drop = None
filepath = None
# window height
height = 720
# camera
gCam = Camera()

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

### PARSING ###
# console output
def print_line(line, number, max_digits):
    digits = len(str(number))
    if number == None:
        spacing = ' '*max_digits
    else:
        spacing = ' '*(max_digits-digits)
    print(f'{spacing}{number} | {line}')

# parse_obj() : takes obj file and returns a Mesh
def parse_obj(filepath:str) -> Mesh:
    # open file
    try:
        raw = open(filepath)
        text = raw.read()
    except OSError as err:
        print(err)
        return
    else:
        print(f'opened obj file {filepath}')

    # instantiate Mesh
    mesh = Mesh(filepath)
    # parse file
    print(f'=====start parsing {os.path.basename(filepath)}=======')
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

# push new BVH joint on stack
def pushJoint(bvh:BVH ,parent:Joint, name:str, sub_HIER:list, ch:int, id:int):
    output = Joint()
    output.name = name
    output.parent = parent
    output.id = id
    bvh.Joints[id] = output
    # parse offset & channels
    o = sub_HIER.index('OFFSET')
    offset = [float(val) for val in sub_HIER[o+1:o+4]]
    output.offset = np.array(offset, dtype=np.float32) 
    c = sub_HIER.index('CHANNELS')
    n = int(sub_HIER[c+1])
    for channel in sub_HIER[c+2:c+2+n]:
        output.channels[channel] = ch
        ch += 1
    # separate subjoints by index
    subjoint_ranges = []
    joint = 0
    lv = 0
    for i in range(len(sub_HIER)):
        lv_prev = lv
        if match(r'JOINT', sub_HIER[i]) != None:
            lv += 1
            if lv == 1 and lv_prev == 0:
                joint += 1
                subjoint_ranges.append([i,0])
        elif match(r'}', sub_HIER[i]) != None:
            lv -= 1        
            if lv == 1 and lv_prev == 2:
                subjoint_ranges[joint][1] = i
    # add subjoints
    for r in subjoint_ranges:
        [start,end] = r
        output.add_child(pushJoint(output, sub_HIER[start+1],sub_HIER[start:end], ch))
    
    return output


# parse_bvh(): takes bvh file and returns
def parse_bvh(filepath:str) -> BVH:
    # open file
    try:
        raw = open(filepath)
        text = raw.read()
    except OSError as err:
        print(err)
        return
    else:
        print(f'opened bvh file {filepath}')
    # instantiate BVH
    outfile = BVH(filepath)
    err = None
    ### PARSE ###
    print(f'=====start parsing {os.path.basename(filepath)}=======')
    # split into HIERARCHY and MOTION
    temp = split(r'MOTION|HIERARCHY',text)
    for block in temp:
        if match(r'ROOT', block):
            Hierarchy = block
        elif match(r'Frames', block):
            Motion = block
    ### hierarchy ###
    HIER = Hierarchy.split(r'\s+')
    i = 0, ch = 0
    # root
    while match(r'ROOT', HIER[i]) == None: i += 1    
    Root = Joint()
    Root.name = HIER[i+1]
    i += 4
    Root.set_root(np.array([float(OFFSET) for OFFSET in HIER[i:i+3]]))
    i += 3
    while match(r'[XYZ](POSITION|ROTATION)', HIER[i]) != None:
        Root.channels[HIER[i]] = ch
        i += 1
        ch += 1
    # parse joints
    # separate lv 1 subjoints by index
    subjoint_ranges = []
    joint = 0
    lv = 0
    for i in range(len(HIER)):
        lv_prev = lv
        if match(r'JOINT', HIER[i]) != None:
            lv += 1
            if lv == 1 and lv_prev == 0:
                joint += 1
                subjoint_ranges.append([i,0])
        elif match(r'}', HIER[i]) != None:
            lv -= 1        
            if lv == 1 and lv_prev == 2:
                subjoint_ranges[joint][1] = i
    # add subjoints
    id = 1
    for r in subjoint_ranges:
        [start,end] = r
        newJoint = pushJoint(outfile, Root, HIER[start+1], HIER[start:end], ch, id)
        Root.add_child(newJoint)
        outfile.Joints[id] 
    
    ### motion ###
    lines = Motion.split('\n')
    outfile.frames = int(lines[0].removeprefix('Frames: '))
    outfile.fps = int(1/float(lines[1].removeprefix('Frame Time: ')))
    # convert into numpy array
    channel_count = len(split(r'\s+', lines[3]))
    channel_data = np.array([[float(val) for val in split(r'\s+',frame)] for frame in lines], dtype= np.float32)

    outfile.set_root(Root)
    outfile.motion_data = channel_data
    return outfile     


        
        
            





### CALLBACK FUNCS ###
# controls
controls = '''------ controls ------
- drag & drop Wavefront .obj file: render mesh
- drag & drop Biovision .bhv file: view mocap data
- C : show this help dialogue
- ESC : exit program

> viewing <
- LMB drag : orbit
- RMB drag : shift
- Scroll wheel up/down : zoom in/out
- Tilt wheel left/right : fov increase/decrease
- 0 : reset camera

> rendering <
- Z : toggle wireframe mode
- S : toggle smooth shading

> animation <
- spacebar : play/pause animation
'''
# scroll wheel -> zoom & pov
def scrollCB(window, xoffset, yoffset):
    global gCam
    gCam.zoom -= gCam.zoomsens * yoffset
    gCam.fov += xoffset
    return

# file drop cbfunc
def filedropCB(window, paths):
    global drop_mesh, filepath
    filepath = paths[0]
    if match(r'^.*\.obj$', filepath): 
        drop_mesh = parse_obj(filepath)
        return
    elif match(r'^.*\.bvh$', filepath):
        drop_bvh = parse_bvh(filepath)
        return
    else: print(f'{os.path.basename(filepath)}: unsupported extension')
    return

# keyboard commands
def keyCB(window, key, scancode, action, mods):
    global wireframe, hmode
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.terminate()
            exit(0)
        elif key == glfw.KEY_C: print(controls)



### render ###
def render(window, time:float, camera:Camera, drop=None):
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
    # draw obj / bvh
    glColor3ub(127, 255, 255)
    if type(drop) == Mesh:
        drawMesh(drop)
    elif type(drop) == BVH:
        drawBVH(drop,time)
    return

# draw mesh
def drawMesh(p_mesh:Mesh):
    glVertexPointer(3, GL_FLOAT, 3*p_mesh.vpos.itemsize, p_mesh.vpos)
    glNormalPointer(GL_FLOAT, 12, p_mesh.vnorm)
    indices = np.ravel(p_mesh.ibuff[:, 0:3])
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, indices)

# draw BVH
def drawBVH(p_bvh:BVH, time:float):
    
    return


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
    return


def main():
    # set up globals
    global gCam
    gCam = Camera()
    # set up GLFW
    if not glfw.init():
        print("glfw: failed to init")
        return -1
    window = glfw.create_window(
        int(height * gCam.aspRatio), height, "obj Viewer", None, None)
    if not window:
        glfw.terminate()
        return -1
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_scroll_callback(window, scrollCB)
    glfw.set_drop_callback(window, filedropCB)
    glfw.set_key_callback(window, keyCB)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        gCam.get_input(window)
        gCam.update()
        # render
        render(window, glfw.get_time(),gCam, drop)
        glfw.swap_buffers(window)
    print('goodbye!')
    glfw.terminate()
    return 0


if __name__ == "__main__":
    try: main()
    except SystemExit:
        print('goodbye!')

