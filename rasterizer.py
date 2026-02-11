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

msaa : int = 0
w = 640
h = 480
projector = Projector(w, h, 1, 10) #width, height, near plane, far plane
screen = np.zeros((h,w,3))
coverage = np.zeros((h, w*msaa))

vx1 = [-0.8, -1.4]
vx2 = [0.8, -0.8]
vx3 = [0.0, 0.0]

vy1 = [-0.6, -0.4]
vy2 = [-0.6, -0.6]
vy3 = [0.6, 0.6]

z1 = [-2, -2]
z2 = [-2, -2]
z3 = [-2, -2]

col1 = [[1,0,0], [0,0,1]]
col2 = [[0,1,0], [0,1,0]]
col3 = [[0,0,1], [1,0,0]]

for i in range(0,2):

    #Get primitives

    vertex1 = Vertex(vx1[i], vy1[i], z1[i], col1[i])
    vertex2 = Vertex(vx2[i], vy2[i], z2[i], col2[i])
    vertex3 = Vertex(vx3[i], vy3[i], z3[i], col3[i])

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
            bx = j + 0.5
            by = y + 0.5

            edge1 = edge(ss_tri.A, ss_tri.B, bx, by) / (2 * area) #Similar logic. Divide by 2 to get triangle area and then divide by area to normalize the result. The cross product above gives unnormalized barycentric coordinates. 
            edge2 = edge(ss_tri.B, ss_tri.C, bx, by) / (2 * area)
            edge3 = edge(ss_tri.C, ss_tri.A, bx, by) / (2 * area)

            '''
            print(edge1)
            print(edge2)
            print(edge3)
            '''

            if (msaa == 2):
                x0 = j + 0.25
                x1 = j + 0.75

                y0 = y + 0.25
                y1 = y + 0.75

                e0_1 = edge(ss_tri.A, ss_tri.B, x0, y0)
                e0_2 = edge(ss_tri.B, ss_tri.C, x0, y0)
                e0_3 = edge(ss_tri.C, ss_tri.A, x0, y0)

                e1_1 = edge(ss_tri.A, ss_tri.B, x1, y1)
                e1_2 = edge(ss_tri.B, ss_tri.C, x1, y1)
                e1_3 = edge(ss_tri.C, ss_tri.A, x1, y1)

                if (e0_1 >= 0 and e0_2 >= 0 and e0_3 >= 0):
                    coverage[y][j + 0] = 1
                if (e1_1 >= 0 and e1_2 >= 0 and e1_3 >= 0):
                    coverage[y][j + 1] = 1
            
            if (edge1 >= 0 and edge2 >= 0 and edge3 >= 0):
                if (msaa == 2):
                    screen[y][j][0] = (((ss_tri.A.R * edge1 + ss_tri.B.R * edge2 + ss_tri.C.R * edge3) * coverage[y][j]) + ((ss_tri.A.R * edge1 + ss_tri.B.R * edge2 + ss_tri.C.R * edge3) * coverage[y][j + 1])) / 2
                    screen[y][j][1] = (((ss_tri.A.G * edge1 + ss_tri.B.G * edge2 + ss_tri.C.G * edge3) * coverage[y][j]) + ((ss_tri.A.G * edge1 + ss_tri.B.G * edge2 + ss_tri.C.G * edge3) * coverage[y][j + 1])) / 2
                    screen[y][j][2] = (((ss_tri.A.B * edge1 + ss_tri.B.B * edge2 + ss_tri.C.B * edge3) * coverage[y][j]) + ((ss_tri.A.B * edge1 + ss_tri.B.B * edge2 + ss_tri.C.B * edge3) * coverage[y][j + 1])) / 2
                else:
                    screen[y][j][0] = ss_tri.A.R * edge1 + ss_tri.B.R * edge2 + ss_tri.C.R * edge3
                    screen[y][j][1] = ss_tri.A.G * edge1 + ss_tri.B.G * edge2 + ss_tri.C.G * edge3
                    screen[y][j][2] = ss_tri.A.B * edge1 + ss_tri.B.B * edge2 + ss_tri.C.B * edge3

plt.imshow(screen)
plt.axis('off')
plt.show()

#Save image
'''
img_unit8 = (screen * 255).astype(np.uint8)
img = Image.fromarray(img_unit8)
img.save('lossless.png', mode='RGB')'''