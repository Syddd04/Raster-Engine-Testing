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

#Set up machines

w = 1280
h = 720
projector = Projector(w, h, 1, 10) #width, height, near plane, far plane
screen = np.zeros((h,w,3))

x1 = [-0.8, -1.4]
x2 = [0.8, -0.8]
x3 = [0.0, 0.0]

y1 = [-0.6, -0.4]
y2 = [-0.6, -0.6]
y3 = [0.6, 0.6]

z1 = [-2, -2]
z2 = [-2, -2]
z3 = [-2, -2]

col1 = [[1,0,0], [0,0,1]]
col2 = [[0,1,0], [0,1,0]]
col3 = [[0,0,1], [1,0,0]]

for i in range(0,2):

    #Get primitives

    vertex1 = Vertex(x1[i], y1[i], z1[i], col1[i])
    vertex2 = Vertex(x2[i], y2[i], z2[i], col2[i])
    vertex3 = Vertex(x3[i], y3[i], z3[i], col3[i])

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
    for i in range(ss_min.y, ss_max.y):
        for j in range(ss_min.x, ss_max.x):
            x = j + 0.5
            y = i + 0.5

            edge1 = edge(ss_tri.A, ss_tri.B, x, y) / (2 * area) #Similar logic. Divide by 2 to get triangle area and then divide by area to normalize the result. The cross product above gives unnormalized barycentric coordinates. 
            edge2 = edge(ss_tri.B, ss_tri.C, x, y) / (2 * area)
            edge3 = edge(ss_tri.C, ss_tri.A, x, y) / (2 * area)

            '''
            print(edge1)
            print(edge2)
            print(edge3)
            '''
            
            if (edge1 >= 0 and edge2 >= 0 and edge3 >= 0):
                screen[i][j][0] = ss_tri.A.R * edge1 + ss_tri.B.R * edge2 + ss_tri.C.R * edge3
                screen[i][j][1] = ss_tri.A.G * edge1 + ss_tri.B.G * edge2 + ss_tri.C.G * edge3
                screen[i][j][2] = ss_tri.A.B * edge1 + ss_tri.B.B * edge2 + ss_tri.C.B * edge3

plt.imshow(screen)
plt.axis('off')
plt.show()

#Save image
img_unit8 = (screen * 255).astype(np.uint8)
img = Image.fromarray(img_unit8)
img.save('lossless.png', mode='RGB')