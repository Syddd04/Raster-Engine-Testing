import numpy as np
from graphics_lib import Triangle, Projector, Vertex
import matplotlib.pyplot as plt
from PIL import Image

def getNDC(project, vertex : Vertex):
    near_point = project.toNearPlane(vertex)
    ndc : Vertex = project.toNDC(near_point)
    ndc.z = project.depth(ndc)
    return ndc

def project(project, vert):
    #Convert to NDC
    ndc = getNDC(project, vert)

    #Convert to screen space
    return project.toScreenSpace(ndc)

def edge(a, b, x, y):
    return (b.x - a.x) * (y - a.y) - (b.y - a.y) * (x - a.x)

def validEdge (v0, v1):
    edge_vec = [v1.x - v0.x, v1.y - v0.y]
    top = edge_vec[1] == 0 and edge_vec[0] < 0  
    left = edge_vec[1] < 0                      
    return top or left

#Set up machines

msaa : int = 2
w = 640
h = 480
projector = Projector(w, h, 1, 10) #width, height, near plane, far plane
screen = np.zeros((h,w,3))
z_buffer = np.full((h, w, 2), np.inf)

vx1 = [
    # Front face (z = -3)
    -1, -1,
    # Back face (z = -5)
     1,  1,
    # Left face (x = -1)
    -1, -1,
    # Right face (x = 1)
     1,  1,
    # Top face (y = 1)
    -1,  1,
    # Bottom face (y = -1)
    -1,  1,
]

vx2 = [
    # Front
     1,  1,
    # Back
    -1, -1,
    # Left
    -1, -1,
    # Right
     1,  1,
    # Top
     1, -1,
    # Bottom
     1, -1,
]

vx3 = [
    # Front
     1, -1,
    # Back
    -1,  1,
    # Left
    -1, -1,
    # Right
     1,  1,
    # Top
     1, -1,
    # Bottom
     1, -1,
]

vy1 = [
    # Front
    -1,  1,
    # Back
    -1,  1,
    # Left
    -1,  1,
    # Right
    -1,  1,
    # Top
     1,  1,
    # Bottom
    -1, -1,
]

vy2 = [
    # Front
    -1,  1,
    # Back
    -1,  1,
    # Left
    -1,  1,
    # Right
    -1,  1,
    # Top
     1,  1,
    # Bottom
    -1, -1,
]

vy3 = [
    # Front
     1, -1,
    # Back
     1, -1,
    # Left
     1, -1,
    # Right
     1, -1,
    # Top
     1,  1,
    # Bottom
    -1, -1,
]

vz1 = [
    # Front
    -3, -3,
    # Back
    -5, -5,
    # Left
    -5, -3,
    # Right
    -3, -5,
    # Top
    -3, -3,
    # Bottom
    -5, -5,
]

vz2 = [
    # Front
    -3, -3,
    # Back
    -5, -5,
    # Left
    -3, -5,
    # Right
    -5, -3,
    # Top
    -3, -3,
    # Bottom
    -5, -5,
]

vz3 = [
    # Front
    -3, -3,
    # Back
    -5, -5,
    # Left
    -3, -5,
    # Right
    -5, -3,
    # Top
    -3, -3,
    # Bottom
    -5, -5,
]

col1 = [
    [1,0,0], [1,0,0],     # front – red
    [0,1,0], [0,1,0],     # back – green
    [0,0,1], [0,0,1],     # left – blue
    [1,1,0], [1,1,0],     # right – yellow
    [1,0,1], [1,0,1],     # top – magenta
    [0,1,1], [0,1,1],     # bottom – cyan
]

col2 = col1.copy()
col3 = col1.copy()

for i in range(0,len(vx1)):

    #Get primitives

    vertex1 = Vertex(vx1[i], vy1[i], vz1[i], col1[i])
    vertex2 = Vertex(vx2[i], vy2[i], vz2[i], col2[i])
    vertex3 = Vertex(vx3[i], vy3[i], vz3[i], col3[i])

    triangle = Triangle(vertex1, vertex2, vertex3)

    #Convert to screen space

    ss_v1 = project(projector, triangle.A)
    ss_v2 = project(projector, triangle.B)
    ss_v3 = project(projector, triangle.C) 

    ss_tri = Triangle(ss_v1, ss_v2, ss_v3)

    ss_min = ss_tri.min().floor()
    ss_max = ss_tri.max().ceil()

    #Check winding.
    area = edge(ss_tri.A, ss_tri.B, ss_tri.C.x, ss_tri.C.y) / 2 #Edge equation is cross product, so divide by 2 to get area of triangle instead of parallelogram.
    if area < 0:
        ss_tri.B, ss_tri.C = ss_tri.C, ss_tri.B
        area = -area

    #Do edge testing
    for y in range(ss_min.y, ss_max.y):
        for j in range(ss_min.x, ss_max.x):
            if area == 0:
                continue
            bx = j + 0.5
            by = y + 0.5

            check1 = 0 if validEdge(ss_tri.A, ss_tri.B) else -1e-9 #adjust for subtle fp errors
            check2 = 0 if validEdge(ss_tri.B, ss_tri.C) else -1e-9
            check3 = 0 if validEdge(ss_tri.C, ss_tri.A) else -1e-9

            if (msaa == 2):
                x0 = j + 0.25
                y0 = y + 0.25

                x1 = j + 0.75
                y1 = y + 0.75

                e0_1 = edge(ss_tri.A, ss_tri.B, x0, y0) / (2 * area)
                e0_2 = edge(ss_tri.B, ss_tri.C, x0, y0) / (2 * area)
                e0_3 = edge(ss_tri.C, ss_tri.A, x0, y0) / (2 * area)

                e1_1 = edge(ss_tri.A, ss_tri.B, x1, y1) / (2 * area)
                e1_2 = edge(ss_tri.B, ss_tri.C, x1, y1) / (2 * area)
                e1_3 = edge(ss_tri.C, ss_tri.A, x1, y1) / (2 * area)

                cov0 = 0
                cov1 = 0

                if ((e0_1 + check1 >= 0) and (e0_2 >= 0 + check2) and (e0_3 >= 0 + check3)):
                    cov0 = 1

                if ((e1_1 >= 0 + check1) and (e1_2 >= 0 + check2) and (e1_3 >= 0 + check3)):
                    cov1 = 1

                z0 = (ss_tri.A.z * e0_1 + ss_tri.B.z * e0_2 + ss_tri.C.z * e0_3)
                z1 = (ss_tri.A.z * e1_1 + ss_tri.B.z * e1_2 + ss_tri.C.z * e1_3)

                if ((cov0 or cov1) and (z0 <= z_buffer[y][j][0] or z1 <= z_buffer[y][j][1])):
                    r = 0
                    g = 0
                    b = 0
                    if (z0 <= z_buffer[y][j][0] and cov0):
                        z_buffer[y][j][0] = z0
                        r += ((ss_tri.A.R * e0_1 + ss_tri.B.R * e0_2 + ss_tri.C.R * e0_3) * cov0)
                        g += ((ss_tri.A.G * e0_1 + ss_tri.B.G * e0_2 + ss_tri.C.G * e0_3) * cov0)
                        b += ((ss_tri.A.B * e0_1 + ss_tri.B.B * e0_2 + ss_tri.C.B * e0_3) * cov0)
                    if (z1 <= z_buffer[y][j][1] and cov1):
                        z_buffer[y][j][1] = z1
                        r += ((ss_tri.A.R * e1_1 + ss_tri.B.R * e1_2 + ss_tri.C.R * e1_3) * cov1)
                        g += ((ss_tri.A.G * e1_1 + ss_tri.B.G * e1_2 + ss_tri.C.G * e1_3) * cov1)
                        b += ((ss_tri.A.B * e1_1 + ss_tri.B.B * e1_2 + ss_tri.C.B * e1_3) * cov1)

                    screen[y][j][0] += r / 2
                    screen[y][j][1] += g / 2
                    screen[y][j][2] += b / 2

            else:
                edge1 = edge(ss_tri.A, ss_tri.B, bx, by) / (2 * area) #Similar logic. Divide by 2 to get triangle area and then divide by area to normalize the result. The cross product above gives unnormalized barycentric coordinates. 
                edge2 = edge(ss_tri.B, ss_tri.C, bx, by) / (2 * area)
                edge3 = edge(ss_tri.C, ss_tri.A, bx, by) / (2 * area)

                z = ss_tri.A.z * edge1 + ss_tri.B.z * edge2 + ss_tri.C.z * edge3

                if ((edge1 + check1 >= 0) and (edge2 + check2) >= 0 and (edge3 + check3) >= 0 and z <= z_buffer[y][j][0]):
                    screen[y][j][0] = ss_tri.A.R * edge1 + ss_tri.B.R * edge2 + ss_tri.C.R * edge3
                    screen[y][j][1] = ss_tri.A.G * edge1 + ss_tri.B.G * edge2 + ss_tri.C.G * edge3
                    screen[y][j][2] = ss_tri.A.B * edge1 + ss_tri.B.B * edge2 + ss_tri.C.B * edge3

                    z_buffer[y][j][0] = z

plt.imshow(screen)
plt.axis('off')
plt.show()

#Save image
img_unit8 = (screen * 255).astype(np.uint8)
img = Image.fromarray(img_unit8)
img.save('lossless.png', mode='RGB')